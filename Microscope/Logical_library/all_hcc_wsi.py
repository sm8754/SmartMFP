
import glob
from PIL import Image


def xunhuan(bingli_path, save_dir, bingli):
    filepath = bingli_path
    img_folders = glob.glob(filepath + "\\IMG*.png")

    MAX_X = -1
    MAX_Y = -1

    for img_path in img_folders:
        filename = img_path.split('\\')[-1]
        x, y = map(int, filename.split('.')[0].split('_')[1:3])
        MAX_X = max(MAX_X, x)
        MAX_Y = max(MAX_Y, y)


    step_20x = [75000, 50000]
    gap_x = step_20x[0]
    gap_y = step_20x[1]
    IMAGE_ROW = MAX_Y // gap_y + 1
    IMAGE_COLUMN = MAX_X // gap_x + 1
    IMAGE_SIZE_X = 900
    IMAGE_SIZE_Y = 600
    to_image = Image.new('RGB', ((IMAGE_COLUMN - 1) * IMAGE_SIZE_X, IMAGE_ROW * IMAGE_SIZE_Y))

    for img_path in img_folders:
        filename = img_path.split('\\')[-1]
        x, y = map(int, filename.split('.')[0].split('_')[1:3])
        i = x // gap_x
        j = y // gap_y

        from_image = Image.open(img_path).resize((IMAGE_SIZE_X, IMAGE_SIZE_Y), Image.ANTIALIAS)
        to_image.paste(from_image, (i * IMAGE_SIZE_X, j * IMAGE_SIZE_Y))

    final_image_path = save_dir + "\\" +"pt.png"
    to_image.save(final_image_path)
    print("Image stitched and saved at", final_image_path)

import os

cervical_slide_path = '\\slides'
save_dir = '\\wholeslideimage'
bingli_name = os.listdir(cervical_slide_path)
for bingli in bingli_name:
    bingli_path = os.path.join(cervical_slide_path, bingli)
    xunhuan(bingli_path, save_dir, bingli)
