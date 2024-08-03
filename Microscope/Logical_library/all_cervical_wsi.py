
import glob
from PIL import Image


def xunhuan(bingli_path, save_dir, bingli):
    filepath = bingli_path
    img_folders = glob.glob(filepath + "\\*.tif")

    MAX_X = -1
    MAX_Y = -1

    for img_path in img_folders:
        filename = img_path.split('\\')[-1]  #
        x, y = map(int, filename.split('.')[0].split('_')[1:3])  #
        MAX_X = max(MAX_X, x)
        MAX_Y = max(MAX_Y, y)

    gap_x = 75000
    gap_y = 50000
    IMAGE_ROW = MAX_Y // gap_y + 1
    IMAGE_COLUMN = MAX_X // gap_x + 1
    IMAGE_SIZE_X = 96
    IMAGE_SIZE_Y = 64

    to_image = Image.new('RGB', ((IMAGE_COLUMN - 1) * IMAGE_SIZE_X, IMAGE_ROW * IMAGE_SIZE_Y))

    for img_path in img_folders:
        filename = img_path.split('\\')[-1]
        x, y = map(int, filename.split('.')[0].split('_')[1:3])
        i = x // gap_x
        j = y // gap_y
        if i == 0:
            continue
        y_position = (IMAGE_ROW - 1 - j) * IMAGE_SIZE_Y
        from_image = Image.open(img_path).resize((IMAGE_SIZE_X, IMAGE_SIZE_Y), Image.LANCZOS)
        to_image.paste(from_image, ((i-1) * IMAGE_SIZE_X, y_position))
    final_image_path = save_dir + "\\pt" +".png"
    to_image.save(final_image_path)
    print("Image stitched and saved at", final_image_path)

import os
cls = 'NILM'
cervical_slide_path = '\\ZJU_slides\\' + cls
save_dir = '\\Microdata\\thumbnail\\' + cls
bingli_name = os.listdir(cervical_slide_path)
for bingli in bingli_name:
    bingli_path = os.path.join(cervical_slide_path, bingli)
    xunhuan(bingli_path, save_dir, bingli)
