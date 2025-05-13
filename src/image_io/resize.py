def resize_image_rgb_nearest(pixels, target_size=(256, 256)):
    """
    使用最近邻插值手工实现图像缩放（适用于 RGB 图像）
    输入：
        pixels: 三维列表，尺寸 H×W×3
        target_size: (新宽度, 新高度)，默认 (256, 256)
    返回：
        resized_pixels: 缩放后的三维列表，维度为 H'×W'×3
    """
    src_h, src_w = len(pixels), len(pixels[0])
    dst_w, dst_h = target_size

    resized = [[[0, 0, 0] for _ in range(dst_w)] for _ in range(dst_h)]

    for y in range(dst_h):
        for x in range(dst_w):
            # 对应原图中最近的坐标
            src_x = round(x * src_w / dst_w)
            src_y = round(y * src_h / dst_h)

            # 保证索引合法
            src_x = min(src_x, src_w - 1)
            src_y = min(src_y, src_h - 1)

            resized[y][x] = pixels[src_y][src_x]

    return resized

def resize_image_rgb_bilinear(pixels, target_size=(256, 256)):
    """
    手工实现双线性插值图像缩放（适用于 RGB 图像）
    输入：pixels 为 H×W×3 列表
    输出：resize 后的 H'×W'×3 图像
    """
    src_h, src_w = len(pixels), len(pixels[0])
    dst_w, dst_h = target_size
    dst_pixels = [[[0, 0, 0] for _ in range(dst_w)] for _ in range(dst_h)]

    for y in range(dst_h):
        for x in range(dst_w):
            gx = x * (src_w - 1) / (dst_w - 1)
            gy = y * (src_h - 1) / (dst_h - 1)

            x0, y0 = int(gx), int(gy)
            x1, y1 = min(x0 + 1, src_w - 1), min(y0 + 1, src_h - 1)
            dx, dy = gx - x0, gy - y0

            for c in range(3):  # RGB 三通道
                a = pixels[y0][x0][c]
                b = pixels[y0][x1][c]
                c_ = pixels[y1][x0][c]
                d = pixels[y1][x1][c]

                val = (1 - dx) * (1 - dy) * a + dx * (1 - dy) * b + \
                      (1 - dx) * dy * c_ + dx * dy * d

                dst_pixels[y][x][c] = int(round(max(0, min(255, val))))

    return dst_pixels

def resize_channel_yuv_nearest(channel, target_size):
    """
    最近邻插值：用于单通道（Y, Cr, Cb）图像
    """
    src_h, src_w = len(channel), len(channel[0])
    dst_h, dst_w = target_size
    resized = [[0 for _ in range(dst_w)] for _ in range(dst_h)]

    for y in range(dst_h):
        for x in range(dst_w):
            src_x = round(x * src_w / dst_w)
            src_y = round(y * src_h / dst_h)
            src_x = min(src_x, src_w - 1)
            src_y = min(src_y, src_h - 1)
            resized[y][x] = channel[src_y][src_x]

    return resized

def resize_channel_yuv_bilinear(channel, target_size):
    """
    双线性插值：用于单通道（Y, Cr, Cb）图像
    """
    src_h, src_w = len(channel), len(channel[0])
    dst_h, dst_w = target_size
    resized = [[0 for _ in range(dst_w)] for _ in range(dst_h)]

    for y in range(dst_h):
        for x in range(dst_w):
            gx = x * (src_w - 1) / (dst_w - 1)
            gy = y * (src_h - 1) / (dst_h - 1)

            x0, y0 = int(gx), int(gy)
            x1, y1 = min(x0 + 1, src_w - 1), min(y0 + 1, src_h - 1)
            dx, dy = gx - x0, gy - y0

            a = channel[y0][x0]
            b = channel[y0][x1]
            c = channel[y1][x0]
            d = channel[y1][x1]

            val = (1 - dx) * (1 - dy) * a + dx * (1 - dy) * b + (1 - dx) * dy * c + dx * dy * d
            resized[y][x] = int(round(max(0, min(255, val))))

    return resized