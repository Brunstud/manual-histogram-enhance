import os
from utils.file_utils import list_image_files, ensure_dir
from image_io import load_image_rgb, save_image_rgb, rgb_to_ycrcb, y_to_rgb
from histogram import compute_histogram, render_histogram_image
from enhancement import histogram_equalization, clahe_equalization, contrast_stretch, gamma_correction

# 定义增强方法映射表
ENHANCE_METHODS = {
    'equalize': histogram_equalization,
    'clahe': clahe_equalization,
    'stretch': contrast_stretch,
    'gamma': gamma_correction
}

INPUT_DIR = './data/extracted_images'
OUTPUT_DIR = './data/processed_images'
HIST_DIR = os.path.join(OUTPUT_DIR, 'histograms')

ensure_dir(OUTPUT_DIR)
ensure_dir(HIST_DIR)

image_paths = list_image_files(INPUT_DIR)

for path in image_paths:
    name = os.path.splitext(os.path.basename(path))[0]
    pixels = load_image_rgb(path)
    y_channel = rgb_to_ycrcb(pixels)

    for mode, func in ENHANCE_METHODS.items():
        out_dir = os.path.join(OUTPUT_DIR, mode)
        ensure_dir(out_dir)
        hist_dir = os.path.join(HIST_DIR, mode)
        ensure_dir(hist_dir)

        # 增强处理
        if mode == 'gamma':
            y_enhanced = func(y_channel, gamma=1.5)
        else:
            y_enhanced = func(y_channel)

        # 直方图绘制
        hist_ori = compute_histogram(y_channel)
        hist_eq = compute_histogram(y_enhanced)

        hist_img_ori = render_histogram_image(hist_ori)
        hist_img_eq = render_histogram_image(hist_eq)

        # 合并为 RGB 输出图像
        enhanced_rgb = y_to_rgb(y_enhanced)
        save_image_rgb(enhanced_rgb, os.path.join(out_dir, f'{name}.jpg'))

        # 保存直方图对比图像（灰度图合并或分别存）
        hist_combined = [
            hist_img_ori[i] + [0]*10 + hist_img_eq[i]
            for i in range(len(hist_img_ori))
        ]
        hist_rgb = y_to_rgb(hist_combined)
        save_image_rgb(hist_rgb, os.path.join(hist_dir, f'{name}_hist.jpg'))

        print(f'✅ {mode} 增强完成: {name}')