import agonutils as au


if __name__ == '__main__':
    bin_filepath = 'examples/asm/tgt/test.bin'
    width = 256
    height = 256
    image_filepath = 'examples/asm/tgt/test.png'
    au.rgba2_to_img(bin_filepath, image_filepath, width, height)