def converter(core,  wjtn):


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