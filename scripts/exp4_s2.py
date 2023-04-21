import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import sys
sys.path.append("..")
import filt

freq=2.49414

nvk_list = [(625, 25), (6250, 250), (62500, 2500)]
timing_methods = ['PAPI', 'STiming']
ps_candidate = [0.05, 0.1, 0.2]
# sc1-S625+25x6-INIT+6MiBx40-PAPI.csv
# 存放MetResult
results_list = list()
denoise_cdf_list = list()
# Running FilT
ifig = 0
for nvk, interval in nvk_list:
    for tm in timing_methods:
        tm_file = './exp4_data/exp4-T' + str(nvk) + '-' + tm + '.csv'
        # df = pd.read_csv(tm_file, header=None)
        if tm == 'STiming':
            tick = freq
        else:
            tick = 1
        tv_file = './exp4_data/exp4-T' + str(nvk) + '-' + tm + '-sample.csv'
        test_mes = filt.MetResult(met_file=tm_file, col_id=2, freq_ghz=2.5, tick_ghz=tick)
        denoise_bins_candidate = list()
        for ps in ps_candidate:
            denoise_bins, residual, lost_wd = test_mes.filt(tnoise_file=tv_file, col=2, vkern_count=nvk, roundto=5, met_pl=0.001, met_ps=0.001, tf_pl=0.001, tf_ps=ps, mix=True)
            denoise_bins_candidate.append((ps, denoise_bins, residual, lost_wd))
        # Picking denoise cdf with the lowest restore error
        denoise_result = min(denoise_bins_candidate, key=lambda x: x[3])
        ps = denoise_result[0]
        denoise_bins = denoise_result[1]
        residual = denoise_result[2]
        lost_wd = denoise_result[3]
        print(nvk, tm, 'bin_p_st=', ps, 'ep=', residual, 'eR=', lost_wd/np.mean(test_mes.met_arr))
        denoise_cdf = filt.bin_to_cdf(np.array(denoise_bins), 1000)
        denoise_cdf_list.append(denoise_cdf)
        results_list.append(test_mes)
    # Plotting
    step = 10
    fig, ax = plt.subplots(1, 1, figsize=(10, 4), dpi=300)  # , gridspec_kw={'height_ratios': [1, 2, 3]})
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = 'cambria'
    mpl.rcParams['font.size'] = '16'
    cdf_met_papi = filt.raw_to_cdf(results_list[ifig * 2].met_arr, 1000)
    cdf_met_stiming = filt.raw_to_cdf(results_list[ifig * 2 + 1].met_arr, 1000)
    # cdf_ntf_papi = filt.bin_to_cdf(results_list[i*2].denoise_arr, 1000)
    # cdf_ntf_stiming = filt.bin_to_cdf(results_list[i*2+1].denoise_arr, 1000)
    tm_file = './exp4_data/exp4-T' + str(nvk) + '-STiming' + '.csv'
    ms = 4.5
    df = pd.read_csv(tm_file, header=None)
    arr0 = df[1].to_numpy() * 2 / 2.5
    cdf0 = filt.raw_to_cdf(arr0, 1000)
    ax.plot([i / 10 for i in range(0, 996, 5)], cdf0[0:996:5] / 1000, ms=2, color='black', lw=2, ls='--', marker=None)
    ax.plot([i / 10 for i in range(0, 996, step)], cdf_met_papi[0:996:step] / 1000, lw=0, ls='-', marker='x',
            fillstyle='none', ms=ms, color='red')
    ax.plot([i / 10 for i in range(0, 996, step)], denoise_cdf_list[ifig * 2][0:996:step] / 1000, lw=0, ls='-', marker='x',
            fillstyle='none', ms=ms, color='blue')
    ax.plot([i / 10 for i in range(0, 996, step)], cdf_met_stiming[0:996:step] / 1000, lw=0, ls='-', marker='^',
            fillstyle='none', ms=ms, color='orange')
    ax.plot([i / 10 for i in range(0, 996, step)], denoise_cdf_list[ifig * 2 + 1][0:996:step] / 1000, lw=0, ls='-',
            marker='^', fillstyle='none', ms=ms, color='green')

    w0 = filt.calc_wasserstein(cdf_met_papi, cdf0, [999, 1000])[0]
    w1 = filt.calc_wasserstein(denoise_cdf_list[ifig * 2], cdf0, [999, 1000])[0]
    w2 = filt.calc_wasserstein(cdf_met_stiming, cdf0, [999, 1000])[0]
    w3 = filt.calc_wasserstein(denoise_cdf_list[ifig * 2 + 1], cdf0, [999, 1000])[0]
    print('w_met_papi=', w0, 'w_filter_papi=', w1, 'w_met_stiming=', w2, 'w_filter_stiming=', w3)

    ax.tick_params(direction='in')
    ax.grid(True, which="both", ls='dotted', color='grey')
    ymin = np.min([denoise_cdf_list[ifig * 2], denoise_cdf_list[ifig * 2 + 1]]) * 0.99 / 1000
    ymax = np.quantile([denoise_cdf_list[ifig * 2], denoise_cdf_list[ifig * 2 + 1]], 0.999) / 1000
    ax.set_ylim(ymin, ymax)
    ax.tick_params(direction='in')
    ax.grid(True, which="both", ls='dotted', color='grey')
    ax.set_xlim(-5, 105)
    fig.savefig('exp4_' + str(ifig) + '.png', bbox_inches='tight')
    ifig += 1
