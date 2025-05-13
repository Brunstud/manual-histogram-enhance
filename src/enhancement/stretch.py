# 对比度拉伸（线性灰度归一化）
def contrast_stretch(y_channel):
    y_flat = [pix for row in y_channel for pix in row]
    y_min, y_max = min(y_flat), max(y_flat)
    if y_max == y_min:
        return y_channel  # 若亮度无变化，返回原图

    result = [[
        round((pix - y_min) * 255 / (y_max - y_min))
        for pix in row
    ] for row in y_channel]
    return result