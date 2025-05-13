# 简化版自适应直方图均衡化（CLAHE）：分块增强 + 裁剪限制

def clahe_equalization(y_channel, tile_size=8, clip_limit=40):
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