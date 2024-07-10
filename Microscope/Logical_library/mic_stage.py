import time

def mv(s):

    positions = {
        1: ([0, 750000], [2000000, 3080000]),
        2: ([2500000, 750000], [4700000, 3080000]),
        3: ([5500000, 750000], [7800000, 3080000]),
        4: ([8350000, 750000], [10540000, 3080000])
    }

    pos_start = [positions[i][0] for i in range(1, 5)]
    pos_end = [positions[i][1] for i in range(1, 5)]

    if s == 0:
        return pos_start, pos_end
    elif s in positions:
        return positions[s]
    else:
        raise ValueError("Invalid slide index. Please enter a number between 0 and 4.")


def move(core, current_posx, current_posy, judge):
    time.sleep(0.1)
    core.set_xy_position(current_posx, current_posy)
    if judge:
        core.wait_for_device("XYStage")


def move_z(core, current_Z, wait):

    core.set_position('ZStage', current_Z)
    if wait:
        core.wait_for_device("ZStage")

def move_xyz(core, current_posx, current_posy, current_Z, judge=0):

    core.set_xy_position(current_posx, current_posy)
    core.set_position('ZStage', current_Z)
    if judge:
        core.wait_for_device("XYStage")
        core.wait_for_device("ZStage")
