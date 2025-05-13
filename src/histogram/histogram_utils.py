# 手工绘制灰度直方图为图像（使用纯像素方式构建）
def draw_histogram(y_channel):
    # 初始化频率统计
    hist = [0] * 256
    for row in y_channel:
        for pix in row:
            hist[pix] += 1

    max_val = max(hist)
    height, width = 100, 256
    canvas = [[255] * width for _ in range(height)]  # 初始化全白背景图像

    for x in range(256):
        h = int(hist[x] / max_val * height)
        for y in range(height - h, height):
            canvas[y][x] = 0  # 画黑色柱状
    return canvas