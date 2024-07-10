import serial.tools.list_ports
from pycromanager import Acquisition, Bridge
from pycromanager import multi_d_acquisition_events, start_headless
import os
import sys
from Microscope.Logical_library.mic_stage import mv, move_xyz
from Microscope.Logical_library.mic_lens import converter
from Microscope.Logical_library.mic_sensor import cap_fov
from Microscope.Logical_library.glob_AF import (autofocus_and_record_positions, find_top_left_focus,
                                                get_corners_focus_values, interpolate_focus)
from Microscope.Logical_library.point_AF import AFocus
import time
import warnings
from Microscope.Logical_library.VM_CCA_Class import CCAPredictor10, CCAPredictor20
import tkinter as tk
from threading import Thread
import sys

warnings.filterwarnings("ignore")
sys.path.append(os.getcwd())
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
start = time.time()
mm_app_path = '\\Micro-Manager-2.0'
config_file = '\\config\\nexcam.cfg'
start_headless(mm_app_path, config_file, timeout=5000)
bridge = Bridge()
core = bridge.get_core()

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
    window.title("real-time result")
    window.geometry("600x400")

    text_output = tk.Text(window, wrap=tk.WORD, font=("Arial Unicode MS", 10))
    text_output.pack(expand=True, fill=tk.BOTH)

    sys.stdout = RedirectedOutput(text_output)

    window.mainloop()


def prepare_pos(current_posX, current_posY, z_position=880000):

    core.set_xy_position(current_posX, current_posY)
    core.wait_for_device("XYStage")

    core.set_position('ZStage', z_position)
    data = f'GP {current_posX},{current_posY},{z_position}\r'
    print(f"Initial coordinates of the stage: {data}")



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


def move(current_posx, current_posy, judge):
    time.sleep(0.1)
    core.set_xy_position(current_posx, current_posy)
    if judge:
        core.wait_for_device("XYStage")

def output_message(positive_num, positive_list, grade):
    if len(positive_list) == 0:
        print("There are currently no samples of patients with a possibility of being positive.")
        return

    if len(positive_list) == 1:
        formatted_list = str(positive_list[0])
    else:
        formatted_list = ", ".join(map(str, positive_list[:-1])) + " and " + str(positive_list[-1])

    message = (f"There are currently {positive_num} FOVs of patients with "
               f"a possibility of being positive, namely samples {formatted_list}."
               f"Where suspected {grade}")
    print(message)
    return message


