import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import sys
sys.path.append("..")
import filt

freq=2.49414

# Calculating W-metric
ind = np.concatenate((np.array([i for i in np.arange(0.1, 1, 0.1)]), np.array([i for i in range(1, 10)]), np.array([i for i in range(10, 101, 10)])))
width = 2       # the width of the bars

# plt.legend(labels=['Men' ,'Women' ,'Children'])
ibar=0
wd0_all = list()
wd1_all = list()
wd1p_all = list()
wd2_all = list()
wd2p_all = list()
print('t_base, t_mean, w-metric, w90-99.9(R90-99.9), w99-99.9(R99-99.9)')
for tm in ['PAPI', 'STiming']:
    for distro in ['norm-s0.015', 'pareto-b26']:
        print(tm, distro)
        wd0_list = list()
        wd1_list = list()
        wd1p_list = list()
        wd2_list = list()
        wd2p_list = list()
        for mean_us in ind:
            if mean_us < 1:
                mean_us = np.round(mean_us, 1)
            else:
                mean_us = int(mean_us)
            met_file = './exp3_data/sc2-'+distro+'-'+str(mean_us)+'us-' + tm + '.csv'
            df = pd.read_csv(met_file, header=None)
            if tm.find('STiming') > -1:
                arr = df[2].to_numpy() / freq
            else:
                arr = df[2].to_numpy()
            cdf = filt.raw_to_cdf(arr, 1000)
            arr0 = df[1].to_numpy() * 2 / 2.5
            cdf0 = filt.raw_to_cdf(arr0, 1000)
            wd = filt.calc_wasserstein(cdf, cdf0, [900, 990, 999, 1000])
            wd0 = wd[2]
            wd1 = wd0 - wd[0] # 90%~99.9%
            wd2 = wd0 - wd[1] # 99%~99.9%
            wd1p = wd1 / wd0
            wd2p = wd2 / wd0
            wd0_list.append(wd0)
            wd1_list.append(wd1)
            wd1p_list.append(wd1p)
            wd2_list.append(wd2)
            wd2p_list.append(wd2p)
            print('%.1f us: %.1f, %.1f(%.3f), %.1f(%.3f)' % (mean_us, wd0, wd1, wd1p, wd2, wd2p))
        wd0_all.append(wd0_list)
        wd1_all.append(wd1_list)
        wd1p_all.append(wd1p_list)
        wd2_all.append(wd2_list)
        wd2p_all.append(wd2p_list)
        # ax.plot(ind, wd2_list, color=colors[ibar], ls='dotted', marker='^')

# Plotting
colors = ['red', 'blue', 'orange', 'green']
fig, axs = plt.subplots(4, 1, figsize=(5, 12), dpi=300)

for ibar in range(0, 4):
    ax = axs[ibar]
    ax.plot(ind, np.array(wd0_all[ibar])/1000, color='black', ls='--', marker='^', fillstyle='none')
    ax_alt = ax.twinx()
    ax_alt.plot(ind, np.array(wd1p_all[ibar])*100, color='green', lw=0, marker='x')
    ax_alt.plot(ind, np.array(wd2p_all[ibar])*100, color='blue', lw=0, marker='x')
    ax_alt.set_ylim(0, 104)
    ax_alt.yaxis.grid(True, which='major', ls='dotted', color='black')
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.xaxis.set_major_formatter(mpl.ticker.ScalarFormatter())
    ax.yaxis.set_major_formatter(mpl.ticker.ScalarFormatter())
    ax.set_ylim(0.01, 12)
    ax.tick_params(direction='in')
    ax.grid(True, ls='dashdot', color='black')
fig.savefig('exp3_s2.png', bbox_inches='tight')