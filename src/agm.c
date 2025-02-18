#include "agm.h"

// Helper: Reuse dithering with lookback.
// Processes 'size' pixels.
// oldNo, newNo, oldDither, newDither, and final_out are buffers of length 'size' (packed RGBA2 data).
// unchanged_count is an array of uint16_t (length = size), tracking consecutive unchanged frames.
// lookback is the threshold.
void reuse_dithering_with_lookback_internal(
    const uint8_t *oldNo, const uint8_t *newNo,
    const uint8_t *oldDither, const uint8_t *newDither,
    uint16_t *unchanged_count, int size, int lookback,
    uint8_t *final_out)
{
    for (int i = 0; i < size; i++) {
        if (oldNo[i] == newNo[i])
            unchanged_count[i]++;
        else
            unchanged_count[i] = 0;
        // If the pixel changed, or we've seen it unchanged for lookback frames, adopt newDither;
        // otherwise, reuse oldDither.
        if ((oldNo[i] != newNo[i]) || (unchanged_count[i] >= lookback))
            final_out[i] = newDither[i];
        else
            final_out[i] = oldDither[i];
    }
}

// Helper: Compute frame difference.
// For each pixel, diff = 0 if oldFinal == newFinal, else diff = newFinal.
void compute_frame_difference_internal(const uint8_t *oldFinal, const uint8_t *newFinal, int size, uint8_t *diff_out) {
    for (int i = 0; i < size; i++) {
        diff_out[i] = (oldFinal[i] == newFinal[i]) ? 0 : newFinal[i];
    }
}




