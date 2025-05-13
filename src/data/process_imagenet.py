import os
from PIL import Image
import cv2
import numpy as np
from tqdm import tqdm

# 设置路径与参数
EXTRACT_DIR = './extracted_images'      # 解压后的原始图像
OUTPUT_DIR = './processed_images-ref'       # 增强并统一尺寸后的图像
HIST_DIR = os.path.join(OUTPUT_DIR, 'histograms')  # 直方图保存路径
TARGET_SIZE = (256, 256)                # 图像标准化尺寸
ENHANCE_MODE = ['equalize', 'clahe', 'stretch', 'gamma']

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(HIST_DIR, exist_ok=True)


# Step 2: 多种图像增强方法实现
def enhance_histogram(img_np, mode):
    # 转换为 YCrCb 颜色空间，提取亮度通道 Y
    ycrcb = cv2.cvtColor(img_np, cv2.COLOR_RGB2YCrCb)
    y = ycrcb[:, :, 0]
    y_ori = y.copy()

    if mode == 'equalize':
        # 方式 1：全局直方图均衡化（最常用）
        y_eq = cv2.equalizeHist(y)

    elif mode == 'clahe':
        # 方式 2：自适应直方图均衡化（局部增强 + 限制对比度）
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        y_eq = clahe.apply(y)

    elif mode == 'stretch':
        # 方式 3：线性对比度拉伸，将 y 范围归一化到 [0, 255]
        y_min, y_max = np.min(y), np.max(y)
        if y_max - y_min < 1:
            # 避免除以接近零造成黑图
            y_eq = y.copy()
            print(f"⚠️ Stretch skipped due to narrow dynamic range: min={y_min}, max={y_max}")
        else:
            # 使用 float 精度进行拉伸，再转回 uint8
            y_eq = ((y.astype(np.float32) - y_min) * 255.0 / (y_max - y_min)).clip(0, 255).astype(np.uint8)

    elif mode == 'gamma':
        # 方式 4：Gamma 校正（提升暗部细节）
        gamma = 1.5  # 可调整为 <1（提亮）或 >1（压暗）
        y_norm = y / 255.0
        y_eq = np.power(y_norm, gamma) * 255
        y_eq = np.clip(y_eq, 0, 255).astype(np.uint8)

    else:
        raise ValueError(f"未知增强模式：{ENHANCE_MODE}")

    # 将增强后的 Y 通道与原 CrCb 合并，转回 RGB
    ycrcb[:, :, 0] = y_eq
    enhanced = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2RGB)
    return enhanced, y_ori, y_eq

def draw_histogram_comparison(original_y, enhanced_y, out_path, title):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)

    # 左图：增强前
    axes[0].hist(original_y.ravel(), bins=256, range=[0, 256], color='blue', alpha=0.7)
    axes[0].set_title('Before Enhancement')
    axes[0].set_xlabel('Pixel Intensity')
    axes[0].set_ylabel('Frequency')

    # 右图：增强后
    axes[1].hist(enhanced_y.ravel(), bins=256, range=[0, 256], color='red', alpha=0.7)
    axes[1].set_title('After Enhancement')
    axes[1].set_xlabel('Pixel Intensity')

    fig.suptitle(f'Y Channel Histogram Comparison: {title}', fontsize=12)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(out_path)
    plt.close()

# Step 3: 遍历图像并处理
for synset in tqdm(os.listdir(EXTRACT_DIR), desc='Processing synsets'):
    synset_path = os.path.join(EXTRACT_DIR, synset)
    output_synset_path = os.path.join(OUTPUT_DIR, synset)
    os.makedirs(output_synset_path, exist_ok=True)

    for img_file in os.listdir(synset_path):
        if not img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
        img_path = os.path.join(synset_path, img_file)
        try:
            with Image.open(img_path) as img:
                img = img.convert('RGB')
                img = img.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
                img_np = np.array(img)

                for mode in ENHANCE_MODE:
                    # enhance the image
                    img_enhanced, y_before, y_after = enhance_histogram(img_np, mode)

                    # Path: the enhanced image
                    mode_output_path = os.path.join(output_synset_path, mode)
                    os.makedirs(mode_output_path, exist_ok=True)
                    img_path = os.path.join(mode_output_path, img_file)
                    
                    # Path: the histogram comparison
                    hist_output_path = os.path.join(HIST_DIR, mode)
                    os.makedirs(hist_output_path, exist_ok=True)
                    hist_path = os.path.join(hist_output_path, f"{os.path.splitext(img_file)[0]}_hist.png")

                    # Skip
                    if os.path.exists(img_path) and os.path.exists(hist_path):
                        print(f"⚠️ 跳过已存在的图像: {img_path} 和直方图: {hist_path}")
                        continue

                    # Save the enhanced image and histogram
                    Image.fromarray(img_enhanced).save(img_path, 'JPEG')
                    draw_histogram_comparison(y_before, y_after, hist_path, f"{synset}/{img_file} [{mode}]")

                    print(f"✅ {mode.upper()}增强完成: {img_path}")

        except Exception as e:
            print(f"❌ 跳过损坏图像: {img_path}, 错误: {e}")
