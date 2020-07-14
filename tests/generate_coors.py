from os import listdir
from os.path import isfile, join
import math

def get_files(mypath):
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    print("Files found: " + str(onlyfiles).replace('[', '').replace(']', ''))

    return onlyfiles

# Generates coordinates that are interpreted by the main program
def stepper_coors(mypath, file_name, coor_amt, revs):
    f = open(mypath + file_name, "w")

    rev_steps = 3200
    arm_length = 1900
    currentTheta = 0 # theta coordinate val in steps
    theta_steps = round(rev_steps / coor_amt)

    for i in range(revs * coor_amt):
        funcResult = round(arm_length * abs(math.cos(math.radians(360 * currentTheta / rev_steps)))) # r coordinate val
        f.write("(" + str(currentTheta) + ", " + str(funcResult) + ")\n")
        currentTheta += theta_steps
    print("Done!")

def simple_square(amp, theta):
    if theta > 360:
        theta -= 360

    if theta >= 0 and theta < 45 or theta > 315 and theta <= 360:
        funcResult = round(amp / math.cos(math.radians(theta)))
    elif theta > 45 and theta < 135:
        funcResult = round(amp / math.sin(math.radians(theta)))
    elif theta > 135 and theta < 225:
        funcResult = round(-amp / math.cos(math.radians(theta)))
    else:
        funcResult = round(-amp / math.sin(math.radians(theta)))
    return funcResult

def square_spiral(amp, theta, layers):
    rel_theta = theta % 360 # relative theta angle
    layer_sep = round(amp / layers)
    current_amp = layer_sep * math.trunc(theta / 360) + 1
    thresh_angle = 270 + math.atan(current_amp + layer_sep / current_amp) # bottom-right corner angle

    if rel_theta >= 0 and rel_theta < 45:
        funcResult = round(current_amp / math.cos(math.radians(rel_theta)))
    elif rel_theta >= 45 and rel_theta < 135:
        funcResult = round(current_amp / math.sin(math.radians(rel_theta)))
    elif rel_theta >= 135 and rel_theta < 225:
        funcResult = round(-current_amp / math.cos(math.radians(rel_theta)))
    elif rel_theta >= 225 and rel_theta < 270:
        funcResult = round(-current_amp / math.sin(math.radians(rel_theta)))
    elif rel_theta >= thresh_angle and rel_theta <= 360:
        funcResult = round(current_amp / math.cos(math.radians(rel_theta)))
    else:
        funcResult = round(-current_amp / math.sin(math.radians(rel_theta)))
    return funcResult

# Generates coordinates that can be plotted by desmos
# mypath: location of file created
# file_name: name of file
# coor_amt: num of coor per rev
# revs: num of revs
# max_amp: max amplitude of the function
def plotting_coors(mypath, file_name, coor_amt, max_amp, revs):
    f = open(mypath + file_name, "w")

    rev_steps = 3200 # default sand table mechanism setting for steps per rev
    currentTheta = 0 # theta coordinate val in steps
    theta_steps = round(rev_steps / coor_amt)

    for i in range(revs * coor_amt):
        deg = 360 * currentTheta / rev_steps
        funcResult = simple_square(max_amp, deg) # r coordinate val
        # funcResult = square_spiral(max_amp, deg, 100)

        f.write("\left(" + str(funcResult) + "\cos\left(" + str(round((deg), 1)) + "\\right),\ "
                            + str(funcResult) + "\sin\left(" + str(round((deg), 1)) +  "\\right)\\right)\n")

        currentTheta += theta_steps
    print("Done!")

#stepper_coors("files/", "testfile.txt", 100, 1)
plotting_coors("files/", "testfile.txt", 300, 100, 1)