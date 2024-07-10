
import openslide
import json
import os
import cv2
import numpy as np
import random
import math
import glob
import matplotlib.pyplot as plt
import copy
import xml.etree.ElementTree as ET
import json


def check_data_distribution(json_paths):

    # record the number of different kinds of poses (i.e. bboxes)
    pos_num_dict = {}

    for c in CLASS_NAMES:
        small_pos_num = 0
        medium_pos_num = 0
        large_pos_num = 0

        for p in json_paths:

            # load train json file to gain labels
            with open(p, 'r') as f:
                train_dicts = json.load(f)

            for train_dict in train_dicts:
                if train_dict['class'] == c:
                    w = train_dict['w']
                    h = train_dict['h']
                    area = w * h

                    # accumulate the number of different sizes of poses
                    if area < 32**2:
                        small_pos_num += 1
                    elif area > 96**2:
                        large_pos_num += 1
                    else:
                        medium_pos_num += 1

        pos_num_dict[c] = [small_pos_num, medium_pos_num, large_pos_num]
        print('Class-%s: small: %d, medium: %d, large: %d' % (c, small_pos_num, medium_pos_num, large_pos_num))

def iou_filter(new_roi_label, all_bbox_labels, iou_thred=0.5):

    # new patch coordinate information
    roi_xmin = new_roi_label['x']
    roi_ymin = new_roi_label['y']
    roi_w = new_roi_label['w']
    roi_h = new_roi_label['h']

    new_bbox_labels = []

    for bbox_label in all_bbox_labels:
        if bbox_label['class'] != 'roi':
            # bbox coordinate information
            bbox_xmin = bbox_label['x']
            bbox_ymin = bbox_label['y']
            bbox_w = bbox_label['w']
            bbox_h = bbox_label['h']

            # get intersection:
            if bbox_w * bbox_h < IMG_SIZE**2 and bbox_w < IMG_SIZE and bbox_h < IMG_SIZE:
                x1 = max(bbox_xmin, roi_xmin)
                y1 = max(bbox_ymin, roi_ymin)
                x2 = min(bbox_xmin + bbox_w - 1, roi_xmin + roi_w - 1)
                y2 = min(bbox_ymin + bbox_h -1, roi_ymin + roi_h - 1)

                w = np.maximum(0, x2 - x1 + 1)    # the width of overlap
                h = np.maximum(0, y2 - y1 + 1)    # the height of overlap

                iou_area = w * h
                bbox_area = bbox_w * bbox_h

                if (iou_area / bbox_area) > iou_thred:
                    new_bbox_labels.append({'x':x1-roi_xmin, 'y':y1-roi_ymin, 'w':x2-x1+1, 'h':y2-y1+1, 'class':bbox_label['class']})
            else:
                pass

    return new_bbox_labels

def produce_patch_for_large_bbox(large_bbox_labels, CLASS_NAMES, img_name, stride_proportion, img_size, read_tool, save_dir):

    stride = img_size * stride_proportion

    fully_positive_patch_nums = 0
    for large_bbox_label in large_bbox_labels:
        # get the horizontal/vertical moving step (i.e., sliding step)
        hor_move_step = int((large_bbox_label['w'] - img_size)/stride + 1)
        ver_move_step = int((large_bbox_label['h'] - img_size)/stride + 1)

        if hor_move_step < 1:
            hor_move_step = 1
        if ver_move_step < 1:
            ver_move_step = 1

        # get the start sliding coordinate information
        x_start = int(large_bbox_label['x'])
        y_start = int(large_bbox_label['y'])
        width = int(copy.deepcopy(img_size))
        height = int(copy.deepcopy(img_size))

        # two forloops for horizontal and vertical moving the windows
        for ver in range(ver_move_step):
            for hor in range(hor_move_step):
                x_new = int(x_start + ver * stride)
                y_new = int(y_start + hor * stride)

                img = np.array(slide.read_region((x_new, y_new), level,
                                                 (width, height)))[:, :, :3]
                img_arr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

                if large_bbox_label['w'] > width and large_bbox_label['h'] < height:

                    w_correct = width
                    h_correct = large_bbox_label['h']
                elif large_bbox_label['w'] < width and large_bbox_label['h'] > height:
                    w_correct = large_bbox_label['w']
                    h_correct = height
                else:
                    w_correct = width
                    h_correct = height
                img_label = [{'x':0, 'y':0, 'w':w_correct, 'h':h_correct, 'class':large_bbox_label['class']}]
                fully_positive_patch_nums += 1
                if not os.path.exists(save_dir + 'train\\' + CLASS_NAMES + '\\' + img_name + '\\'):
                    os.makedirs(save_dir + 'train\\' + CLASS_NAMES + '\\' + img_name + '\\')
                cv2.imwrite(save_dir + 'train\\' + CLASS_NAMES + '\\' + img_name + '\\' + img_name + '_{}_large.png'.format(fully_positive_patch_nums), img_arr)
                with open(save_dir + 'label\\' + CLASS_NAMES + '\\' + img_name + '\\' + img_name + '_{}_large.json'.format(fully_positive_patch_nums), 'w') as json_f:
                    json.dump(img_label, json_f)
        return fully_positive_patch_nums

