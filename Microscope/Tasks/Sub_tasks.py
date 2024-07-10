encoding = "utf-8"
import serial.tools.list_ports
# import nexcam
from pycromanager import Acquisition, Bridge
from pycromanager import Acquisition, multi_d_acquisition_events, start_headless
import os
import sys
from Models.test_oneshot import one_test_cervical_cancer_cells
from Microscope.Logical_library.point_AF import AFocus
import time
from PIL import Image, ImageTk
import cv2
import numpy as np
from pathlib import Path
import random

start = time.time()
mm_app_path = 'C:\\Program Files\\Micro-Manager-2.0'
config_file = 'D:\\Micro_Test\\config\\nexcam.cfg'
start_headless(mm_app_path, config_file, timeout=5000)
bridge = Bridge()
core = bridge.get_core()

def XY_position(Number_of_slide):

    positions = {
        1: ([10500000, 3300000], [8400000, 780000]),
        2: ([7600000, 3300000], [5400000, 780000]),
        3: ([4750000, 3300000], [2600000, 780000]),
        4: ([1900000, 3300000], [0, 780000])
    }

    if Number_of_slide in positions:
        return positions[Number_of_slide]
    else:
        raise ValueError("Invalid slide number. Please enter a number between 1 and 4.")


def move_to_current_XY_position(current_posX, current_posY, z_position=880000):

    core.set_xy_position(current_posX, current_posY)
    core.wait_for_device("XYStage")

    core.set_position('ZStage', z_position)

    data = f'GP {current_posX},{current_posY},{z_position}\r'
    print(f"Initial coordinates of the stage: {data}")

def converter(wjtn):

    magnifications = {
        4: ("4X", 3),
        10: ("10X", 4),
        20: ("20X", 5),
        40: ("40X", 1)
    }

    if wjtn in magnifications:
        ratio, WJ = magnifications[wjtn]
        core.set_state('ObjectiveTurret', WJ)
        core.wait_for_device('ObjectiveTurret')
        print(f"The magnification is now set to {ratio}.")
    else:
        raise ValueError("Invalid magnification value. Valid options are 4, 10, 20, or 40.")

def step(wjtn):

    step_sizes = {
        4: [370000, 245000],   # Step sizes for 4X magnification
        10: [150000, 100000],
        20: [75000, 50000],
        40: []
    }

    if wjtn in step_sizes:
        return step_sizes[wjtn]
    else:
        raise ValueError(f"Unsupported magnification: {wjtn}. Valid options are 4, 10, 20, 40.")

def photo_a_microview(save_path, name):

    events = [
        {
            "axes": {"subset": 0, "time": 0},
            "min_start_time": 0,
        }
    ]
    def image_processor(image, metadata):
        frame = np.reshape(image.pix, newshape=[metadata['Height'], metadata['Width']])

        cv2.namedWindow("capture", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("capture", 800, 600)
        cv2.imshow("capture", frame)
        cv2.waitKey(1)  # Refresh the display window

        image_filename = f"{name}.png"
        full_path = os.path.join(save_path, image_filename)
        cv2.imwrite(full_path, frame)
        print("Image saved successfully at:", full_path)

    with Acquisition(directory=save_path, name=name, show_display=False, image_process_fn=image_processor) as acq:
        acq.acquire(events)

def setup_camera():
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

setup_camera()


