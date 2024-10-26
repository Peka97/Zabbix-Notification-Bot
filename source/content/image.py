import io

from PIL import Image

from config import CURRENT_CONFIG

config = CURRENT_CONFIG


def check_image(image: bytes, settings: dict):
    img_size = Image.open(io.BytesIO(image)).size
    if img_size < (config.graph_width, config.graph_height):
        raise ValueError(f'"Item ID {settings['itemid']}" not found.')

def save_image(image: bytes, settings: dict) -> str:
    img_name = f"{settings['host']}_{settings['triggerid']}_graph.png"
    img_path = f"{config.IMAGE_CACHE_PATH}/{img_name}"
    
    
    with open(img_path, 'wb') as file:
        file.write(image)
    
    return img_path