def xml_process(tree, pos_path ,pos_file, CLASS_NAMES):
    root = tree.getroot()
    annotations = []

    class_name = CLASS_NAMES
    for region in root.findall(".//Region"):
        vertices = region.findall('Vertices/Vertex[@Z="0"]')
        x1, y1 = float(vertices[0].get('X')), float(vertices[0].get('Y'))
        x2, y2 = float(vertices[2].get('X')), float(vertices[2].get('Y'))
        width = x2 - x1
        height = y2 - y1

        annotation = {
            "x": x1,
            "y": y1,
            "w": width,
            "h": height,
            "class": class_name
        }
        annotations.append(annotation)

    with open(pos_path + '\\' + pos_file + '.json', 'w') as json_file:
        json.dump(annotations, json_file, indent=4)

TRIAN_PATH = '\\TCT\\dierpi'
SAVE_DIR = '\\dataset\\'
CLASS_NAMES = ["ASC-US", "HSIL", "LSIL"]

for m in range(len(CLASS_NAMES)):
    pos_path = os.path.join(TRIAN_PATH, CLASS_NAMES[m])
    pos_files = os.listdir(pos_path)

    for pos_file in pos_files:

        if pos_file.split('.')[1] == 'xml':
            tree = ET.parse(os.path.join(pos_path, pos_file))
            xml_process(tree, pos_path, pos_file.split('.')[0], CLASS_NAMES[m])
IMG_SIZE = 512
STRIDE_PROPORTION = 0.25
for mm in range(len(CLASS_NAMES)):
    posjson_path = os.path.join(TRIAN_PATH, CLASS_NAMES[mm])
    json_paths = glob.glob(posjson_path + '/*.json')
    all_normal_patch_nums = 0
    all_fully_positive_patch_nums = 0
    for p in json_paths:

        with open(p, 'r') as f:
            train_dicts = json.load(f)

        img_name = p.split('\\')[-1].split('.')[0]
        kfb_path = os.path.join(posjson_path, img_name + '.svs')

        slide = openslide.OpenSlide(kfb_path)
        level = 0
        down_factor = slide.level_downsamples[level]

        large_bbox_labels = []
        nums = 0
        for train_dict in train_dicts:
            if train_dict['class'] != 'roi':
                w = int(train_dict['w'])
                h = int(train_dict['h'])
                x_min = int(train_dict['x'])
                y_min = int(train_dict['y'])
                x_max = x_min + w - 1
                y_max = y_min + h - 1
                x_center = int(x_min + int(w/2) -1)
                y_center = int(y_min + int(h/2) -1)

                if w * h < IMG_SIZE**2 and w < IMG_SIZE and h < IMG_SIZE:
                    offset_dist= int((IMG_SIZE - max(w, h))/2)

                    rand_x_offset = np.random.randint(-offset_dist, offset_dist)
                    rand_y_offset = np.random.randint(-offset_dist, offset_dist)

                    patch_label = {'x':x_center + rand_x_offset - IMG_SIZE//2,
                                   'y':y_center + rand_y_offset - IMG_SIZE//2,
                                    'w':IMG_SIZE, 'h':IMG_SIZE}

                    new_bbox_labels = iou_filter(patch_label, train_dicts, 0.5)
                    nums += 1

                    if not os.path.exists(SAVE_DIR):
                        os.makedirs(SAVE_DIR)
                        os.makedirs(SAVE_DIR + '\\train\\')
                        os.makedirs(SAVE_DIR + '\\label\\')
                    if not os.path.exists(SAVE_DIR + 'train\\' + CLASS_NAMES[mm] + '\\' + img_name + '\\'):
                        os.makedirs(SAVE_DIR + 'train\\' + CLASS_NAMES[mm] + '\\' + img_name + '\\')
                    if not os.path.exists(SAVE_DIR + 'label\\' + CLASS_NAMES[mm] + '\\' + img_name + '\\'):
                        os.makedirs(SAVE_DIR + 'label\\' + CLASS_NAMES[mm] + '\\' + img_name + '\\')
                    # img = read.ReadRoi(patch_label['x'], patch_label['y'], patch_label['w'], patch_label['h'], 20)
                    img = np.array(slide.read_region((patch_label['x'], patch_label['y']), level, (patch_label['w'], patch_label['h'])))[:, :, :3]
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    cv2.imwrite(SAVE_DIR + 'train\\' + CLASS_NAMES[mm] + '\\' + img_name + '\\' + img_name + '_{}.png'.format(nums), img)
                    with open(SAVE_DIR + 'label\\' + CLASS_NAMES[mm] + '\\' + img_name + '\\' + img_name + '_{}.json'.format(nums), 'w') as json_f:
                        json.dump(new_bbox_labels, json_f)
                else:
                    large_bbox_labels.append(train_dict)

        if large_bbox_labels != []:
            fully_positive_patch_nums = produce_patch_for_large_bbox(large_bbox_labels, CLASS_NAMES[mm], img_name, STRIDE_PROPORTION, IMG_SIZE, slide, SAVE_DIR)
        else:
            fully_positive_patch_nums = 0

        all_normal_patch_nums += nums
        all_fully_positive_patch_nums += fully_positive_patch_nums
        print('Image-%s produces %d normal patch images and %d fully-positive patch image.' % (img_name, nums, fully_positive_patch_nums))

    print('\nall normal image numbers: %d, all fully positive image numbers: %d' % (all_normal_patch_nums, all_fully_positive_patch_nums))
    print('All patch images were saved to %s.' % SAVE_DIR)

