import agonutils as au

if __name__ == '__main__':
    palette_file = '/home/smith/Agon/mystuff/agon-utils/examples/palettes/Agon64.gpl'
    src_file = 'examples/matrix/src/images/ctl_panel_navball.png'
    tgt_file = 'examples/matrix/tgt/images/ctl_panel_navball.rgba2'


    au.convert_to_palette(src_file, src_file, palette_file, 'rgb', (0, 0, 0, 0))
    au.img_to_rgba2(src_file, tgt_file, palette_file, 'rgb', (0, 0, 0, 0))
