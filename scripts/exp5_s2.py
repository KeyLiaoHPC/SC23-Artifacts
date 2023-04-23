import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import sys
sys.path.append("..")
import filt

freq=2.49414

base_time_list = [i for i in np.arange(0.1, 0.99, 0.1)] + [i for i in np.arange(1, 10, 1)] + [i for i in np.arange(10, 101, 10)]# us
timing_methods = ['PAPI', 'STiming']
distro_list = ['norm-s0.015', 'pareto-b26']

def plot_wd_trend(ifig, in_er_list=list(), in_ep_list=list(), in_wd_met=list(), in_wd_ntf=list(), in_wd90_met=list(), in_wd90_ntf=list()):
    # Plotting
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = 'cambria'
    mpl.rcParams['font.size'] = '14'
    mpl.rc('font', weight='bold')
    font_path = 'C:/Windows/Fonts/cambria.ttc'  # Cambria
    font_prop = fm.FontProperties(fname=font_path, size=14)
    colors = ['blue', 'green']
    fig, axs = plt.subplots(2, 1, figsize=(8, 4), dpi=300, sharex=True, gridspec_kw={'height_ratios': [3, 1]})
    fig.subplots_adjust(hspace=0.05)
    er_list = list()
    ep_list = list()
    for i in range(0, len(in_er_list)):
        if in_er_list[i] <= 0.001:
            er_list.append(0.001)
        else:
            er_list.append(in_er_list[i])
        if in_ep_list[i] <= 0.01:
            ep_list.append(0.01)
        else:
            ep_list.append(in_ep_list[i])

    axs[0].plot(base_time_list, np.array(in_wd_met) / 1000, ls='--', color='blue', lw=2, ms=8, marker='x',
                fillstyle='none')
    axs[0].plot(base_time_list, np.array(in_wd_ntf) / 1000, ls='--', color='green', lw=2, ms=8, marker='x',
                fillstyle='none')
    axs[0].plot(base_time_list, np.array(in_wd90_met) / 1000, lw=0, ls='--', color='blue', ms=8, marker='.',
                fillstyle='none')
    axs[0].plot(base_time_list, np.array(in_wd90_ntf) / 1000, lw=0, ls='--', color='green', ms=8, marker='.',
                fillstyle='none')
    axs[1].plot(base_time_list, er_list, ls='--', color='red', lw=2, ms=8, marker='x', fillstyle='none')
    axs1_alt = axs[1].twinx()
    axs1_alt.plot(base_time_list, ep_list, ls='--', color='darkorange', lw=2, ms=8, marker='x', fillstyle='none')

    axs[1].yaxis.grid(True, which='major', ls='dotted', color='grey')
    axs[1].set_ylim(0.0001, 0.06)
    axs[1].set_yscale('log')
    axs[1].set_yticks([0.001, 0.01], ['≤0.001', 0.01])
    axs[1].grid(True, ls='dotted', color='grey')
    axs[1].axhline(y=0.01, c='black', lw=2, ls='dashdot')
    axs1_alt.set_ylim(0.001, 0.6)
    axs1_alt.set_yscale('log')
    axs1_alt.set_yticks([0.01, 0.1], ['≤0.01', 0.1])

    ax = axs[0]
    ax.yaxis.grid(True, which='major', ls='dotted', color='grey')
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.xaxis.set_major_formatter(mpl.ticker.ScalarFormatter())
    # ax.yaxis.set_major_formatter(mpl.ticker.ScalarFormatter())
    # ax.set_ylim(0.1, 12)
    ax.tick_params(direction='in')
    ax.grid(True, ls='dotted', color='grey')
    ax.set_ylim(0.0004, 10)
    ax.set_yticks([0.01, 0.1, 1, 10], [0.01, 0.1, 1, 10])
    fig.savefig('exp5_' + str(ifig) + '.png', bbox_inches='tight')