# # visualize specific class image to check if the data generation is right
# fig = plt.figure(figsize=(16,16))
# p = '\Annotations\T2019_306_12.json'
# pp = '\JPEGImages\T2019_306_12.png'
#
# with open(p, 'r') as f:
#     train_dicts = json.load(f)
# img = cv2.imread(pp)
# img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
#
# for l in train_dicts:
#     x = int(l['x'])
#     y = int(l['y'])
#     w = int(l['w'])
#     h = int(l['h'])
#     # x = int((0.22 - 0.08/2)*1536)
#     # y = int((0.27 - 0.13/2)*1536)
#     # w = int(0.08 * 1536)
#     # h = int(0.13 * 1536)
#
#
#     img = cv2.rectangle(img,(x,y),(x+w-1,y+h-1),(0,255,0),2)
# # print(l['class'])
#
# plt.imshow(img)
# plt.show()


# # compute the generated data distribution
# import glob
# json_paths = glob.glob('train/label/*.json')
# check_data_distribution(json_paths)
#
#
# # visualize the generated samples with different classes
# import glob
# import cv2
# import json
# json_total_path = '\\dataset\\label'
# # json_paths = glob.glob('\\HSIL\\01S079\\*.json')
# train_path = '\\dataset\\train'
# display_image_set = [] # store the samples
#
# CLASS_NAMES = ["ASC-US", "HSIL", "LSIL"]
# for c in CLASS_NAMES:
#     for d in os.listdir(json_total_path + '\\' + c):
#
#         # break_flag = 0
#         json_paths = glob.glob(json_total_path+ '\\' + c + '\\' + d + '\\*.json')
#         for json_path in json_paths:
#             # obtain image name
#             img_name = json_path.split('\\')[-1][:-5]
#             img_folder_name = img_name.split('_')[0]
#             with open(json_path, 'r') as f:
#                 labels = json.load(f)
#
#             for label in labels:
#                 if label['class'] == c:
#                     x = int(label['x'])
#                     y = int(label['y'])
#                     w = int(label['w'])
#                     h = int(label['h'])
#                     img = cv2.imread(train_path + '\\' + c + '\\' + img_folder_name + '\\' + img_name + '.jpg')
#                     img = cv2.rectangle(img,(x,y), (x+w-1,y+h-1), (0,255,0), 4)
#                     display_image_set.append(img)
#                     if not os.path.exists('\\dataset\\visualize\\' + c + '\\' + img_folder_name):
#                         os.makedirs('\\dataset\\visualize\\' + c + '\\' + img_folder_name)
#                     cv2.imwrite('\\dataset\\visualize\\' + c + '\\' + img_folder_name + '\\' + img_name + '.jpg', img)
#                     # break_flag = 1
#                     break
#
#             # if break_flag == 1:
#             #     break
#
# # visualize the stored samples with different classes
# fig = plt.figure(figsize=(32,32))
# for i in range(len(CLASS_NAMES)):
#     plt.subplot(2,3,i+1)
#     plt.imshow(display_image_set[i])
#     plt.title(CLASS_NAMES[i])
#     plt.axis('off')
# plt.tight_layout()
# plt.show()