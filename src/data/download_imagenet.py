import os
import requests

import tarfile

# synset IDs
synsets = ['n02352591', 'n02123045', 'n04465501']

INPUT_TAR_DIR = './imagenet_data'       # 存放 .tar 文件的文件夹
EXTRACT_DIR = './extracted_images'      # 解压后的原始图像
os.makedirs(EXTRACT_DIR, exist_ok=True)

for sid in synsets:
    url = f'https://image-net.org/data/winter21_whole/{sid}.tar'
    local_path = os.path.join(INPUT_TAR_DIR, f'{sid}.tar')
    print(f'Downloading {url} ...')
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
    else:
        print(f'Failed to download {sid}')

# Step 1: 解压所有 .tar 文件
for tarname in os.listdir(INPUT_TAR_DIR):
    if tarname.endswith('.tar'):
        synset_id = tarname.replace('.tar', '')
        extract_path = os.path.join(EXTRACT_DIR, synset_id)
        os.makedirs(extract_path, exist_ok=True)
        with tarfile.open(os.path.join(INPUT_TAR_DIR, tarname), 'r') as tar:
            tar.extractall(path=extract_path)
        print(f'✅ 解压完成: {tarname}')