ps_candidate = [0.05, 0.1, 0.2]
ifig = 0
# sc1-S625+25x6-INIT+6MiBx40-PAPI.csv
# 存放MetResult
for distro in distro_list:
    pareto_results_list = list()
    pareto_denoise_cdf_list = list()
    pareto_stiming_ep_list = list()
    pareto_stiming_er_list = list()
    pareto_papi_ep_list = list()
    pareto_papi_er_list = list()

    for base_time in base_time_list:
        if base_time < 1:
            base_time = np.round(base_time, 1)
        else:
            base_time = np.round(base_time, 0)
        for tm in timing_methods:
            tm_file = './exp5_data/exp5-' + distro + '-' + str(base_time) + 'us-' + tm + '.csv'
            # df = pd.read_csv(tm_file, header=None)
            # Reading theoretical time
            df = pd.read_csv(tm_file, header=None)
            arr0 = df[1].to_numpy() * 2 / 2.5
            cdf0 = filt.raw_to_cdf(arr0, 1000)
            if tm == 'STiming':
                tick = freq
            else:
                tick = 1
            nvk = base_time * 1000 * 2.5 / 2
            tv_file = './exp5_data/exp5-' + distro + '-' + str(base_time)  + 'us-' + tm + '-sample.csv'
            test_mes = filt.MetResult(met_file=tm_file, col_id=2, freq_ghz=2.5, tick_ghz=tick)
            lost_wd_min = 0x7fffffff - 1
            denoise_bins_candidate = list()
            # Denoise using different start probability of noise
            for ps in ps_candidate:
                denoise_bins, residual, lost_wd = test_mes.filt(tnoise_file=tv_file, col=2, vkern_count=nvk, roundto=5, met_pl=0.001, met_ps=0.001, tf_pl=0.001, tf_ps=ps, mix=True)
                denoise_bins_candidate.append((ps, denoise_bins, residual, lost_wd))
            # Picking denoise cdf with the lowest restore error
            denoise_result = min(denoise_bins_candidate, key=lambda x: x[3])
            ps = denoise_result[0]
            denoise_bins = denoise_result[1]
            residual = denoise_result[2]
            lost_wd = denoise_result[3]
            er = lost_wd/np.mean(test_mes.met_arr)
            if tm == 'STiming':
                pareto_stiming_ep_list.append(residual)
                pareto_stiming_er_list.append(er)
            else:
                pareto_papi_ep_list.append(residual)
                pareto_papi_er_list.append(er)
            print(base_time, tm, 'ps=%f,eP=%.4f,eR=%.6f'% (ps, residual, er))
            denoise_cdf = filt.bin_to_cdf(np.array(denoise_bins), 1000)
            pareto_denoise_cdf_list.append(denoise_cdf)
            pareto_results_list.append(test_mes)
    # Calculating W-metric
    pareto_wd_met_papi = list()
    pareto_wd_ntf_papi = list()
    pareto_wd_met_stiming = list()
    pareto_wd_ntf_stiming = list()
    pareto_wd90_met_papi = list()
    pareto_wd90_ntf_papi = list()
    pareto_wd90_met_stiming = list()
    pareto_wd90_ntf_stiming = list()
    # sc1-S625+25x6-INIT+6MiBx40-PAPI.csv
    # 存放MetResult
    for i in range(0, len(base_time_list)):
        base_time = base_time_list[i]
        if base_time < 1:
            base_time = np.round(base_time, 1)
        else:
            base_time = np.round(base_time, 0)
        tm = 'PAPI'
        tm_file = './exp5_data/exp5-' + distro + '-' + str(base_time) + 'us-' + tm + '.csv'
        cdf0 = filt.raw_to_cdf(pd.read_csv(tm_file, header=None)[1].to_numpy() * 2 / 2.5, 1000)
        met_cdf = filt.raw_to_cdf(pareto_results_list[i * 2].met_arr, 1000)
        # denoise_cdf = filt.bin_to_cdf(results_list[i*2].denoise_arr, 1000)
        [w0_90, w0] = filt.calc_wasserstein(met_cdf, cdf0, [900, 999, 1000])[0:2]
        [w1_90, w1] = filt.calc_wasserstein(pareto_denoise_cdf_list[i * 2], cdf0, [900, 999, 1000])[0:2]
        w0_90 = w0 - w0_90
        w1_90 = w1 - w1_90
        print(i, base_time, 'PAPI, w-metric:', w0, w1, 'w90:', w0_90, w1_90)
        pareto_wd_met_papi.append(w0)
        pareto_wd_ntf_papi.append(w1)
        pareto_wd90_met_papi.append(w0_90)
        pareto_wd90_ntf_papi.append(w1_90)
        met_cdf = filt.raw_to_cdf(pareto_results_list[i * 2 + 1].met_arr, 1000)
        # denoise_cdf = filt.bin_to_cdf(results_list[i*2+1].denoise_arr, 1000)
        [w0_90, w0] = filt.calc_wasserstein(met_cdf, cdf0, [900, 999, 1000])[0:2]
        [w1_90, w1] = filt.calc_wasserstein(pareto_denoise_cdf_list[i * 2 + 1], cdf0, [900, 999, 1000])[0:2]
        w0_90 = w0 - w0_90
        w1_90 = w1 - w1_90
        print(i, base_time, 'STiming, w_raw=', w0, 'w_filtered=', w1, 'w90_raw=', w0_90, 'w90_filtered=', w1_90)
        pareto_wd_met_stiming.append(w0)
        pareto_wd_ntf_stiming.append(w1)
        pareto_wd90_met_stiming.append(w0_90)
        pareto_wd90_ntf_stiming.append(w1_90)
    plot_wd_trend(ifig, pareto_papi_er_list, pareto_papi_ep_list, pareto_wd_met_papi, pareto_wd_ntf_papi,
                  pareto_wd90_met_papi, pareto_wd90_ntf_papi)
    ifig += 1
    plot_wd_trend(ifig, pareto_stiming_er_list, pareto_stiming_ep_list, pareto_wd_met_stiming, pareto_wd_ntf_stiming,
                  pareto_wd90_met_stiming, pareto_wd90_ntf_stiming)
    ifig += 1

