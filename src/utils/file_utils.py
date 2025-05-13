import os

def list_image_files(folder_path, exts={'.jpg', '.jpeg', '.png'}, max_files=3):
    """
    遍历文件夹并返回所有图像文件路径（可指定最大数量）
    参数:
        folder_path: 根目录
        exts: 允许的扩展名集合
        max_files: 返回的最大文件数（默认不限）
    """
    files = []
    for root, _, filenames in os.walk(folder_path):
        for name in filenames:
            if os.path.splitext(name)[1].lower() in exts:
                files.append(os.path.join(root, name))
                if max_files is not None and len(files) >= max_files:
                    return files
    return files



def ensure_dir(path):
    """确保目录存在，若不存在则创建"""
    os.makedirs(path, exist_ok=True)