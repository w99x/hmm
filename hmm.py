import numpy as np
import matplotlib.pyplot as plt
import re
from scipy.signal import argrelextrema

def read_and_prepare(filenames):
    data_arrays = []
    maxtime = 0
    for filename in filenames:
        data_array = np.array(map(lambda l: map(float, filter(lambda x: len(x) > 0, re.split('\\s+', l))), open(filename))).T
        data_array[0, :] += maxtime
        maxtime = np.max(data_array[0, :])
        data_arrays.append(data_array)
    concated = np.concatenate(data_arrays, axis=1)
    return concated[0,:], concated[1:,:]

def get_pattern(patternfilename):
    pattern_data = np.array(
        map(lambda l: map(float, filter(lambda x: len(x) > 0, re.split('\\s+', l))), open(patternfilename))).T
    pattern_t, pattern = pattern_data[0, :], pattern_data[1:, :]
    pattern_t -= pattern_t[0]
    return pattern_t, pattern

def get_chars(np_marray):
    minimumsidx = argrelextrema(np_marray, np.less)
    maximumsidx = argrelextrema(np_marray, np.greater)

    def get_vals_by_idx(idxs):
        return [np_marray[x] for x in idxs]

    minimums = get_vals_by_idx(minimumsidx[0])
    maximums = get_vals_by_idx(maximumsidx[0])
    if len(maximums) == 0 or len(minimums) == 0:
        return None

    minmax = np.max(minimums)
    minmin = np.min(minimums)

    maxmin = np.min(maximums)
    maxmax = np.max(maximums)

    maxmax -= minmin
    maxmin -= minmin
    minmin -= maxmax
    minmax -= maxmax
    maxratio = maxmax / maxmin
    minratio = minmin / minmax


    std = np.std(np_marray)
    var = np.var(np_marray)

    return [std, var]


def filter_extr_plain_draw(distances, values, threshold=0.8):
    extr = argrelextrema(np.array(distances), np.less)
    extrvals = extr[0]

    def filter_extr_plain(extrspos, values, threshold=threshold):
        filtered = [[values[extrspos[0]], None]]
        for i in range(len(extrvals) - 1):
            last = filtered[-1][0]
            if (values[extrspos[i + 1]] - last >= threshold):
                filtered[-1][-1] = values[extrvals[i+1]]
                filtered.append([values[extrvals[i+1]], None])
        return reduce(lambda res, x: res + x, filtered, [])

    return filter_extr_plain(extrvals, values)

from scipy.spatial.distance import euclidean
from fastdtw import fastdtw

def get_dtw_in_window(window, patterns):
    pattern_len = len(patterns[0])
    windows_len = len(window[0])
    distances = []
    for i in range(windows_len - pattern_len - 1):
        datawin = window[:, i:pattern_len + i]
        distance, path = fastdtw(patterns, datawin, dist=euclidean)
        print(distance, path)
        distances.append(distance)
    return distances

def filter_extr(distances, window_t, window_s, signal_len):
    founds_pos = []

    dtw_mins = argrelextrema(np.array(distances), np.less)[0]
    for dtw_min in dtw_mins:
        time = window_t[dtw_min]
        signal = window_s[:, dtw_min:dtw_min + signal_len]

        sig_chars = [get_chars(s) for s in signal]

        if all(sig_chars):
            sig_chars_map = dict(zip(fh_loop_character_filter_map.keys(), sig_chars))
        else:
            continue

        coeff = 1.2
        positive = 0
        for k in sig_chars_map.keys():
            if abs(sig_chars_map[k][0]*coeff) >= abs(fh_loop_character_filter_map[k][0]):
                positive += 1
                #if abs(sig_chars_map[k][1] * coeff) >= abs(fh_loop_character_filter_map[k][1]):
                #    positive += 1

        if positive >= len(sig_chars_map):
            founds_pos.append(time)
    return founds_pos

def draw_signals(filteredt, datat, datas, signal_size=10):
    minmaxdist = [[-50, 100]] * len(filteredt)

    plt.figure()
    plt.plot(range(len(distances)), distances)
    plt.grid()

    plt.figure()
    newdatasarr = reduce(lambda res, x: res + [datat, x], datas, [])
    plt.plot(*newdatasarr)
    for i in range(len(filteredt)):
        plt.plot([filteredt[i], filteredt[i]], minmaxdist[i], '-r')
        plt.plot([filteredt[i] + 0.1*signal_size, filteredt[i] + 0.1*signal_size], minmaxdist[i], '-g')

    plt.grid()

def draw_patterns(time, sig):
    for pat in sig:
        plt.figure()
        plt.plot(time, pat)
        plt.grid()

fh_loop_character_filter_map = {
        0:[3.5, 1.5], #x
        #1:[3.5, 1.3], #y
        #4:[1.5, 2], #y
        #5:[9, 1.2] #z
    }

significant_coords = fh_loop_character_filter_map.keys()

pattern_t, pattern = get_pattern("pattern.csv")
pattern = pattern[np.r_[significant_coords]]

#pattern_stas_t, pattern_stas = get_pattern("pattern_stas.csv")
#pattern_stas = pattern_stas[np.r_[significant_coords]]

fh_loop_character_filter_map = dict(zip(significant_coords, [get_chars(p) for p in pattern]))

draw_patterns(pattern_t, pattern)
#draw_patterns(pattern_stas_t, pattern_stas)

newdatat, newdatas = read_and_prepare([#'merged.csv',
                                       #'iracsv/merged.csv',
                                       #'stasdrivecsv/merged.csv',
                                       'stasloopcsv/merged.csv'
                                       ])

newdatas = newdatas[np.r_[significant_coords]]

distances = get_dtw_in_window(newdatas, pattern)
#filteredt = filter_extr_plain_draw(distances, newdatat)
filteredt = filter_extr(distances, newdatat, newdatas, len(pattern_t))
draw_signals(filteredt, newdatat, newdatas, signal_size=len(pattern_t))

dtw_mins = argrelextrema(np.array(distances), np.less)[0]
draw_signals(newdatat[np.r_[dtw_mins]], newdatat, newdatas, signal_size=len(pattern_t))

plt.show()
raw_input()