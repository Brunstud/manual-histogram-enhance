import os

def list_image_files(folder_path, exts={'.jpg', '.jpeg', '.png'}):
    """
    遍历文件夹并返回所有图像文件路径（带扩展名过滤）
    """
    files = []
    for root, _, filenames in os.walk(folder_path):
        for name in filenames:
            if os.path.splitext(name)[1].lower() in exts:
                files.append(os.path.join(root, name))
    return files


def ensure_dir(path):
    """确保目录存在，若不存在则创建"""
    os.makedirs(path, exist_ok=True)