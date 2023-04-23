import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import sys
sys.path.append("..")
import filt

freq = 2.49414

narr_list = [64, 80, 128, 160, 256, 500, 512, 1000, 1024, 2000, 2048, 4000, 4096, 6000, 8000]
timing_methods = ['PAPI', 'STiming']
ps_candidate = [0.05, 0.1, 0.2]
# 存放MetResult
results_list = list()
denoise_cdf_list = list()
for size in narr_list:
    for tm in timing_methods:
        tm_file = './exp6_data/TL_CALC_W-C' + str(size) + '-' + tm + '.csv'
        df = pd.read_csv(tm_file, header=None)
        if tm == 'STiming':
            tick = freq
        else:
            tick = 1
        tv_file = './exp6_data/TL_CALC_W-C' + str(size) + '-'  + tm + '-sample.csv'
        df = pd.read_csv(tv_file, header=None)
        nvk = df[1][0]
        test_mes = filt.MetResult(met_file=tm_file, col_id=1, freq_ghz=2.5, tick_ghz=tick)
        lost_wd_min = 0x7fffffff - 1
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
        cdf_met = filt.raw_to_cdf(test_mes.met_arr, 1000)
        denoise_cdf = filt.bin_to_cdf(np.array(denoise_bins), 1000)
        # wf = filt.calc_wasserstein(cdf_met, denoise_cdf, [999, 1000])[0]
        print(size, tm, 'ps=%f,eP=%.4f,eR=%.6f'% (ps, residual, lost_wd/np.mean(test_mes.met_arr)))
        denoise_cdf_list.append(denoise_cdf)
        results_list.append(test_mes)
# Print W-metric
for i in range(0, 30, 2):
    cdf_met_papi = filt.raw_to_cdf(results_list[i].met_arr, 1000)
    cdf_met_stiming = filt.raw_to_cdf(results_list[i+1].met_arr, 1000)
    # cdf_ntf_papi = filt.bin_to_cdf(results_list[i].denoise_arr, 1000)
    # cdf_ntf_stiming = filt.bin_to_cdf(results_list[i+1].denoise_arr, 1000)
    wd_met = filt.calc_wasserstein(cdf_met_papi, cdf_met_stiming, [999, 1000])[0]
    wd_ntf = filt.calc_wasserstein(denoise_cdf_list[i], denoise_cdf_list[i+1], [999, 1000])[0]
    print('wd_raw=', wd_met, 'wd_filtered=', wd_ntf)

# Plotting
fig, axs = plt.subplots(3, 5, figsize=(18,6), dpi=200)
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.serif'] = 'cambria'
mpl.rcParams['font.size'] = '12'
mpl.rcParams['xtick.major.pad']='2'
mpl.rcParams['ytick.major.pad']='2'
step = 20
ms=3
imax = 995
for i in range(0, 30, 2):
    fig_x = int(i / 2 / 5)
    fig_y = int(i / 2 % 5)
    ax = axs[fig_x][fig_y]
    cdf_met_papi = filt.raw_to_cdf(results_list[i].met_arr, 1000)
    cdf_met_stiming = filt.raw_to_cdf(results_list[i+1].met_arr, 1000)
    cdf_ntf_papi = denoise_cdf_list[i]
    cdf_ntf_stiming = denoise_cdf_list[i+1]
    # cdf_ntf_papi = filt.bin_to_cdf(results_list[i].denoise_arr, 1000)
    # cdf_ntf_stiming = filt.bin_to_cdf(results_list[i+1].denoise_arr, 1000)
    xarr= [i/10 for i in range(0, imax, step)]
    xarr.append(imax/10)
    yarr = cdf_met_papi[:imax:step]/1000
    yarr = np.append(yarr, cdf_met_papi[imax]/1000)
    ax.plot(xarr, yarr, ms=ms, lw=0.5, ls='-', marker='.', fillstyle='none', color='red')

    yarr = cdf_ntf_papi[:imax:step]/1000
    yarr = np.append(yarr, cdf_ntf_papi[imax]/1000)
    ax.plot(xarr, yarr, ms=ms, lw=0.5, ls='-', marker='.', fillstyle='none', color='blue')

    yarr = cdf_met_stiming[:imax:step]/1000
    yarr = np.append(yarr, cdf_met_stiming[imax]/1000)
    ax.plot(xarr, yarr, ms=ms, lw=0.5, ls='-', marker='.', fillstyle='none', color='darkorange')

    yarr = cdf_ntf_stiming[:imax:step]/1000
    yarr = np.append(yarr,cdf_ntf_stiming[imax]/1000)
    ax.plot(xarr, yarr, ms=ms, lw=0.5, ls='-', marker='.', fillstyle='none', color='green')
    # ax.plot([i/10 for i in range(0, imax, step)], cdf_met_papi[:imax:step]/1000, ms=ms, lw=0.5, ls='-', marker='.', fillstyle='none', color='red')
    # ax.plot([i/10 for i in range(0, imax, step)], cdf_ntf_papi[:imax:step]/1000, ms=ms, lw=0.5, ls='-', marker='.', fillstyle='none', color='blue')
    # ax.plot([i/10 for i in range(0, imax, step)], cdf_met_stiming[:imax:step]/1000, ms=ms, lw=0.5, ls='-', marker='.', fillstyle='none', color='orange')
    # ax.plot([i/10 for i in range(0, imax, step)], cdf_ntf_stiming[:imax:step]/1000, ms=ms, lw=0.5, ls='-', marker='.', fillstyle='none', color='green')
    # ymin = np.min([cdf_met_papi, cdf_met_stiming, cdf_ntf_papi, cdf_ntf_stiming]) / 1000 * 0.98
    # ymax = np.quantile([cdf_met_papi, cdf_met_stiming, cdf_ntf_papi, cdf_ntf_stiming], 0.98) / 1000 * 1.01
    narr = narr_list[int(i/2)]
    ax.text(x=0.05, y=0.9, s=str(narr)+'x'+str(narr), transform=axs[fig_x][fig_y].transAxes, horizontalalignment='left')
    # ax.set_yscale('log')
    ax.grid(which='major', axis='x', color='black', linestyle='dotted', linewidth=0.5)
    ax.grid(which='major', axis='y', color='black', linestyle='dotted', linewidth=0.5)
