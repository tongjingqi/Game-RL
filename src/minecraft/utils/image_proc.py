from PIL import Image
import math

def thumbnail(image_path):
    img = Image.open(image_path)
    if img.width * img.height <= 640 * 480:
        return    
    scale = math.sqrt(640 * 480 / (img.width * img.height))
    img.thumbnail((int(img.width * scale), int(img.height * scale)))
    img.save(image_path)