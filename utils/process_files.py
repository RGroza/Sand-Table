import numpy as np

from os import listdir
from os.path import isfile, join


max_lin = 15000
microstep_size = 8
Rot_delay_range = (0.01, 0.0001)
Lin_delay_range = (0.01, 0.0001)


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


def add_delays(steps):

    default_speed = 0.001
    max_speed = 0.0001

    delays = np.array([0, 0])
    for s in steps:
        elapsed_time = abs(s[0]) / default_speed
        if elapsed_time > 0 and abs(s[1]) / elapsed_time <= max_speed:
            Rot_delay = round(1 / default_speed, 8)
            Lin_delay = round(elapsed_time / abs(s[1]), 8) if s[1] != 0 else None
        else:
            min_time = abs(s[1]) / max_speed
            Rot_delay = round(min_time / abs(s[0]), 8) if s[0] != 0 else None
            Lin_delay = round(1 / max_speed, 8)

        delays = np.vstack((delays, [Rot_delay, Lin_delay]))

    delays = delays[1:]
    steps_with_delays = np.concatenate((steps, delays), axis=1)

    return steps_with_delays


def coors_to_steps(coors):
    return coors[1:] - coors[:-1]


def process_tracks(folder="tracks/", debug=False):
    files = get_files(folder)
    tracks = []
    for f in files:
        coors = get_coors(f, folder)
        steps = coors_to_steps(coors)
        steps_with_delays = add_delays(steps)

        if debug:
            print(f + " coors:\n{}".format((coors[:29])))
            print(f + " steps:\n{}".format((steps[:29])))

        tracks.append(steps_with_delays)

    return tracks


if __name__ == '__main__':
    process_tracks(folder="../tracks/", debug=True)