import numpy as np

from os import listdir
from os.path import isfile, join


max_lin = 10000
microstep_size = 8


def get_files(folder):
    onlyfiles = [f for f in listdir(folder) if isfile(join(folder, f))]
    print("Tracks found: " + str(onlyfiles).replace('[', '').replace(']', ''))

    return onlyfiles


def get_coors(filename, folder):
    with open(folder + filename, "r") as f:
        content = f.readlines()

    lines = [line.rstrip('\n') for line in content]

    coors = np.array([0, 0])
    for c in lines:
        theta = float(c[:c.find(" ")])
        r = float(c[c.find(" ")+1:])

        if (theta != 0):
            theta = int(microstep_size * 3200 * theta)
            r = int(max_lin * r)
            coors = np.vstack((coors, [theta, r]))

    min_value = coors[1:, 0].min()
    coors[1:, 0] -= min_value

    return coors


def get_steps(filename, folder):
    coors = get_coors(filename, folder)

    return coors_to_steps(coors)


def coors_to_steps(coors):
    return coors[1:] - coors[:-1]


def add_delays(steps):

    min_delay = 0.00001

    delays = np.array([0, 0])
    for s in steps:
        if s[0] > s[1]:
            Rot_delay = round(s[0] * min_delay / s[1], 6) if s[1] != 0 else None
            Lin_delay = min_delay
        elif s[1] > s[0]:
            Rot_delay = min_delay
            Lin_delay = round(s[1] * min_delay / s[0], 6) if s[0] != 0 else None
        else:
            Rot_delay = min_delay
            Lin_delay = min_delay

        delays = np.vstack((delays, [Rot_delay, Lin_delay]))

    delays = delays[1:]
    steps_with_delays = np.concatenate((steps, delays), axis=1)

    return steps_with_delays


def process_tracks(folder="tracks/", debug=False):
    files = get_files(folder)
    tracks = []
    for f in files:
        steps = get_steps(f, folder)
        steps_with_delays = add_delays(steps)

        if debug:
            print(f + " steps:\n{}".format((steps[:29])))
            print(f + " steps_with_delays:\n{}".format((steps_with_delays[:29])))

        tracks.append(steps_with_delays)

    return tracks


if __name__ == '__main__':
    process_tracks(folder="../tracks/", debug=True)
