#include "agm.h"

// Helper: Reuse dithering with lookback.
// Processes 'size' pixels.
// oldNo, newNo, oldDither, newDither, and final_out are buffers of length 'size' (packed RGBA2 data).
// unchanged_count is an array of uint16_t (length = size), tracking consecutive unchanged frames.
// lookback is the threshold.
void dither_lookback(
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
void compute_difference(const uint8_t *oldFinal, const uint8_t *newFinal, int size, uint8_t *diff_out) {
    for (int i = 0; i < size; i++) {
        diff_out[i] = (oldFinal[i] == newFinal[i]) ? 0 : newFinal[i];
    }
}

int _process_mp4(const char *input_file, const char *output_file, int output_width, int output_height, const char *palette_file, const char *noDither_method, const char *dither_method, int lookback, bool has_transparent_color, const uint8_t transparent_rgb[3]) {
    AVFormatContext *format_ctx = avformat_alloc_context();
    avformat_open_input(&format_ctx, input_file, NULL, NULL);
    avformat_find_stream_info(format_ctx, NULL);

    unsigned video_stream_index = 0;
    for (unsigned i = 0; i < format_ctx->nb_streams; i++) {
        if (format_ctx->streams[i]->codecpar->codec_type == AVMEDIA_TYPE_VIDEO) {
            video_stream_index = i;
            break;
        }
    }

    AVCodecParameters *codec_params = format_ctx->streams[video_stream_index]->codecpar;
    const AVCodec *codec = avcodec_find_decoder(codec_params->codec_id);
    AVCodecContext *codec_ctx = avcodec_alloc_context3(codec);
    avcodec_parameters_to_context(codec_ctx, codec_params);
    avcodec_open2(codec_ctx, codec, NULL);

    Palette palette;
    _load_gimp_palette(palette_file, &palette);

    struct SwsContext *sws_ctx = sws_getContext(codec_ctx->width, codec_ctx->height, codec_ctx->pix_fmt, output_width, output_height, AV_PIX_FMT_RGBA, SWS_BILINEAR, NULL, NULL, NULL);

    AVFrame *frame = av_frame_alloc();
    AVFrame *rgba_frame = av_frame_alloc();
    int buffer_size = av_image_get_buffer_size(AV_PIX_FMT_RGBA, output_width, output_height, 1);
    uint8_t *buffer = av_malloc(buffer_size);
    av_image_fill_arrays(rgba_frame->data, rgba_frame->linesize, buffer, AV_PIX_FMT_RGBA, output_width, output_height, 1);

    FILE *fp = fopen(output_file, "wb");

    int frame_pixel_count = output_width * output_height;
    uint8_t *oldNo = malloc(frame_pixel_count);
    uint8_t *oldFinal = malloc(frame_pixel_count);
    uint16_t *unchanged_count = calloc(frame_pixel_count, sizeof(uint16_t));
    int first_frame = 1;

    AVPacket packet;
    int frame_index = 0;
    while (av_read_frame(format_ctx, &packet) >= 0) {
        if (packet.stream_index == (int)video_stream_index) {
            avcodec_send_packet(codec_ctx, &packet);
            while (avcodec_receive_frame(codec_ctx, frame) == 0) {
                frame_index++;

                sws_scale(sws_ctx, (const uint8_t * const*)frame->data, frame->linesize, 0, codec_ctx->height, rgba_frame->data, rgba_frame->linesize);

                uint8_t *converted_rgba = malloc(buffer_size);
                memcpy(converted_rgba, rgba_frame->data[0], buffer_size);

                uint8_t *no_rgba = malloc(buffer_size);
                uint8_t *dither_rgba = malloc(buffer_size);
                memcpy(no_rgba, converted_rgba, buffer_size);
                memcpy(dither_rgba, converted_rgba, buffer_size);
                free(converted_rgba);

                _convert_method_rgb(no_rgba, output_width, output_height, &palette, has_transparent_color, transparent_rgb);
                _convert_method_rgb(dither_rgba, output_width, output_height, &palette, has_transparent_color, transparent_rgb);

                uint8_t *newNo = malloc(frame_pixel_count);
                uint8_t *newDither = malloc(frame_pixel_count);
                _rgba32_to_rgba2(no_rgba, frame_pixel_count, newNo);
                _rgba32_to_rgba2(dither_rgba, frame_pixel_count, newDither);
                free(no_rgba);
                free(dither_rgba);

                uint8_t *finalDither = malloc(frame_pixel_count);
                if (first_frame) {
                    memcpy(oldNo, newNo, frame_pixel_count);
                    memcpy(oldFinal, newDither, frame_pixel_count);
                    memcpy(finalDither, newDither, frame_pixel_count);
                    first_frame = 0;
                } else {
                    dither_lookback(oldNo, newNo, oldFinal, newDither, unchanged_count, frame_pixel_count, lookback, finalDither);
                    memcpy(oldNo, newNo, frame_pixel_count);
                    memcpy(oldFinal, finalDither, frame_pixel_count);
                }
                free(newNo);
                free(newDither);

                size_t compressed_size = 0;
                uint8_t *compressed_frame = _rle_encode_internal(finalDither, frame_pixel_count, &compressed_size);
                uint32_t compressed_size_le = (uint32_t)compressed_size;
                fwrite(&compressed_size_le, sizeof(uint32_t), 1, fp);
                fwrite(compressed_frame, sizeof(uint8_t), compressed_size, fp);
                free(compressed_frame);
                free(finalDither);

                fprintf(stderr, "\rFrame %d processed", frame_index);
                fflush(stderr);
            }
        }
        av_packet_unref(&packet);
    }
    fprintf(stderr, "\n");

    fclose(fp);
    av_free(buffer);
    av_frame_free(&frame);
    av_frame_free(&rgba_frame);
    sws_freeContext(sws_ctx);
    avcodec_free_context(&codec_ctx);
    avformat_close_input(&format_ctx);
    free(oldNo);
    free(oldFinal);
    free(unchanged_count);

    return 0;
}
