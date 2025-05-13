def clip(value, min_val=0, max_val=255):
    """将值限制在[min_val, max_val]之间"""
    return max(min_val, min(value, max_val))


def compute_cdf(hist):
    """
    根据灰度直方图计算累计分布函数 CDF
    返回列表 cdf[0..255]
    """
    cdf = [0] * 256
    cdf[0] = hist[0]
    for i in range(1, 256):
        cdf[i] = cdf[i - 1] + hist[i]
    return cdf


def bilinear_interpolate(a, b, c, d, wx, wy):
    """
    双线性插值（用于 tile 插值融合）：
    参数：
        a, b, c, d 为四邻域像素值
        wx, wy 分别为水平和垂直方向的权重 (0~1)
    """
    return (
        (1 - wy) * ((1 - wx) * a + wx * b) +
        wy * ((1 - wx) * c + wx * d)
    )