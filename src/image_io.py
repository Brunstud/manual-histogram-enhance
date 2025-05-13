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


def rgb_to_ycrcb(pixels):
    """
    将 RGB 像素图像转换为 YCrCb 格式
    返回 Y 通道二维数组，Cr/Cb 可选
    """
    height, width = len(pixels), len(pixels[0])
    Y = [[0 for _ in range(width)] for _ in range(height)]
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[y][x]
            Y[y][x] = round(0.299 * r + 0.587 * g + 0.114 * b)
    return Y


def y_to_rgb(y_channel):
    """
    将灰度图（Y 通道）转为伪 RGB 图像（三通道相同）
    """
    return [[[v, v, v] for v in row] for row in y_channel]