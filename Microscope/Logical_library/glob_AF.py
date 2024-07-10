import time
from Microscope.Logical_library.mic_stage import mv, move
from Microscope.Logical_library.point_AF import AFocus
from Microscope.Logical_library.mic_sensor import clear_buffer

def find_top_left_focus(pos0, pos1, current_X, current_Y, focus_coords, stepX, stepY, Focus_time_X, Focus_time_Y):
    grid_x = (current_X - pos0[0]) // stepX
    grid_y = (current_Y - pos0[1]) // stepY

    grid_x = max(1, min(grid_x, Focus_time_X - 2))
    grid_y = max(1, min(grid_y, Focus_time_Y - 2))

    for focus in focus_coords:
        if (focus[0] == pos0[0] + grid_x * stepX) and (focus[1] == pos0[1] + grid_y * stepY):
            return focus
    return None

def get_corners_focus_values(top_left_focus, focus_coords, stepX, stepY):
    top_left = top_left_focus
    top_right = bottom_left = bottom_right = None

    for focus in focus_coords:
        if focus[1] == top_left[1] and focus[0] == top_left[0] + stepX:
            top_right = focus
        elif focus[0] == top_left[0] and focus[1] == top_left[1] + stepY:
            bottom_left = focus
        elif focus[0] == top_left[0] + stepX and focus[1] == top_left[1] + stepY:
            bottom_right = focus

    return top_left, top_right, bottom_left, bottom_right

def interpolate_focus(x_percent, y_percent, top_left, top_right, bottom_left, bottom_right):

    top_focus = top_left + (top_right - top_left) * x_percent
    bottom_focus = bottom_left + (bottom_right - bottom_left) * x_percent

    focus_value = top_focus + (bottom_focus - top_focus) * y_percent

    return focus_value

def autofocus_and_record_positions(core, pos10, pos11, Focus_time_X, Focus_time_Y):

    focus_positions = []

    steps_X = (pos11[0] - pos10[0]) // (Focus_time_X - 1)
    steps_Y = (pos11[1] - pos10[1]) // (Focus_time_Y - 1)
    max_clarity = 0
    current_Z = 925000
    current_Z = 3248400
    for i in range(1, Focus_time_Y-1):
        current_Y = pos10[1] + i * steps_Y
        time.sleep(1)
        clarity_list = []
        z_positions = []
        current_row_indices = []

        for j in range(1, Focus_time_X-1):
            current_X = pos10[0] + j * steps_X
            move(core, current_X, current_Y, 1)

            clear_buffer(core, 1)
            current_Z, max_clarity, frames = AFocus(core, current_X, current_Y, current_Z, fine_flag=False, max_clarity_former =max_clarity)
            clear_buffer(core, 1)

            clarity_list.append(max_clarity)
            z_positions.append(current_Z)

            focus_positions.append([current_X, current_Y, current_Z, max_clarity])
            current_row_indices.append(len(focus_positions) - 1)

        for index in current_row_indices:
            if (focus_positions[index][3] < 10):
                closest_foreground_index = None
                min_distance = float('inf')
                for other_index in current_row_indices:
                    if (focus_positions[other_index][3] > 10):
                        distance = abs(index - other_index)
                        if distance < min_distance:
                            closest_foreground_index = other_index
                            min_distance = distance

                if closest_foreground_index is not None:
                    focus_positions[index][2] = focus_positions[closest_foreground_index][2]


    return focus_positions, steps_X, steps_Y