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

def ycbcr_merge(y_channel, original_rgb):
    """
    将增强后的 Y 通道与原始 RGB 图像中的 CrCb 通道合并，重建彩色图像
    原理：用增强后的 Y 替换原图中的亮度，再从 YCrCb 转回 RGB
    """
    height = len(y_channel)
    width = len(y_channel[0])
    merged = []

    for i in range(height):
        row = []
        for j in range(width):
            r, g, b = original_rgb[i][j]
            # 原图 RGB → CrCb（近似转换）
            Cr = 128 + 0.5 * r - 0.418688 * g - 0.081312 * b
            Cb = 128 - 0.168736 * r - 0.331264 * g + 0.5 * b
            Y = y_channel[i][j]

            # YCrCb → RGB（反向变换）
            R = Y + 1.402 * (Cr - 128)
            G = Y - 0.344136 * (Cb - 128) - 0.714136 * (Cr - 128)
            B = Y + 1.772 * (Cb - 128)

            row.append([int(max(0, min(255, R))),
                        int(max(0, min(255, G))),
                        int(max(0, min(255, B)))])
        merged.append(row)
    return merged