plt.subplots_adjust(hspace=0.2, wspace=0.15)
fig.savefig('exp6_0.png', bbox_inches='tight')

from matplotlib.ticker import NullFormatter, NullLocator

narr_list = [64, 80, 128, 160, 256, 500, 512, 1000, 1024, 2000, 2048, 4000, 4096, 6000, 8000]#, 8192]
papi_met_basetime = np.mean(results_list[0].met_arr)
papi_ntf_basetime = np.mean(results_list[0].met_arr)
papi_met_gridtime = list()
papi_ntf_gridtime = list()
stiming_met_gridtime = list()
stiming_ntf_gridtime = list()
# Calculating run time for each grid
for i in range(0, 30, 2):
    narr = narr_list[int(i/2)]
    papi_met_gridtime.append(np.mean(results_list[i].met_arr) / narr)
    wavg = np.sum(denoise_cdf_list[i]) / 1000
    # for j in range(0, len(results_list[i].denoise_arr)):
        # wavg += results_list[i].denoise_arr[j, 0] * results_list[i].denoise_arr[j, 1]
    papi_ntf_gridtime.append(wavg / narr)
    stiming_met_gridtime.append(np.mean(results_list[i+1].met_arr) / narr)
    wavg = np.sum(denoise_cdf_list[i+1]) / 1000
    # for j in range(0, len(results_list[i+1].denoise_arr)):
    #     wavg += results_list[i+1].denoise_arr[j, 0] * results_list[i+1].denoise_arr[j, 1]
    stiming_ntf_gridtime.append(wavg / narr)
fig, ax = plt.subplots(2, 1, figsize=(10,4), dpi=300, sharex=True)
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.serif'] = 'cambria'
mpl.rcParams['font.size'] = '14'
ax[0].plot(narr_list, papi_met_gridtime, lw=1, marker='x', ls='--', color='red')
ax[0].plot(narr_list, papi_ntf_gridtime, lw=1, marker='x', ls='--', color='blue')
ax[0].plot(narr_list, stiming_met_gridtime, lw=1, marker='x', ls='--', color='orange')
ax[0].plot(narr_list, stiming_ntf_gridtime, lw=1, marker='x', ls='--', color='green')
ax[0].set_ylim(8, 15)
ax[0].set_yticks([i for i in range(9, 16, 2)], [i for i in range(9, 16, 2)])
ax[1].plot(narr_list, 1 / (np.array(papi_met_gridtime) / papi_met_gridtime[0]), lw=1, marker='x', ls='--', color='red')
ax[1].plot(narr_list, 1 / (np.array(papi_ntf_gridtime) / papi_ntf_gridtime[0]), lw=1, marker='x', ls='--', color='blue')
ax[1].plot(narr_list, 1 / (np.array(stiming_met_gridtime) / stiming_met_gridtime[0]), lw=1, marker='x', ls='--', color='orange')
ax[1].plot(narr_list, 1 / (np.array(stiming_ntf_gridtime) / stiming_ntf_gridtime[0]), lw=1, marker='x', ls='--', color='green')
ax[1].set_ylim(0.5, 1.5)
ax[1].set_yticks([i for i in np.arange(0.6, 1.6, 0.2)], [0.6, 0.8, 1.0, 1.2, 1.4])
ax[0].set_xscale('log')
ax[1].set_xscale('log')
ax[0].xaxis.set_minor_formatter(NullFormatter())
ax[0].xaxis.set_major_formatter(NullFormatter())
ax[0].xaxis.set_minor_locator(NullLocator())
ax[0].xaxis.set_major_locator(NullLocator())
ax[0].set_xticks([64, 128, 256, 512, 1024, 2048, 4096, 8000], [64, 128, 256, 512, 1024, 2048, 4096, 8000])
ax[0].grid(which='major', axis='x', color='black', linestyle='dotted', linewidth=0.5)
ax[0].grid(which='major', axis='y', color='black', linestyle='dotted', linewidth=0.5)
ax[1].grid(which='major', axis='x', color='black', linestyle='dotted', linewidth=0.5)
ax[1].grid(which='major', axis='y', color='black', linestyle='dotted', linewidth=0.5)
plt.subplots_adjust(hspace=0)
fig.savefig('exp6_1.png', bbox_inches='tight')