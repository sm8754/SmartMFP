
import nexcam
import time
import serial.tools.list_ports
import cv2
import os
import shutil
import numpy as np
import math
from skimage import data, filters
from pycromanager import Acquisition, Bridge
from pycromanager import multi_d_acquisition_events, start_headless
from Microscope.Logical_library.mic_sensor import clear_buffer
from Microscope.Logical_library.mic_stage import move_z

down_z = 925000
up_z = 938000
step_z = 300
step_z_fine = 100

save_path = '\\Temporary_Files\\AFocus\\'
save_temp_af_imgs = False

def Folder_count(path):
    count = 0
    filelist = os.listdir(path)
    for f in filelist:
        filepath = os.path.join(path, f)
        if os.path.isfile(filepath):
            os.remove(filepath)
        elif os.path.isdir(filepath):
            shutil.rmtree(filepath, True)
    for file in os.listdir(path):
        file = os.path.join(path, file)
        if os.path.isdir(file):
            count = count+1
    return count

def Laplacian(img):

    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    return cv2.Laplacian(gray_img, cv2.CV_64F).var()

def tenengrad(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    out = filters.sobel(gray_img)
    out = np.sum(out**2)
    out = np.sqrt(out)
    return out

def Compute_Clarity(img, save_flag):
    if save_flag:
        img = cv2.imread(img, cv2.IMREAD_COLOR)
    clarity = Laplacian(img)
    return clarity

def photo_a_microview(core, current_X, current_Y, current_Z, save_flag, qq, show_focus = True):

    events = [
        {
            "axes": {"subset": 0, "time": 0},
            "min_start_time": 0,
        }
    ]
    def image_processor(image, metadata):
        frame = np.reshape(image.pix, newshape=[metadata['Height'], metadata['Width']])

        if save_flag:
            if qq == 1:
                image_filename = f'{int(current_X / 100)}_{int(current_Y / 100)}_{int(current_Z / 100)}.bmp'
            else:
                image_filename = f'{int(current_X / 100)}_{int(current_Y / 100)}_{int(current_Z / 100)}.png'
            cv2.imwrite(save_path + image_filename, frame)
            out = Compute_Clarity(save_path + image_filename, save_flag)
        else:

            out = Compute_Clarity(frame, save_flag)

        if current_Z <= up_z and (not show_focus):
            window_name = "Capture Window"
            cv2.namedWindow(window_name, 0)
            cv2.resizeWindow(window_name, 180, 120)
            cv2.imshow(window_name, frame)
            cv2.setWindowTitle(window_name, f"X: {current_X}, Y: {current_Y}, Z: {current_Z}, Clarity: {out}")
            cv2.waitKey(1)
        elif show_focus:
            clear_buffer(core, 1)
            frame = np.reshape(image.pix, newshape=[metadata['Height'], metadata['Width']])
            cv2.destroyWindow("Capture Window")
            window_name = "Focus Window"
            cv2.namedWindow(window_name, 0)
            cv2.resizeWindow(window_name, 180, 120)
            cv2.imshow(window_name, frame)
            cv2.setWindowTitle(window_name, f"X: {current_X}, Y: {current_Y}, Clarity: {out}")
            cv2.waitKey(1)

        return out, frame

    with Acquisition(directory=save_path, show_display=False, image_process_fn=image_processor) as acq:
        acq.acquire(events)

def Fine_focus(core, current_X, current_Y, Focus_point_Z):
    Folder_count(save_path)
    clarity_list = []
    range_down = Focus_point_Z-step_z
    range_up = Focus_point_Z + step_z
    for current_Z in range(range_down, range_up, step_z_fine):
        move_z(core, current_Z, 1)
        clarity, frames = photo_a_microview(core, current_X, current_Y, current_Z, save_flag=save_temp_af_imgs,qq=0)
        record_every_position = {'position': current_Z, 'clarity': clarity}
        clarity_list.append(record_every_position)
    max_clarity = 0
    for index in clarity_list:
        if index['clarity'] > max_clarity:
            max_clarity = index['clarity']
            Focus_point_Z_new = int(index['position'])
    return Focus_point_Z_new, max_clarity

def AFocus(core, current_X, current_Y, current_Z_former=925000, fine_flag = False, max_clarity_former = 0):
    clarity_list = []
    decline_count = 0
    mf = False

    clear_buffer(core, 1)
    if max_clarity_former > 15:
        down_z = current_Z_former - 10 * step_z
        up_z = current_Z_former + 10 * step_z
    else:
        down_z = 925000
        up_z = 938000
    for current_Z in range(down_z, up_z, step_z):

        move_z(core, current_Z, 1)
        clarity, frames = photo_a_microview(core, current_X, current_Y, current_Z, save_flag=save_temp_af_imgs, qq=0, show_focus = False)

        record_every_position = {'position': current_Z, 'clarity': clarity}
        clarity_list.append(record_every_position)

        if len(clarity_list) > 1 and clarity_list[-1]['clarity'] < clarity_list[-2]['clarity']:
            decline_count += 1
        else:
            decline_count = 0

        if decline_count >= 5:
            break


    max_clarity = 0
    time.sleep(0.1)
    index_flag = 0
    for index in clarity_list[1:-1]:
        index_flag = index_flag + 1
        # print(index)
        if index['clarity'] > max_clarity:
            max_clarity = index['clarity']
            Focus_point_Z = index['position']
            index_flags  = index_flag

    if fine_flag:
        move_z(core, Focus_point_Z-step_z, 0)
        Focus_point_Z, max_clarity = Fine_focus(core, current_X, current_Y, Focus_point_Z)
        time.sleep(0.1)
    move_z(core, Focus_point_Z, 1)
    time.sleep(0.05)
    clear_buffer(core, 1)
    clarity, _ = photo_a_microview(core, current_X, current_Y, Focus_point_Z, save_flag=False, qq=1, show_focus = True)

    return Focus_point_Z, max_clarity, frames


if __name__ == "__main__":

    # cap = cv2.VideoCapture(0)  #
    #
    # if not cap.isOpened():
    #     print("no camera")
    #     exit()
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3072)
    #
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2048)
    # cap.set(cv2.CAP_PROP_FPS, 60)
    # # cap.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, 5600)
    # # cap.set(cv2.CAP_PROP_HUE, -15)
    mm_app_path = '\\Micro-Manager-2.0'
    config_file = '\\config\\nexcam.cfg'
    start_headless(mm_app_path, config_file, timeout=5000)
    bridge = Bridge()
    core = bridge.get_core()
    try:
        core.set_camera_device("CameraDeviceName")
    except:
        print("Unable to open camera")
    try:

        core.set_property("CameraDeviceName", "Exposure", 100.0)
        core.set_property("CameraDeviceName", "Frame Rate", "60")
        core.set_property("CameraDeviceName", "Resolution", "1536x1024")
        print("The camera has been successfully set up")

    except Exception as e:
        print(f"Error setting camera parameters: {str(e)}")

    save_path = 'E:\\LLM-Micro-main\\Temporary_Files\\AFocus\\'

    save_temp_af_imgs = False
    AFocus(core, 6338451, 1094571, 3251000, fine_flag=False)

    print("----------OK----------")

