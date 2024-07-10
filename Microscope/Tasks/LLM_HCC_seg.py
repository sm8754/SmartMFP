
import serial.tools.list_ports
import os
import time
import warnings
# from PIL import Image, ImageTk
import cv2
from pycromanager import Acquisition, Bridge
from pycromanager import multi_d_acquisition_events, start_headless
from Microscope.Logical_library.VM_HCC_seg import hccPredictor10, hccPredictor20
from Microscope.Logical_library.mic_stage import *
from Microscope.Logical_library.mic_lens import converter
from Microscope.Logical_library.glob_AF import *
from Microscope.Logical_library.mic_sensor import *
import tkinter as tk
from tkinter import ttk
from copy import deepcopy
from threading import Thread
import sys
import numpy as np
import glob
from PIL import Image


warnings.filterwarnings("ignore")
sys.path.append(os.getcwd())
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

class RedirectedOutput:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)

    def flush(self):
        pass

def create_window():
    window = tk.Tk()
    window.title("Real time process")
    window.geometry("160x90")

    text_output = tk.Text(window, wrap=tk.WORD, font=("Arial Unicode MS", 7))
    text_output.pack(expand=True, fill=tk.BOTH)

    sys.stdout = RedirectedOutput(text_output)

    window.mainloop()



def step(wjtn):

    step_sizes = {
        4: [370000, 245000],
        10: [150000, 100000],
        20: [75000, 50000],
        40: [37500, 25000]
    }

    if wjtn in step_sizes:
        return step_sizes[wjtn]
    else:
        raise ValueError(f"Unsupported magnification: {wjtn}. Valid options are 4, 10, 20, 40.")

def sled(core, val):
    try:
        core.set_property('LEDDevice', val)
        print("LED：", val)
    except Exception as e:
        print(f"An error occurred: {str(e)}")



def pt_hcc(filepath, name):

    img_folders = glob.glob(filepath + name + "\\*.png")

    MAX_X = -1
    MAX_Y = -1

    for img_path in img_folders:
        filename = img_path.split('\\')[-1]
        x, y = map(int, filename.split('.')[0].split('_')[1:3])
        MAX_X = max(MAX_X, x)
        MAX_Y = max(MAX_Y, y)


    step_4x = [370000, 245000]
    step_10x = [150000, 100000]
    step_20x = [75000, 50000]
    step_40x = [37500, 25000]
    gap_x = step_20x[0]
    gap_y = step_20x[1]
    IMAGE_ROW = MAX_Y // gap_y + 1
    IMAGE_COLUMN = MAX_X // gap_x + 1
    IMAGE_SIZE_X = 384
    IMAGE_SIZE_Y = 256

    to_image = Image.new('RGB', ((IMAGE_COLUMN - 1) * IMAGE_SIZE_X, IMAGE_ROW * IMAGE_SIZE_Y))

    for img_path in img_folders:
        filename = img_path.split('\\')[-1]
        x, y = map(int, filename.split('.')[0].split('_')[1:3])
        i = x // gap_x
        j = y // gap_y
        from_image = Image.open(img_path).resize((IMAGE_SIZE_X, IMAGE_SIZE_Y), Image.ANTIALIAS)
        to_image.paste(from_image, (i * IMAGE_SIZE_X, j * IMAGE_SIZE_Y))
    final_image_path = filepath + "seghcc.png"
    to_image.save(final_image_path)
    print("Image stitched and saved at", final_image_path)
    return final_image_path


def interpolate_focus(x_percent, y_percent, top_left, top_right, bottom_left, bottom_right):

    top_focus = top_left + (top_right - top_left) * x_percent
    bottom_focus = bottom_left + (bottom_right - bottom_left) * x_percent

    focus_value = top_focus + (bottom_focus - top_focus) * y_percent

    return focus_value

def display_table(slide_result):
    root = tk.Tk()
    root.title('Slide Results')

    tree = ttk.Treeview(root, columns=list(slide_result[0].keys()), show='headings')
    tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    for col in slide_result[0].keys():
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor=tk.W)

    for item in slide_result:
        tree.insert('', tk.END, values=list(deepcopy(item).values()))

    root.mainloop()

def generate_summary(slide_result):
    summaries = []

    for item in slide_result:
        slide = item["slide"]

        total_patches = sum([v for k, v in item.items() if k not in ["slide", "pos_nums"]])

        if item["background"] + item["normal"] == total_patches:
            summary = f"Slide {slide} has no positive patches. The patient had no cervical lesions.\n"
        else:
            hcc_propt = (slide_result['tumor'] / (slide_result['tumor'] + slide_result['normal'])) * 100
            summary = f"Slide {slide}: Liver cancer tissues comprises {hcc_propt} of the total area.\n"
        summaries.append(summary)

    return ' '.join(summaries)

