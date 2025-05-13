import os
from PIL import Image

def analyze_image_sizes(folder_by_class):
    """
    遍历每类文件夹中的图像，统计最大尺寸、最小尺寸、平均面积（像素总数）
    参数：folder_by_class 是一个 {class_id: folder_path} 的字典
    """
    results = {}
    global_total = 0
    global_area_sum = 0
    global_max = (0, 0)
    global_min = (1 << 30, 1 << 30)

    for class_id, folder in folder_by_class.items():
        max_size = (0, 0)
        min_size = (1 << 30, 1 << 30)
        total_area = 0
        count = 0

        for fname in os.listdir(folder):
            if not fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
            try:
                with Image.open(os.path.join(folder, fname)) as img:
                    w, h = img.size
                    area = w * h
                    max_size = max(max_size, (w, h), key=lambda x: x[0] * x[1])
                    min_size = min(min_size, (w, h), key=lambda x: x[0] * x[1])
                    total_area += area
                    count += 1
            except Exception as e:
                print(f"⚠️ 跳过损坏图像: {fname}, 错误: {e}")

        if count > 0:
            avg_area = total_area / count
            avg_side = int(avg_area ** 0.5)
            results[class_id] = {
                'count': count,
                'max_size': max_size,
                'min_size': min_size,
                'avg_area': avg_area,
                'avg_side': avg_side
            }
            global_total += count
            global_area_sum += total_area
            global_max = max(global_max, max_size, key=lambda x: x[0] * x[1])
            global_min = min(global_min, min_size, key=lambda x: x[0] * x[1])

    global_avg_area = global_area_sum / global_total if global_total else 0
    global_avg_side = int(global_avg_area ** 0.5)

    return results, {
        'total': global_total,
        'max_size': global_max,
        'min_size': global_min,
        'avg_area': global_avg_area,
        'avg_side': global_avg_side
    }


if __name__ == '__main__':
    # 示例调用
    base = './extracted_images'
    synsets = ['n02123045', 'n02352591', 'n04465501']
    folder_map = {s: os.path.join(base, s) for s in synsets}

    results, global_summary = analyze_image_sizes(folder_map)

    print("\n📊 每类图像统计：")
    for k, v in results.items():
        print(f"类别 {k}: 共 {v['count']} 张, 平均尺寸约 {v['avg_side']}×{v['avg_side']}, 最大: {v['max_size']}, 最小: {v['min_size']}")

    print("\n📈 全体图像汇总：")
    print(f"图像总数: {global_summary['total']}")
    print(f"最大尺寸: {global_summary['max_size']}, 最小尺寸: {global_summary['min_size']}")
    print(f"平均面积: {global_summary['avg_area']:.1f}，等效尺寸约: {global_summary['avg_side']}×{global_summary['avg_side']}")

    print("\n✅ 推荐统一 resize 尺寸：建议设置为 {}×{}，以最大覆盖图像细节且兼顾效率".format(
        min(global_summary['avg_side'], 512),
        min(global_summary['avg_side'], 512)
    ))
