# utils.py
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt

# Reading quantile from a csv file
def print_met_quantile(csv_file='', cols=0, quants=None):
    if quants is None:
        quants = [0, 0.5, 0.95]
    data = np.loadtxt(csv_file, delimiter=',')
    data = data[:, cols]
    for i in range(len(quants)):
        quants[i] *= 100
    print(np.percentile(data, quants, axis=0, method='nearest'))


# Generating vkern parameters according to input distribution
# print:
# S = , N =, I =, NI =
def gen_vkern(arr=np.zeros(0), test_per_bin=10000, bin_gap=10, tocy=1, cuts=(0,0)):
    arr = arr * tocy
    lower_bound = np.percentile(arr, cuts[0] * 100, method='nearest')
    upper_bound = np.percentile(arr, cuts[1] * 100, method='nearest')
    data_cut = arr[(arr >= lower_bound) & (arr <= upper_bound)]
    S = math.floor(data_cut.min() / 2)
    N = int(test_per_bin)
    I = math.floor(bin_gap / 2)
    NI = math.ceil((data_cut.max() - data_cut.min()) / bin_gap)
    print("S = {}, N = {}, I = {}, NI = {}".format(S, N, I, NI))


# calc_wasserstein
# Calculating Wasserstein distance of multiple distribution
def calc_wasserstein(cdf1=np.zeros(0), cdf2=np.zeros(0), splits=[]):
    if type(splits) is int:
        wds = np.sum(np.absolute(cdf2-cdf1)) / splits
    elif type(splits) is list:
        nsplit = np.max(splits)
        wds = list()
        gap = np.absolute(cdf2-cdf1)
        for s in splits:
            wds.append(np.sum(gap[0:s+1]) / nsplit)
    else:
        wds = None
    return wds

def filt_draw_cdf(files='', cols=1, splits=1000):
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(16, 10), dpi=150)
    ax.scatter(x=[1,2,3], y=[1,2,3])

    return fig, ax


def filt_draw_wasserstein():
    pass


# raw_to_bin
# converting an 1D raw measurement results array to a rounded histogram
# input:
#   - arr[=np.zeros(0)]: 1D np array, example: [4512.23, 3132.13, 2423.12]
#   - roundto[=10]: round to 1, 10, 100 ...
# return:
#   - an ascending 2D histo array, example: [[2420, 0.33333], [[3130, 0.33333]], [4510, 0.3333]]
def raw_to_bin(arr=np.zeros(0), roundto=10):
    if type(arr) is not np.array and type(arr) is not np.ndarray:
        raise TypeError("Type error:  arr[=np.zeros(0)]: 1D np array, example: [4512.23, 3132.13, 2423.12]")
    if np.ndim(arr) != 1:
        raise TypeError("Type error:  arr[=np.zeros(0)]: 1D np array, example: [4512.23, 3132.13, 2423.12]")
    if len(arr) == 0:
        raise ValueError("arr can not be empty.")
    # Rounding and sorting
    round_arr = np.round(arr / roundto) * roundto
    round_arr.sort()
    tot_count = len(round_arr)
    bins, counts = np.unique(round_arr, return_counts=True)
    counts = counts / tot_count

    return np.array([bins, counts]).T


# bin_to_cdf
# Converting
def bin_to_cdf(arr=np.zeros(0), splits=100):
    cdfs = np.zeros(splits+1)
    p = 0
    step = 1 / splits
    ibin = 0
    probs = np.cumsum(arr[:, 1])
    for p in range(0, splits):
        while p*step > probs[ibin]:
            ibin += 1
        cdfs[p] = arr[ibin, 0]
    cdfs[splits] = arr[-1, 0]

    return cdfs

# raw_to_cdf
def raw_to_cdf(arr=np.zeros(0), splits=100):
    cdfs = np.zeros(splits + 1)
    sorted_arr = np.sort(arr, axis=0)
    arrlen = len(sorted_arr)
    step = 1 / splits
    for p in range(0, splits):
        iarr = int(np.round(p * step * arrlen))
        cdfs[p] = sorted_arr[iarr]
    cdfs[splits] = sorted_arr[-1]

    return cdfs


# gen_pareto
def gen_pareto(alpha=1, nins_s=10000, nins_e=40000, ntest=10000, ofile=''):
    # generating samples
    rarr = (np.random.pareto(alpha, ntest) + 1) * nins_s
    # cutoff
    rarr = rarr[rarr < nins_e]
    # fill the ntest
    while rarr.size < ntest:
        r = (np.random.pareto(5, 1) + 1) * nins_s
        if r <= nins_e:
            rarr = np.append(rarr, (np.random.pareto(5, 1) + 1) * nins_s)
    rarr=np.round_(rarr, 0)
    rarr_cdf = raw_to_cdf(rarr, 1000)
    # drawing distribution
    fig, ax = plt.subplots(1, 1, figsize=(10, 6), dpi=150)
    ax.scatter(x=range(0, 1001), y=rarr_cdf, s=1)
    ax.set_ylim(nins_s - (nins_e - nins_s) / 6, nins_e + (nins_e - nins_s) / 6)
    if len(ofile):
        df = pd.DataFrame(rarr)
        df.to_csv(ofile, header=False, index=False)
    else:
        print(rarr)