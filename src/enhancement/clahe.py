# 自适应直方图均衡化（CLAHE）手工实现

# 简化版自适应直方图均衡化（CLAHE）：分块增强 + 裁剪限制
def clahe_equalization_0(y_channel, tile_size=8, clip_limit=40):
    import copy
    height = len(y_channel)
    width = len(y_channel[0])
    output = copy.deepcopy(y_channel)

    tile_h = height // tile_size
    tile_w = width // tile_size

    def local_equalize(tile):
        hist = [0] * 256
        for row in tile:
            for p in row:
                hist[p] += 1

        # 裁剪限制：超过 clip_limit 的部分平均分布
        excess = sum(max(0, h - clip_limit) for h in hist)
        for i in range(256):
            if hist[i] > clip_limit:
                hist[i] = clip_limit
        inc = excess // 256
        hist = [h + inc for h in hist]

        # 计算 CDF + LUT
        cdf = [0] * 256
        cdf[0] = hist[0]
        for i in range(1, 256):
            cdf[i] = cdf[i - 1] + hist[i]

        total = tile_size * tile_size
        cdf_min = next(c for c in cdf if c > 0)
        if total == cdf_min:
            lut = list(range(256))
        else:
            lut = [round((cdf[i] - cdf_min) / (total - cdf_min) * 255) for i in range(256)]

        return [[lut[p] for p in row] for row in tile]

    # 遍历所有 tile 区块并增强
    for th in range(tile_size):
        for tw in range(tile_size):
            tile = [
                y_channel[th * tile_h + i][tw * tile_w : tw * tile_w + tile_w]
                for i in range(tile_h)
            ]
            eq_tile = local_equalize(tile)
            for i in range(tile_h):
                output[th * tile_h + i][tw * tile_w : tw * tile_w + tile_w] = eq_tile[i]

    return output


# 采用等大小 tile 分块，对每个块局部直方图增强 + 裁剪限制
def clahe_equalization_1(y_channel, tile_size=8, clip_limit=40):
    """
    CLAHE：分块直方图增强 + 限制对比度
    参数：
        y_channel: 输入图像的 Y 通道（二维列表）
        tile_size: 块划分数量（tile_size x tile_size）
        clip_limit: 每个灰度值最大频数（控制对比度）
    返回：增强后的 Y 通道
    """
    height = len(y_channel)
    width = len(y_channel[0])
    import copy
    output = copy.deepcopy(y_channel)

    block_h = height // tile_size
    block_w = width // tile_size

    def local_equalize(tile):
        """对单个 tile 执行直方图裁剪 + 均衡化"""
        hist = [0] * 256
        for row in tile:
            for p in row:
                hist[p] += 1

        # Clip histogram
        excess = sum(max(0, h - clip_limit) for h in hist)
        for i in range(256):
            if hist[i] > clip_limit:
                hist[i] = clip_limit
        inc = excess // 256
        hist = [h + inc for h in hist]

        # CDF → LUT
        cdf = [0] * 256
        cdf[0] = hist[0]
        for i in range(1, 256):
            cdf[i] = cdf[i - 1] + hist[i]

        total = block_h * block_w
        cdf_min = next((c for c in cdf if c > 0), 0)
        if total == cdf_min:
            lut = list(range(256))
        else:
            lut = [round((cdf[i] - cdf_min) / (total - cdf_min) * 255) for i in range(256)]

        return [[lut[p] for p in row] for row in tile]

    # 遍历 tile 区域，分别增强（不插值，硬拼）
    for by in range(tile_size):
        for bx in range(tile_size):
            tile = [
                y_channel[by * block_h + i][bx * block_w : bx * block_w + block_w]
                for i in range(block_h)
            ]
            enhanced = local_equalize(tile)
            for i in range(block_h):
                output[by * block_h + i][bx * block_w : bx * block_w + block_w] = enhanced[i]

    return output

