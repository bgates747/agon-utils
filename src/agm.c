#include "agm.h"

int _process_mp4_internal(const char *input_file, const char *output_file, int output_width, int output_height, 
                          const char *palette_file, const char *method, PyObject *transparent_color) {
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
    AVCodec *codec = avcodec_find_decoder(codec_params->codec_id);
    AVCodecContext *codec_ctx = avcodec_alloc_context3(codec);
    avcodec_parameters_to_context(codec_ctx, codec_params);
    
    if (avcodec_open2(codec_ctx, codec, NULL) < 0) {
        fprintf(stderr, "Could not open codec\n");
        avcodec_free_context(&codec_ctx);
        avformat_close_input(&format_ctx);
        return -1;
    }

    // Determine total frame count (approximate using duration and framerate)
    int64_t duration = format_ctx->duration;  // Duration in AV_TIME_BASE units
    double fps = av_q2d(format_ctx->streams[video_stream_index]->avg_frame_rate);
    int total_frames = (int)((duration / (double)AV_TIME_BASE) * fps);
    if (total_frames <= 0) {
        fprintf(stderr, "Warning: Could not determine total frames, defaulting to unknown progress.\n");
    }

    // Set up conversion to 32-bit RGBA with the desired output dimensions.
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

    // Open the output file for writing (for the custom movie format).
    FILE *fp = fopen(output_file, "wb");
    if (!fp) {
        fprintf(stderr, "Could not open output file: %s\n", output_file);
        av_free(buffer);
        av_frame_free(&frame);
        av_frame_free(&rgba_frame);
        sws_freeContext(sws_ctx);
        avcodec_free_context(&codec_ctx);
        avformat_close_input(&format_ctx);
        return -1;
    }

    // Process frames
    AVPacket packet;
    int frame_count = 0;
    while (av_read_frame(format_ctx, &packet) >= 0) {
        if (packet.stream_index == (int)video_stream_index) {
            if (avcodec_send_packet(codec_ctx, &packet) == 0) {
                while (avcodec_receive_frame(codec_ctx, frame) == 0) {
                    frame_count++;

                    // Convert the decoded frame to RGBA.
                    sws_scale(sws_ctx, (const uint8_t * const*)frame->data, frame->linesize, 0,
                              codec_ctx->height, rgba_frame->data, rgba_frame->linesize);

                    // Allocate a new buffer for the converted RGBA frame.
                    uint8_t *converted_rgba = malloc(buffer_size);
                    if (!converted_rgba) {
                        fprintf(stderr, "Memory allocation failed for converted_rgba\n");
                        continue;
                    }
                    memcpy(converted_rgba, rgba_frame->data[0], buffer_size);

                    // Apply the palette conversion using the internal function.
                    if (_convert_to_palette_internal(converted_rgba, output_width, output_height,
                                                     palette_file, method, transparent_color) != 0) {
                        fprintf(stderr, "Palette conversion failed for frame %d.\n", frame_count);
                        free(converted_rgba);
                        continue;
                    }

                    // Convert the processed RGBA data to RGBA2 format using the internal helper.
                    uint8_t *rgba2_data = _rgba32_to_rgba2_internal(converted_rgba, output_width, output_height);
                    if (!rgba2_data) {
                        fprintf(stderr, "RGBA2 conversion failed for frame %d.\n", frame_count);
                        free(converted_rgba);
                        continue;
                    }

                    // Write the RGBA2 data for this frame to the output file.
                    fwrite(rgba2_data, sizeof(uint8_t), (size_t)output_width * output_height, fp);

                    free(converted_rgba);
                    free(rgba2_data);

                    // Update progress
                    if (total_frames > 0) {
                        double progress = (frame_count / (double)total_frames) * 100.0;
                        fprintf(stderr, "\rFrame %d of %d processed (%.2f%%)   ", frame_count, total_frames, progress);
                    } else {
                        fprintf(stderr, "\rFrame %d processed (progress unknown)   ", frame_count);
                    }
                    fflush(stderr);
                }
            }
        }
        av_packet_unref(&packet);
    }
    
    // Print newline for clean output after progress tracking
    fprintf(stderr, "\n");

    fclose(fp);
    av_free(buffer);
    av_frame_free(&frame);
    av_frame_free(&rgba_frame);
    sws_freeContext(sws_ctx);
    avcodec_free_context(&codec_ctx);
    avformat_close_input(&format_ctx);

    return 0;
}
