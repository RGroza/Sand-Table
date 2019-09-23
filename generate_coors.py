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

# Generates coordinates that can be plotted by desmos
# mypath: location of file created
# file_name: name of file
# coor_amt: num of coor per rev
# revs: num of revs
# max_amp: max amplitude of the function
def plotting_coordinates(mypath, file_name, coor_amt, revs, max_amp):
    f = open(mypath + file_name, "w")

    rev_steps = 3200
    max_disp = max_amp
    currentTheta = 0 # theta coordinate val in steps
    theta_steps = round(rev_steps / coor_amt)

    for i in range(revs):
        for i in range(coor_amt):
            funcResult = round(max_disp * abs(math.cos(math.radians(360 * currentTheta / rev_steps)))) # r coordinate val

            f.write("\left(" + str(funcResult) + "\cos\left(" + str(round(360*(currentTheta / rev_steps), 1)) + "\\right),\ "
                             + str(funcResult) + "\sin\left(" + str(round(360*(currentTheta / rev_steps), 1)) +  "\\right)\\right)\n")

            currentTheta += theta_steps
        currentTheta = 0
    print("Done!")

#stepper_coordinates("files/", "testfile.txt", 100, 1)
plotting_coordinates("files/", "testfile.txt", 100, 1, 100)