def VLT_HCC_Seg_4slides():
    Thread(target=create_window).start()
    ports_list = list(serial.tools.list_ports.comports())
    if len(ports_list) <= 0:
        print("There is no serial device")
    else:
        print("\nThe available serial devices are: \n")
        print("%-10s %-50s %-10s" % ("num", "name", "number"))
        for i in range(len(ports_list)):
            comport = list(ports_list[i])
            comport_number, comport_name = comport[0], comport[1]
            print("%-10s %-50s %-10s" % (i, comport_name, comport_number))

        port_num = ports_list[0][0]
        print("Default selection for serial port: %s\n" % port_num)
        ser = serial.Serial(port='COM3', baudrate=9600, bytesize=serial.SEVENBITS, stopbits=serial.STOPBITS_TWO,
                            timeout=0.5)
        if ser.isOpen():
            print("Successfully opened serial port, Number: %s" % ser.name)
        else:
            print("no serical.")
        print('\n')

#     cap = cv2.VideoCapture(0)
#
#     if not cap.isOpened():
#         print("no camera")
#         exit()
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3072)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2048)
#     cap.set(cv2.CAP_PROP_FPS, 60)
#     # cap.set(cv2.CAP_PROP_AUTO_WB, 0)
#     # cap.set(cv2.CAP_PROP_EXPOSURE, -10)
#     # cap.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, 5800)
#     # cap.set(cv2.CAP_PROP_HUE, -15)
#     cap = Camera_Collecting()

    mm_app_path = '\\Micro-Manager-2.0'
    config_file = '\\config\\nexcam.cfg'
    start_headless(mm_app_path, config_file, timeout=5000)
    bridge = Bridge()
    core = bridge.get_core()
    try:
        core.set_camera_device("CameraDeviceName")
    except:
        print("Unable to open camera")
        return
    try:
        # Here, we use general attributes as an example,
        # which need to be adjusted according to the specific camera model during actual use
        core.set_property("CameraDeviceName", "Exposure", 100.0)
        core.set_property("CameraDeviceName", "Frame Rate", "60")
        core.set_property("CameraDeviceName", "Resolution", "1536x1024")

        print("The camera has been successfully set up")
        return bridge, core
    except Exception as e:
        print(f"Error setting camera parameters: {str(e)}")

    hcc_predictor10 = hccPredictor10()

    slide_results = []
    wjtn = 4
    converter(core, wjtn)
    Focus_time_X, Focus_time_Y = 6, 11
    for s in slide_num:
        positive_dict = {"slide": 0, "pos_nums": 0, 'tumor': 0, 'normal': 0, "background": 0}

        post_pt = []
        positive_dict['slide'] = s
        pos_0, pos_1 = mv(s)

        stepn = step(wjtn)
        step_x = stepn[0]
        step_y = stepn[1]


        focus_coords, steps_X, steps_Y, start_point_, end_point_ = autofocus_and_record_positions(core, pos_0, pos_1, Focus_time_X, Focus_time_Y)
        print('Focusing completed, focus list has been saved.')
        current_posx = start_point_[0]
        current_posy = start_point_[1]

        path = '/Temporary_Files/save_images/hcc/slide' + str(s) + '_' + str(wjtn) + 'x_0' + '\\'
        if not os.path.exists(path):
            os.mkdir(path)

        print("Segmenting the tumor with low magnification")

        while (current_posy <= end_point_[1]):
            k = 0

            top_left_focus = find_top_left_focus(start_point_, end_point_, current_posx, current_posy, focus_coords, steps_X, steps_Y)
            if top_left_focus:
                top_left, top_right, bottom_left, bottom_right = get_corners_focus_values(top_left_focus, focus_coords,
                                                                                          steps_X, steps_Y)
                if top_right is None or bottom_left is None:
                    focus_Z = top_left_focus[2]
                else:
                    x_relative = (current_posx - top_left_focus[0]) // steps_X
                    y_relative = (current_posy - top_left_focus[1]) // steps_Y

                    focus_Z = interpolate_focus(
                        x_relative, y_relative,
                        top_left[2], top_right[2],
                        bottom_left[2], bottom_right[2],
                        )
                move_xyz(core, current_posx, current_posy, focus_Z, 1)

            clear_buffer(core, 1)
            time.sleep(0.05)
            while (current_posx <= end_point_[0]):
                k = k + 1

                name = 'IMG_' + str(current_posx - start_point_[0]) + '_' + str(current_posy - start_point_[1])
                current_posx = current_posx + step_x

                top_left_focus = find_top_left_focus(start_point_, end_point_, current_posx, current_posy, focus_coords, steps_X, steps_Y)
                if top_left_focus:
                    top_left, top_right, bottom_left, bottom_right = get_corners_focus_values(top_left_focus, focus_coords,
                                                                                              steps_X, steps_Y)

                    if top_right is None or bottom_left is None:
                        focus_Z = top_left_focus[2]
                    else:
                        x_relative = (current_posx - top_left_focus[0]) // steps_X
                        y_relative = (current_posy - top_left_focus[1]) // steps_Y

                        focus_Z = interpolate_focus(
                            x_relative, y_relative,
                            top_left[2], top_right[2],
                            bottom_left[2], bottom_right[2],
                            )

                    move_xyz(core, current_posx, current_posy, focus_Z, 0)

                    clear_buffer(core, 1)
                    time.sleep(0.05)
                    cap_fov(core, path, name)

                    img_path = path + f'{name}.png'

                    ret, positive_dict['tumor'], positive_dict['normal'], positive_dict['background'] = hcc_predictor10.predict(img_path)
                    if ret:
                        stop_flag = 1
                        post_pt.append([current_posx, current_posy])

            current_posx = start_point_[0]
            current_posy = current_posy + step_y
        slide_results.append(positive_dict)

        if stop_flag == 0:
            break
        print('Tumor segmentation completed. Calculate the position...\n')
        print('Tumor position:', post_pt)
        stepn = step(20)
        step_x = stepn[0]
        step_y = stepn[1]
        pp = 0
        converter(core, 20)
        hcc_predictor20 = hccPredictor20()
        Focus_time_X, Focus_time_Y = 5, 7
        positive_dict = {"slide": 0, "pos_nums": 0, 'tumor': 0, 'normal': 0, "background": 0}

        current_posx_list, current_posy_list = zip(*post_pt)
        pos_0, pos_1 = [min(current_posx_list), min(current_posy_list)], [max(current_posx_list), max(current_posy_list)]
        focus_coords, steps_X, steps_Y, start_point_, end_point_ = autofocus_and_record_positions(core, pos_0,
                                                                                                  pos_1,
                                                                                                  Focus_time_X,
                                                                                                  Focus_time_Y)

        print('Focusing completed, focus list has been saved.')
        current_posx = start_point_[0]
        current_posy = start_point_[1]

        while (current_posy <= end_point_[1]):
            k = 0

            top_left_focus = find_top_left_focus(start_point_, end_point_, current_posx, current_posy, focus_coords, steps_X, steps_Y)
            if top_left_focus:
                top_left, top_right, bottom_left, bottom_right = get_corners_focus_values(top_left_focus, focus_coords,
                                                                                          steps_X, steps_Y)
                if top_right is None or bottom_left is None:
                    focus_Z = top_left_focus[2]
                else:
                    x_relative = (current_posx - top_left_focus[0]) // steps_X
                    y_relative = (current_posy - top_left_focus[1]) // steps_Y

                    focus_Z = interpolate_focus(
                        x_relative, y_relative,
                        top_left[2], top_right[2],
                        bottom_left[2], bottom_right[2],
                        )
                move_xyz(core, current_posx, current_posy, focus_Z, 1)

            clear_buffer(core, 1)
            time.sleep(0.05)
            while (current_posx <= end_point_[0]):
                k = k + 1

                name = 'IMG_20_' + str(current_posx - start_point_[0]) + '_' + str(current_posy - start_point_[1])
                current_posx = current_posx + step_x

                top_left_focus = find_top_left_focus(start_point_, end_point_, current_posx, current_posy, focus_coords, steps_X, steps_Y)
                if top_left_focus:
                    top_left, top_right, bottom_left, bottom_right = get_corners_focus_values(top_left_focus, focus_coords,
                                                                                              steps_X, steps_Y)

                    if top_right is None or bottom_left is None:
                        focus_Z = top_left_focus[2]
                    else:
                        x_relative = (current_posx - top_left_focus[0]) // steps_X
                        y_relative = (current_posy - top_left_focus[1]) // steps_Y

                        focus_Z = interpolate_focus(
                            x_relative, y_relative,
                            top_left[2], top_right[2],
                            bottom_left[2], bottom_right[2],
                            )

                    move_xyz(core, current_posx, current_posy, focus_Z, 0)

                    clear_buffer(core, 1)
                    time.sleep(0.02)
                    cap_fov(core, path, name)

                    img_path = path + f'{name}.png'
                    print('----' + name)
                    ret, tumor_count, nor_count, bkg_count = hcc_predictor20.predict(img_path)
                    positive_dict['tumor'] += tumor_count
                    positive_dict['normal'] +=nor_count
                    positive_dict['background'] += bkg_count

            current_posx = start_point_[0]
            current_posy = current_posy + step_y
        slide_results.append(positive_dict)
        hcc_area = (positive_dict['tumor'] * (0.25 * 65536))/1000000

    display_table(slide_results)

    print('Segmentation Completed!\n')

    message = generate_summary(slide_results)
    ser.close()
    cv2.destroyAllWindows()
    pt_hcc(path, name)
    return message

if __name__ == '__main__':
    Focus_time_X, Focus_time_Y = 5, 7
    slide_num = [1, 2, 3, 4]
    VLT_HCC_Seg_4slides()

