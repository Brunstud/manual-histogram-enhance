# 全局直方图均衡化（纯 Python 实现，无依赖 OpenCV）
def histogram_equalization(y_channel):
    # 统计灰度频率
    hist = [0] * 256
    for row in y_channel:
        for pix in row:
            hist[pix] += 1

    # 构建累计分布函数（CDF）
    cdf = [0] * 256
    cdf[0] = hist[0]
    for i in range(1, 256):
        cdf[i] = cdf[i - 1] + hist[i]

    # 查找 CDF 中最小的非零值
    cdf_min = next(c for c in cdf if c > 0)
    total = cdf[-1]  # 总像素数

    # 构建查找表 LUT（映射到 0-255）
    lut = [round((cdf[i] - cdf_min) / (total - cdf_min) * 255) for i in range(256)]

    # 应用映射表
    result = [[lut[pix] for pix in row] for row in y_channel]
    return result