def VLT_CCA_Class_Screening_4slides():

    Thread(target=create_window).start()
    ports_list = list(serial.tools.list_ports.comports())
    if len(ports_list) <= 0:
        print("No serial device.")
    else:
        print("\033[1;31m\nThe available devices are as follows: \033[0m\n")
        print("%-10s %-50s %-10s" % ("num", "name", "number"))
        for i in range(len(ports_list)):
            comport = list(ports_list[i])
            comport_number, comport_name = comport[0], comport[1]
            print("%-10s %-50s %-10s" % (i, comport_name, comport_number))

        port_num = ports_list[0][0]
        print("Default selection of serial port: %s\n" % port_num)
        ser = serial.Serial(port=port_num, baudrate=9600, bytesize=serial.SEVENBITS, stopbits=serial.STOPBITS_TWO,
                            timeout=0.5)
        if ser.isOpen():
            print("Successfully opened serial port, number: %s" % ser.name)
        else:
            print("Unable to open serial port.")
        print('\n')

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

    cca_predictor = CCAPredictor10()
    plf_flux = 4
    positive_list = []
    wjtn = [10, 20, 4, 40]
    fine_flag = False
    for s in range(plf_flux):
        post_pt = []
        grade = []
        positive_num10 = 0
        s = s + 1
        pos_0, pos_1 = mv(s)
        pos_all = 0
        move(pos_0[0], pos_0[1], 1)
        time.sleep(1)
        converter(core, wjtn[0])
        stepn = step(wjtn[0])
        step_x = stepn[0]
        step_y = stepn[1]
        focus_coords, steps_X, steps_Y, start_point_, end_point_ = autofocus_and_record_positions(core, pos_0, pos_1, Focus_time_X, Focus_time_Y)
        current_posx = start_point_[0]
        current_posy = start_point_[1]
        path = '/Temporary_Files/save_images/slide' + str(s) + '_' + str(wjtn[0]) + 'x_0/'
        if not os.path.exists(path):
            os.mkdir(path)

        while (current_posy <= pos_1[1]):
            stop_flag = 0
            k = 0
            name = 'IMG_10_' + str(current_posx - pos_0[0]) + '_' + str(current_posy - pos_0[1])
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
                cap_fov(path, name)
            while (current_posx <= pos_1[0]):
                k = k + 1
                name = 'IMG_10_' + str(current_posx - pos_0[0]) + '_' + str(current_posy - pos_0[1])
                current_posx = current_posx + step_x
                top_left_focus = find_top_left_focus(start_point_, end_point_, current_posx, current_posy,
                                                     focus_coords, steps_X, steps_Y, Focus_time_X, Focus_time_Y)
                if top_left_focus:
                    top_left, top_right, bottom_left, bottom_right = get_corners_focus_values(top_left_focus, focus_coords,
                                                                                              steps_X, steps_Y)

                    if top_right is None or bottom_left is None:

                        focus_Z = top_left_focus[2]
                    else:
                        x_relative = (current_posx - top_left_focus[0]) // steps_X
                        y_relative = (current_posy - top_left_focus[1]) // steps_Y

                        #
                        focus_Z = interpolate_focus(
                            x_relative, y_relative,
                            top_left[2], top_right[2],
                            bottom_left[2], bottom_right[2],
                            )
                    move_xyz(core, current_posx, current_posy, focus_Z, 1)
                    time.sleep(0.02)
                    cap_fov(path, name)
                    img_path = path + f'{name}.png'
                    print('----' + name)
                    text_result, _ = cca_predictor.predict(img_path, 10)
                    #
                    if text_result == 'Positive':
                        stop_flag = 1
                        positive_num10 = positive_num10 + 1
                        post_pt.append([current_posx, current_posy])

            current_posx = pos_0[0]
            current_posy = current_posy + step_y
            time.sleep(0.5)

        if stop_flag == 0:
            break
        stepn = step(wjtn[1])
        step_x = stepn[0]
        step_y = stepn[1]
        pp = 0
        cca_predictor = CCAPredictor20()
        converter(core, wjtn[1])
        if len(post_pt) > 10:
            g_a = 1
            focus_coords, steps_X, steps_Y, start_point_, end_point_ = autofocus_and_record_positions(core, pos_0,
                                                                                                      pos_1,
                                                                                                      Focus_time_X,
                                                                                                      Focus_time_Y)
        for c in post_pt:
            cx, cy = c[0], c[1]

            positive_num20 = 0
            while (cx <= cy+100000):
                stop_flag = 0
                name = 'IMG_20_' + str(cx - pos_0[0]) + '_' + str(cy - pos_0[1])
                if g_a == 1:
                    top_left_focus = find_top_left_focus(start_point_, end_point_, cx, cy, focus_coords,
                                                         steps_X, steps_Y)
                    if top_left_focus:
                        top_left, top_right, bottom_left, bottom_right = get_corners_focus_values(top_left_focus,
                                                                                                  focus_coords,
                                                                                                  steps_X, steps_Y)

                        if top_right is None or bottom_left is None:
                            focus_Z = top_left_focus[2]
                        else:
                            x_relative = (cx - top_left_focus[0]) // steps_X
                            y_relative = (cy - top_left_focus[1]) // steps_Y

                            focus_Z = interpolate_focus(
                                x_relative, y_relative,
                                top_left[2], top_right[2],
                                bottom_left[2], bottom_right[2],
                            )
                else:
                    focus_Z = AFocus(core, cx, cy, focus_Z)
                move_xyz(core, cx, cy, focus_Z, 1)
                cap_fov(path, name)
                while (cx <= cx+150000):
                    name = 'IMG_20_' + str(cx - pos_0[0]) + '_' + str(cy - pos_0[1])
                    cx = cx + step_x
                    if g_a == 1:
                        top_left_focus = find_top_left_focus(start_point_, end_point_, cx, cy,
                                                             focus_coords, steps_X, steps_Y, Focus_time_X, Focus_time_Y)
                        if top_left_focus:
                            top_left, top_right, bottom_left, bottom_right = get_corners_focus_values(top_left_focus,
                                                                                                      focus_coords,
                                                                                                      steps_X, steps_Y)

                            if top_right is None or bottom_left is None:
                                focus_Z = top_left_focus[2]
                            else:
                                x_relative = (cx - top_left_focus[0]) // steps_X
                                y_relative = (cy - top_left_focus[1]) // steps_Y

                                focus_Z = interpolate_focus(
                                    x_relative, y_relative,
                                    top_left[2], top_right[2],
                                    bottom_left[2], bottom_right[2],
                                )
                    else:
                        focus_Z = AFocus(core, cx, cy, focus_Z)
                    move_xyz(core, cx, cy, focus_Z, 1)
                    cap_fov(path, name)
                    img_path = path + f'{name}.png'
                    print('----' + name)
                    text_result, pp0 = cca_predictor.predict(img_path, 20)
                    if text_result not in ['NILM', 'BKG']:
                        positive_num20 = positive_num20 + 1
                        pos_all = pos_all+1
                        pp = pp + pp0
                        if text_result not in grade:
                            grade.append(text_result)
                cx = c[0]
                cy = cy + step_y
                time.sleep(0.5)
        positive_list.append(s)
    message = output_message(pos_all, positive_list, grade)
    ser.close()

    return message

if __name__ == '__main__':
    Focus_time_X, Focus_time_Y = 7, 9
    VLT_CCA_Class_Screening_4slides()