def clahe_equalization_2(y_channel, tile_size=8, clip_limit=40):
    """
    自适应直方图均衡化 CLAHE：分块局部均衡 + 裁剪限制 + 非整除尺寸处理
    参数：
        y_channel: 输入图像 Y 通道（二维列表）
        tile_size: 块数（tile_size x tile_size 网格）
        clip_limit: 每个 bin 最大频数限制
    返回：增强后的 Y 通道图像
    """
    import copy
    height = len(y_channel)
    width = len(y_channel[0])
    output = copy.deepcopy(y_channel)

    # 动态 tile 尺寸：支持图像无法整除的情况
    def get_tile_bounds(index, tile_count, total_size):
        """
        计算某个 tile 的 [起点, 终点) 坐标
        实现均分并处理边缘多余像素
        """
        base = total_size // tile_count
        extra = total_size % tile_count
        start = index * base + min(index, extra)
        end = start + base + (1 if index < extra else 0)
        return start, end

    def local_equalize(tile):
        """
        对 tile 图像做直方图裁剪 + 均衡化
        返回增强后的 tile（二维数组）
        """
        hist = [0] * 256
        for row in tile:
            for p in row:
                hist[p] += 1

        # 裁剪限制
        excess = sum(max(0, h - clip_limit) for h in hist)
        for i in range(256):
            if hist[i] > clip_limit:
                hist[i] = clip_limit
        inc = excess // 256
        hist = [h + inc for h in hist]

        # CDF + LUT
        cdf = [0] * 256
        cdf[0] = hist[0]
        for i in range(1, 256):
            cdf[i] = cdf[i - 1] + hist[i]
        total = cdf[-1]
        cdf_min = next((c for c in cdf if c > 0), 0)

        if total == cdf_min:
            lut = list(range(256))
        else:
            lut = [round((cdf[i] - cdf_min) / (total - cdf_min) * 255) \
                    for i in range(256)]

        # 应用 LUT
        return [[lut[p] for p in row] for row in tile]

    # 分块并增强（不做插值融合）
    for ty in range(tile_size):
        y0, y1 = get_tile_bounds(ty, tile_size, height)
        for tx in range(tile_size):
            x0, x1 = get_tile_bounds(tx, tile_size, width)

            tile = [row[x0:x1] for row in y_channel[y0:y1]]
            enhanced = local_equalize(tile)

            for i in range(y1 - y0):
                output[y0 + i][x0:x1] = enhanced[i]

    return output

# 使用等大小 tile 分块，对每个块局部直方图增强 + 裁剪限制 + 四邻域插值融合
def clahe_equalization(y_channel, tile_size=8, clip_limit=40):
    """
    CLAHE（自适应直方图均衡化）：支持非整除图像尺寸 + 插值融合
    参数：
        y_channel: 输入图像的 Y 通道（二维列表）
        tile_size: 划分为 tile_size x tile_size 个网格块
        clip_limit: 每个 bin 的频数上限，用于限制局部对比度
    返回：
        output: 增强后的 Y 通道图像（二维列表）
    """
    import math

    height = len(y_channel)
    width = len(y_channel[0])

    # 实际 tile 数量（保证覆盖图像）
    tile_rows = tile_size
    tile_cols = tile_size

    # 每个 tile 的最大宽高（不要求整除）
    block_h = math.ceil(height / tile_rows)
    block_w = math.ceil(width / tile_cols)

    # 初始化所有 tile 的 LUT 表
    LUTS = [[None for _ in range(tile_cols)] for _ in range(tile_rows)]

    # === 1. 对每个 tile 计算 LUT ===
    for ty in range(tile_rows):
        for tx in range(tile_cols):
            # 计算 tile 的真实边界
            y0 = ty * block_h
            y1 = min((ty + 1) * block_h, height)
            x0 = tx * block_w
            x1 = min((tx + 1) * block_w, width)

            tile = [row[x0:x1] for row in y_channel[y0:y1]]

            # 构建直方图
            hist = [0] * 256
            for row in tile:
                for p in row:
                    hist[p] += 1

            # 裁剪并重新分配
            excess = sum(max(0, h - clip_limit) for h in hist)
            for i in range(256):
                if hist[i] > clip_limit:
                    hist[i] = clip_limit
            inc = excess // 256
            hist = [h + inc for h in hist]

            # 构建 CDF → LUT
            cdf = [0] * 256
            cdf[0] = hist[0]
            for i in range(1, 256):
                cdf[i] = cdf[i - 1] + hist[i]
            total = cdf[-1]
            cdf_min = next((c for c in cdf if c > 0), 0)

            if total == cdf_min:
                lut = list(range(256))
            else:
                lut = [round((cdf[i] - cdf_min) / (total - cdf_min) * 255) for i in range(256)]

            LUTS[ty][tx] = lut

    # === 2. 对每个像素执行 4-LUT 插值融合 ===
    output = [[0 for _ in range(width)] for _ in range(height)]

    for y in range(height):
        for x in range(width):
            # 像素所在 tile 的浮点索引位置
            gx = x / block_w
            gy = y / block_h

            tx = int(gx)
            ty = int(gy)
            dx = gx - tx
            dy = gy - ty

            # 限制 tile 索引合法（边缘处理）
            tx0 = min(tx, tile_cols - 1)
            tx1 = min(tx + 1, tile_cols - 1)
            ty0 = min(ty, tile_rows - 1)
            ty1 = min(ty + 1, tile_rows - 1)

            val = y_channel[y][x]

            # 取出四个邻接 tile 的 LUT 值
            p00 = LUTS[ty0][tx0][val]
            p10 = LUTS[ty0][tx1][val]
            p01 = LUTS[ty1][tx0][val]
            p11 = LUTS[ty1][tx1][val]

            # 双线性插值融合
            interp_val = (
                (1 - dx) * (1 - dy) * p00 +
                dx * (1 - dy) * p10 +
                (1 - dx) * dy * p01 +
                dx * dy * p11
            )
            output[y][x] = int(round(interp_val))

    return output
