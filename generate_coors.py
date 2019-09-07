from os import listdir
from os.path import isfile, join

def get_files(mypath):
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    print("Files found: " + str(onlyfiles).replace('[', '').replace(']', ''))

    return onlyfiles

def generate_coordinates(mypath, fileName, thetaStep, funcRange):
    theta = funcRange[0]

    #f=open("file{}.txt".format(str(num)))