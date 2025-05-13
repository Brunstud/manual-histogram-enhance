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

# 使用等大小 tile 分块，对每个块局部直方图增强 + 裁剪限制 + 四邻域插值融合
def clahe_equalization(y_channel, tile_size=8, clip_limit=40):
    """
    CLAHE：带插值的分块直方图增强 + 限制对比度
    参数：
        y_channel: 输入图像的 Y 通道（二维列表）
        tile_size: tile_size x tile_size 块划分数
        clip_limit: 每个 bin 最大频数限制（避免过高对比度）
    返回：增强后的 Y 通道（二维列表）
    """
    height = len(y_channel)
    width = len(y_channel[0])
    block_h = height // tile_size
    block_w = width // tile_size

    # === 1. 预先计算所有 tile 的 LUT ===
    LUTS = [[None for _ in range(tile_size)] for _ in range(tile_size)]

    for ty in range(tile_size):
        for tx in range(tile_size):
            # 提取 tile
            tile = [
                y_channel[ty * block_h + i][tx * block_w : tx * block_w + block_w]
                for i in range(block_h)
            ]

            # 统计直方图并裁剪
            hist = [0] * 256
            for row in tile:
                for p in row:
                    hist[p] += 1

            excess = sum(max(0, h - clip_limit) for h in hist)
            for i in range(256):
                if hist[i] > clip_limit:
                    hist[i] = clip_limit
            inc = excess // 256
            hist = [h + inc for h in hist]

            # 计算 CDF → LUT
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

            LUTS[ty][tx] = lut

    # === 2. 对每个像素执行 4-LUT 插值融合 ===
    output = [[0 for _ in range(width)] for _ in range(height)]

    for y in range(height):
        for x in range(width):
            gx = x / block_w - 0.5
            gy = y / block_h - 0.5
            tx = int(gx)
            ty = int(gy)
            dx = gx - tx
            dy = gy - ty

            # 限制 tile 索引合法（边界处理）
            tx0 = max(0, min(tile_size - 1, tx))
            tx1 = max(0, min(tile_size - 1, tx + 1))
            ty0 = max(0, min(tile_size - 1, ty))
            ty1 = max(0, min(tile_size - 1, ty + 1))

            val = y_channel[y][x]
            # 四邻 LUT 查表并插值加权
            p00 = LUTS[ty0][tx0][val]
            p10 = LUTS[ty0][tx1][val]
            p01 = LUTS[ty1][tx0][val]
            p11 = LUTS[ty1][tx1][val]

            interp_val = (
                (1 - dx) * (1 - dy) * p00 +
                dx * (1 - dy) * p10 +
                (1 - dx) * dy * p01 +
                dx * dy * p11
            )
            output[y][x] = int(round(interp_val))

    return output