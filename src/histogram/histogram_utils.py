def compute_histogram(y_channel):
    """
    统计灰度图像 Y 通道的直方图
    参数：二维列表 y_channel，值域为 0~255
    返回：长度为 256 的频数列表 hist
    """
    hist = [0] * 256
    for row in y_channel:
        for val in row:
            val_clipped = max(0, min(255, int(val)))  # 修正越界值
            hist[val_clipped] += 1
    return hist


def render_histogram_image(hist, width=256, height=100):
    """
    将直方图渲染为灰度图像（二维数组，黑底白柱）
    每个列对应一个灰度级，柱高按频率归一化映射到图像高度
    参数：
      hist - 长度为256的灰度频数列表
      width - 图像宽度（=256）
      height - 图像高度（直方图可视化图像的高度）
    返回：二维灰度图像列表（高x宽），像素值范围为0~255
    """
    max_count = max(hist)
    scale = height / max_count if max_count > 0 else 1

    img = [[0 for _ in range(width)] for _ in range(height)]

    for x in range(256):
        h = int(hist[x] * scale)
        for y in range(height - 1, height - h - 1, -1):
            img[y][x] = 255  # 绘制柱状图（白色像素）

    return img

def compute_cdf(hist):
    """
    根据直方图频数列表 hist 计算累计分布函数（CDF）
    返回：长度为 256 的 CDF 列表（整数）
    """
    cdf = [0] * 256
    cdf[0] = hist[0]
    for i in range(1, 256):
        cdf[i] = cdf[i - 1] + hist[i]
    return cdf

def render_cdf_image(cdf, width=256, height=100):
    """
    将 CDF 渲染为图像（灰度曲线图）
    使用线段连接前后两点，黑底白线
    """
    total = cdf[-1]
    scale = height / total if total > 0 else 1

    img = [[0 for _ in range(width)] for _ in range(height)]

    prev_y = height - 1  # 初始化上一个点的纵坐标
    for x in range(256):
        y_val = int(height - 1 - cdf[x] * scale)  # 倒着画
        # 连接上一个点（prev_y）到当前 y_val，绘制垂直线段
        for y in range(min(prev_y, y_val), max(prev_y, y_val) + 1):
            if 0 <= y < height:
                img[y][x] = 255
        prev_y = y_val  # 更新前一个点

    return img
