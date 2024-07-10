import cv2
import numpy as np
from pycromanager import Acquisition, Bridge
import os

def cap_fov(save_path, name):
    """
    Captures a microview image, processes it, and saves it to the specified directory.
    """
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
        cv2.waitKey(1)

        image_filename = f"{name}.png"
        full_path = os.path.join(save_path, image_filename)
        cv2.imwrite(full_path, frame)
        print("Image saved successfully at:", full_path)

    with Acquisition(directory=save_path, name=name, show_display=False, image_process_fn=image_processor) as acq:
        acq.acquire(events)


def clear_buffer(core, frames_to_clear=1):
    for _ in range(frames_to_clear):
        cap_fov('/Temporary_Files/AF/', 'AF')