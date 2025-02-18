#!/usr/bin/env python3
import sys
import pygame
import agonutils as au

# ----- Metadata for the movie -----
VIDEO_FILE = "/home/smith/Agon/mystuff/assets/video/staging/a_ha__Take_On_Me.agm"  # our custom movie file (raw RGBA2 data)
WIDTH = 512
HEIGHT = 384
FRAME_RATE = 30         # frames per second
SCALING_FACTOR = 1.0    # change to 2.0 to double the displayed size

# ----- Helper functions -----
def load_movie_frames(filename, width, height):
    """
    Load the raw movie file and split it into frames.
    Each frame is assumed to be (width * height) bytes of packed RGBA2 data.
    """
    try:
        with open(filename, "rb") as f:
            data = f.read()
    except IOError as e:
        print(f"Error opening {filename}: {e}")
        sys.exit(1)
    
    frame_size = width * height
    num_frames = len(data) // frame_size
    if num_frames == 0:
        print("No frames found in file!")
        sys.exit(1)
    frames = [data[i*frame_size : (i+1)*frame_size] for i in range(num_frames)]
    return frames

def convert_rgba2_to_rgba32(frame_data, width, height):
    """
    Convert a single frame of RGBA2 data (packed, 1 byte per pixel)
    to 32-bit RGBA (4 bytes per pixel) using agonutils.
    """
    # Call the Python-accessible function from agonutils.
    # It should return a bytes object of length width*height*4.
    rgba32 = au.rgba2_to_rgba32_bytes(frame_data, width, height)
    return rgba32

# ----- Main player function -----
def main():
    # Initialize pygame.
    pygame.init()
    window_width = int(WIDTH * SCALING_FACTOR)
    window_height = int(HEIGHT * SCALING_FACTOR)
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Agonutils Video Player")
    
    # Load the movie frames.
    frames = load_movie_frames(VIDEO_FILE, WIDTH, HEIGHT)
    print(f"Loaded {len(frames)} frames from {VIDEO_FILE}")
    
    clock = pygame.time.Clock()
    running = True
    frame_index = 0

    while running:
        # Process events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Get current frame (raw RGBA2 data).
        raw_frame = frames[frame_index]
        
        # Convert from RGBA2 to full 32-bit RGBA.
        rgba32_bytes = convert_rgba2_to_rgba32(raw_frame, WIDTH, HEIGHT)
        
        # Create a pygame surface from the RGBA32 data.
        # frombuffer creates a Surface that shares the bytes buffer.
        try:
            frame_surface = pygame.image.frombuffer(rgba32_bytes, (WIDTH, HEIGHT), "RGBA")
        except Exception as e:
            print("Error creating surface:", e)
            running = False
            continue
        
        # Scale the surface if needed.
        if SCALING_FACTOR != 1.0:
            frame_surface = pygame.transform.scale(frame_surface, (window_width, window_height))
        
        # Blit the frame and update the display.
        screen.blit(frame_surface, (0, 0))
        pygame.display.flip()
        
        # Wait to match the frame rate.
        clock.tick(FRAME_RATE)
        
        # Next frame.
        frame_index = (frame_index + 1) % len(frames)
    
    pygame.quit()

if __name__ == '__main__':
    main()
