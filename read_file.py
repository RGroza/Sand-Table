from os import listdir
from os.path import isfile, join

def get_files(mypath):
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    print("Files found: " + str(onlyfiles).replace('[', '').replace(']', ''))

    return onlyfiles

def get_coordinates(filename, mypath):
    with open(mypath + filename, "r") as f:
        content = f.readlines()

    lines = [line.rstrip('\n') for line in content]

    coor = []
    for c in lines:
        coor.append((int(c[:c.find(" ")]), int(c[c.find(" ")+1:])))

    return coor

mypath = "files/"
files = get_files(mypath)
for f in files:
    coor = get_coordinates(f, mypath)
    print(f + ": " + str(coor))