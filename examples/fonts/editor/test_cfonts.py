from AgonFont import read_font, generate_font_config_code
from ConfigManager import ConfigManager

config_manager = ConfigManager()
font_config = config_manager.get_config_defaults('data/font_psf.cfg')
psf_file_path = '/home/smith/Agon/mystuff/agon-utils/examples/fonts/src/fonts/cfonts/Lat2-VGA16.psf'

font_config, font_image = read_font(psf_file_path, font_config)
font_config_code = generate_font_config_code(font_config)
print(font_config_code)
font_image.show()