from PIL import Image

def load_image_rgb(path):
    """
    使用 Pillow 加载 JPEG 图像，返回 RGB 图像三维列表（H x W x 3）
    """
    with Image.open(path) as img:
        img = img.convert('RGB')
        w, h = img.size
        data = list(img.getdata())
        pixels = [[list(data[y * w + x]) for x in range(w)] for y in range(h)]
        return pixels


def save_image_rgb(pixels, path):
    """
    保存 RGB 图像（3 通道）为 JPEG
    """
    h, w = len(pixels), len(pixels[0])
    flat = [tuple(pixels[y][x]) for y in range(h) for x in range(w)]
    img = Image.new('RGB', (w, h))
    img.putdata(flat)
    img.save(path, format='JPEG')