int _process_mp4_internal(const char *input_file, const char *output_file,
                          int output_width, int output_height,
                          const char *palette_file,
                          const char *noDither_method, const char *dither_method,
                          int lookback, PyObject *transparent_color) {
    AVFormatContext *format_ctx = avformat_alloc_context();
    if (avformat_open_input(&format_ctx, input_file, NULL, NULL) != 0) {
        fprintf(stderr, "Could not open MP4 file: %s\n", input_file);
        return -1;
    }
    
    if (avformat_find_stream_info(format_ctx, NULL) < 0) {
        fprintf(stderr, "Could not retrieve stream info\n");
        avformat_close_input(&format_ctx);
        return -1;
    }

    // Find the video stream index.
    unsigned video_stream_index = 0;
    int found = 0;
    for (unsigned i = 0; i < format_ctx->nb_streams; i++) {
        if (format_ctx->streams[i]->codecpar->codec_type == AVMEDIA_TYPE_VIDEO) {
            video_stream_index = i;
            found = 1;
            break;
        }
    }
    if (!found) {
        fprintf(stderr, "No video stream found\n");
        avformat_close_input(&format_ctx);
        return -1;
    }

    AVCodecParameters *codec_params = format_ctx->streams[video_stream_index]->codecpar;
    const AVCodec *codec = avcodec_find_decoder(codec_params->codec_id);
    AVCodecContext *codec_ctx = avcodec_alloc_context3(codec);
    avcodec_parameters_to_context(codec_ctx, codec_params);
    
    if (avcodec_open2(codec_ctx, codec, NULL) < 0) {
        fprintf(stderr, "Could not open codec\n");
        avcodec_free_context(&codec_ctx);
        avformat_close_input(&format_ctx);
        return -1;
    }

    // Set up conversion to 32-bit RGBA.
    struct SwsContext *sws_ctx = sws_getContext(
        codec_ctx->width, codec_ctx->height, codec_ctx->pix_fmt,
        output_width, output_height, AV_PIX_FMT_RGBA,
        SWS_BILINEAR, NULL, NULL, NULL);

    AVFrame *frame = av_frame_alloc();
    AVFrame *rgba_frame = av_frame_alloc();
    
    int buffer_size = av_image_get_buffer_size(AV_PIX_FMT_RGBA, output_width, output_height, 1);
    uint8_t *buffer = av_malloc(buffer_size);
    av_image_fill_arrays(rgba_frame->data, rgba_frame->linesize, buffer,
                         AV_PIX_FMT_RGBA, output_width, output_height, 1);

    // Open output file.
    FILE *fp = fopen(output_file, "wb");
    if (!fp) {
        fprintf(stderr, "Could not open output file: %s\n", output_file);
        goto cleanup;
    }

    // Persistent buffers for differencing.
    int frame_pixel_count = output_width * output_height;
    uint8_t *oldNo = NULL;     
    uint8_t *oldFinal = NULL;  
    uint16_t *unchanged_count = NULL;
    int first_frame = 1;

    AVPacket packet;
    int frame_index = 0;
    while (av_read_frame(format_ctx, &packet) >= 0) {
        if (packet.stream_index == (int)video_stream_index) {
            if (avcodec_send_packet(codec_ctx, &packet) == 0) {
                while (avcodec_receive_frame(codec_ctx, frame) == 0) {
                    frame_index++;

                    // Convert frame to RGBA.
                    sws_scale(sws_ctx, (const uint8_t * const*)frame->data, frame->linesize, 0,
                              codec_ctx->height, rgba_frame->data, rgba_frame->linesize);

                    // Allocate buffer for current frame.
                    uint8_t *converted_rgba = malloc(buffer_size);
                    if (!converted_rgba) {
                        fprintf(stderr, "Memory allocation failed for converted_rgba\n");
                        continue;
                    }
                    memcpy(converted_rgba, rgba_frame->data[0], buffer_size);

                    // Create two copies for processing.
                    uint8_t *no_rgba = malloc(buffer_size);
                    uint8_t *dither_rgba = malloc(buffer_size);
                    if (!no_rgba || !dither_rgba) {
                        fprintf(stderr, "Memory allocation failed for no/dither copies\n");
                        free(converted_rgba);
                        if (no_rgba) free(no_rgba);
                        if (dither_rgba) free(dither_rgba);
                        continue;
                    }
                    memcpy(no_rgba, converted_rgba, buffer_size);
                    memcpy(dither_rgba, converted_rgba, buffer_size);
                    free(converted_rgba);

                    // Apply palette conversion.
                    if (_convert_to_palette_internal(no_rgba, output_width, output_height,
                                                     palette_file, noDither_method, transparent_color) != 0) {
                        fprintf(stderr, "No-dither palette conversion failed for frame %d.\n", frame_index);
                        free(no_rgba);
                        free(dither_rgba);
                        continue;
                    }
                    if (_convert_to_palette_internal(dither_rgba, output_width, output_height,
                                                     palette_file, dither_method, transparent_color) != 0) {
                        fprintf(stderr, "Dither palette conversion failed for frame %d.\n", frame_index);
                        free(no_rgba);
                        free(dither_rgba);
                        continue;
                    }

                    // Convert both to packed RGBA2.
                    uint8_t *newNo = _rgba32_to_rgba2_internal(no_rgba, output_width, output_height);
                    uint8_t *newDither = _rgba32_to_rgba2_internal(dither_rgba, output_width, output_height);
                    free(no_rgba);
                    free(dither_rgba);
                    if (!newNo || !newDither) {
                        fprintf(stderr, "RGBA2 conversion failed for frame %d.\n", frame_index);
                        if (newNo) free(newNo);
                        if (newDither) free(newDither);
                        continue;
                    }

                    // Allocate buffer for final dithered frame.
                    uint8_t *finalDither = malloc(frame_pixel_count);
                    if (!finalDither) {
                        fprintf(stderr, "Memory allocation failed for finalDither on frame %d.\n", frame_index);
                        free(newNo);
                        free(newDither);
                        continue;
                    }

                    if (first_frame) {
                        oldNo = malloc(frame_pixel_count);
                        oldFinal = malloc(frame_pixel_count);
                        unchanged_count = calloc(frame_pixel_count, sizeof(uint16_t));
                        if (!oldNo || !oldFinal || !unchanged_count) {
                            fprintf(stderr, "Memory allocation failed for persistent buffers.\n");
                            free(newNo);
                            free(newDither);
                            free(finalDither);
                            goto cleanup;
                        }
                        memcpy(oldNo, newNo, frame_pixel_count);
                        memcpy(oldFinal, newDither, frame_pixel_count);
                        memcpy(finalDither, newDither, frame_pixel_count);
                        first_frame = 0;
                    } else {
                        reuse_dithering_with_lookback_internal(oldNo, newNo, oldFinal, newDither,
                                                                unchanged_count, frame_pixel_count, lookback,
                                                                finalDither);
                        memcpy(oldNo, newNo, frame_pixel_count);
                        memcpy(oldFinal, finalDither, frame_pixel_count);
                    }

                    free(newNo);
                    free(newDither);

                    // Apply RLE compression.
                    size_t compressed_size = 0;
                    uint8_t *compressed_frame = _rle_encode_internal(finalDither, frame_pixel_count, &compressed_size);
                    if (!compressed_frame) {
                        fprintf(stderr, "RLE compression failed for frame %d.\n", frame_index);
                        free(finalDither);
                        continue;
                    }
                    // --- Write the 4-byte frame header ---
                    uint32_t compressed_size_le = (uint32_t)compressed_size;
                    fwrite(&compressed_size_le, sizeof(uint32_t), 1, fp);

                    // Write the compressed frame data
                    fwrite(compressed_frame, sizeof(uint8_t), compressed_size, fp);

                    free(compressed_frame);
                    free(finalDither);

                    // Update progress on a single line.
                    fprintf(stderr, "\rFrame %d processed", frame_index);
                    fflush(stderr);
                }
            }
        }
        av_packet_unref(&packet);
    }
    fprintf(stderr, "\n");

cleanup:
    if (fp) fclose(fp);
    if (buffer) av_free(buffer);
    if (frame) av_frame_free(&frame);
    if (rgba_frame) av_frame_free(&rgba_frame);
    if (sws_ctx) sws_freeContext(sws_ctx);
    if (codec_ctx) avcodec_free_context(&codec_ctx);
    if (format_ctx) avformat_close_input(&format_ctx);
    if (oldNo) free(oldNo);
    if (oldFinal) free(oldFinal);
    if (unchanged_count) free(unchanged_count);

    return 0;
}
