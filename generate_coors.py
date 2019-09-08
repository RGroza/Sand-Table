from os import listdir
from os.path import isfile, join
import math

def get_files(mypath):
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    print("Files found: " + str(onlyfiles).replace('[', '').replace(']', ''))

    return onlyfiles

def generate_coordinates(mypath, coor_amt, revs):
    f = open(mypath + "testfile.txt", "w")

    rev_steps = 3200
    arm_length = 1900
    currentTheta = 0
    theta_steps = round(revs * rev_steps / coor_amt)

    for i in range(coor_amt):
        funcResult = round(arm_length * abs(math.cos(math.radians(360 * currentTheta / rev_steps))))
        f.write(str(currentTheta) + " " + str(funcResult) + "\n")
        currentTheta += theta_steps
    print("Done!")

generate_coordinates("files/", 50, 3)