from os import listdir
from os.path import isfile, join
import math

def get_files(mypath):
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    print("Files found: " + str(onlyfiles).replace('[', '').replace(']', ''))

    return onlyfiles

# Generates coordinates that are interpreted by the main program
def stepper_coordinates(mypath, file_name, coor_amt, revs):
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

def simple_square(deg, max_amp):
    if deg > 360:
        deg -= 360

    if deg >= 0 and deg < 45 or deg > 315 and deg <= 360:
        funcResult = round(max_amp / math.cos(math.radians(deg)))
    elif deg > 45 and deg < 135:
        funcResult = round(max_amp / math.sin(math.radians(deg)))
    elif deg > 135 and deg < 225:
        funcResult = round(-max_amp / math.cos(math.radians(deg)))
    else:
        funcResult = round(-max_amp / math.sin(math.radians(deg)))
    return funcResult

# def square_spiral(deg, max_amp, layers):
#     amp = max_amp
#     layer_sep = round(max_amp / layers)
#     for l in layers:
#         for n in range(3):

# Generates coordinates that can be plotted by desmos
# mypath: location of file created
# file_name: name of file
# coor_amt: num of coor per rev
# revs: num of revs
# max_amp: max amplitude of the function
def plotting_coordinates(mypath, file_name, coor_amt, revs, max_amp):
    f = open(mypath + file_name, "w")

    rev_steps = 3200 # default sand table mechanism setting for steps per rev
    currentTheta = 0 # theta coordinate val in steps
    theta_steps = round(rev_steps / coor_amt)

    for i in range(revs * coor_amt):
        deg = 360 * currentTheta / rev_steps
        funcResult = simple_square(deg, max_amp) # r coordinate val

        f.write("\left(" + str(funcResult) + "\cos\left(" + str(round((deg), 1)) + "\\right),\ "
                            + str(funcResult) + "\sin\left(" + str(round((deg), 1)) +  "\\right)\\right)\n")

        currentTheta += theta_steps
    print("Done!")

#stepper_coordinates("files/", "testfile.txt", 100, 1)
plotting_coordinates("files/", "testfile2.txt", 200, 2, 100)