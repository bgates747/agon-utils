#!/usr/bin/env python3
import agonutils as au

if __name__ == '__main__':
    input_video =  "/home/smith/Agon/mystuff/assets/video/staging/a_ha__Take_On_Me.mp4"
    output_video = "/home/smith/Agon/mystuff/assets/video/staging/a_ha__Take_On_Me.agm"
    palette_file = "/home/smith/Agon/mystuff/agz/src/palettes/Agon64.gpl"
    dithering_method = "bayer"
    transparent_color = None  # No transparency

    # Define target output dimensions (match your Agon video format)
    output_width = 512
    output_height = 384

    print(f"Processing video: {input_video}")
    result = au.process_mp4(input_video, output_video, output_width, output_height, palette_file, dithering_method, transparent_color)

    if result == 0:
        print(f"Video successfully processed and saved to: {output_video}")
    else:
        print(f"Video processing failed with error code {result}")
