import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import sys
sys.path.append("../")
import filt

freq=2.49414

# 单一图
id = 0
for size in [256, 4000]:
    split = 100
    step = 1
    timing_methods = ['PAPI', 'STiming']
    # 存放MetResult
    met_list = list()
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = 'cambria'
    mpl.rcParams['font.size'] = '16'
    for tm in timing_methods:
        tm_file = './exp1_data/TL_CALC_W-C' + str(size) + '-' + tm + '.csv'
        df = pd.read_csv(tm_file, header=None)
        med = df[1].min()
        if tm == 'STiming':
            tick = freq
        else:
            tick = 1
        nvk = med / tick * 2.5 / 2
        tv_file = './exp1_data/TL_CALC_W-C' + str(size) + '-' + str(int(nvk)) + 'x40-' + tm + '-tfsample.csv'
        test_mes = filt.MetResult(met_file=tm_file, col_id=1, freq_ghz=2.5, tick_ghz=tick)
        met_list.append(test_mes)
    cdf_met_papi = filt.raw_to_cdf(met_list[0].met_arr, split) / 1000
    cdf_met_stiming = filt.raw_to_cdf(met_list[1].met_arr, split) / 1000
    diff_papi_to_ns = cdf_met_papi - cdf_met_stiming

    fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(15,5), dpi=300, sharex=True, gridspec_kw={'height_ratios': [3, 2]})
    fig.subplots_adjust(hspace=0.05)
    ax[0].plot([i for i in range(0, split, step)], cdf_met_papi[0:split:step], ms=10, lw=2, ls='--', color='blue', marker='x')
    ax[0].plot([i for i in range(0, split, step)], cdf_met_stiming[0:split:step], ms=10, lw=2, ls='--', color='green', marker='+')
    ax[1].plot([i for i in range(0, split, step)], diff_papi_to_ns[0:split:step], ms=10, lw=2, ls='--', marker='x', color='black')
    ax[1].xaxis.set_ticks([i for i in range(0,split+1,10)])

    # ax[0].set_ylim(75000, 10000)
    gap_max, gap_min = np.max(cdf_met_papi[0:split:step]), np.min(cdf_met_stiming[0:split:step])
    gap_division = (gap_max - gap_min) / 4
    tick_min = gap_min - gap_division
    tick_max = gap_max + gap_division
    ax[0].tick_params(direction='in')
    ax[0].xaxis.tick_top()
    ax[0].set_ylim(tick_min,tick_max)

    ax[1].xaxis.tick_bottom()
    ax[1].tick_params(direction='in')
    # ax[0].axvline(50, color='red', ls='--', lw=0.5)
    ax[0].grid(True, ls='--', color='grey', lw=0.6)
    # ax[1].axvline(50, color='red', ls='--', lw=0.5)
    ax[1].grid(True, ls='--', color='grey', lw=0.6)
    gap_max, gap_min = np.max(diff_papi_to_ns[0:split:step]), np.min(diff_papi_to_ns[0:split:step])
    gap_division = (gap_max - gap_min) / 4
    tick_min = gap_min - gap_division
    tick_max = gap_max + gap_division * 1.5
    ax[1].set_ylim(tick_min, tick_max)
    for axis in ['top', 'bottom', 'left', 'right']:
        ax[0].spines[axis].set_linewidth(1.5)
        ax[1].spines[axis].set_linewidth(1.5)

    fig.savefig('exp1_'+ str(id) + '.png', dpi=300, bbox_inches='tight')
    id += 1