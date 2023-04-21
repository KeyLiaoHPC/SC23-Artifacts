import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import sys
sys.path.append("../")
import filt
freq=2.49414
id = 0
for S in [0, 625, 6250, 62500]:
    I = 25
    NI = 6
    NT = 100
    NR = 10
    colors=['blue', 'green', 'red',  'darkorange']
    file_list = ['./exp2_data/exp2-T' + str(S) + '-STiming.csv', './exp2_data/exp2-T'+ str(S) + '-STiming-noflush.csv',
                 './exp2_data/exp2-T' + str(S) + '-PAPI.csv', './exp2_data/exp2-T' + str(S) + '-PAPI-noflush.csv']
    fig, ax = plt.subplots(1, 1, figsize=(5,3), dpi=300)
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = 'cambria'
    mpl.rcParams['font.size'] = '14'
    draw_step = 10
    i = 0
    for f in file_list:
        df = pd.read_csv(f, header=None)
        if f.find('STiming') > 0:
            arr = df[2].to_numpy() / freq
        else:
            arr = df[2].to_numpy()
        if f.find('noflush') > 0:
            mk = '+'
            fs = 'none'
        else:
            mk = 'x'
            fs = 'none'
        cdf = filt.raw_to_cdf(arr, 1000)
        ax.plot([i / 1000 * 100 for i in range(0, 996, draw_step)], cdf[0:996:draw_step], lw=0, ms=3.5, marker=mk, fillstyle=fs, ls='--', color=colors[i])
        i+= 1
        print(np.mean(cdf))
    df = pd.read_csv(file_list[0], header=None)
    arr0 = df[1].to_numpy() * 2 / 2.5
    cdf0 = filt.raw_to_cdf(arr0, 1000)
    ax.plot([i / 1000 * 100 for i in range(0, 991)], cdf0[0:991], ms=0.5, color='black', ls='--')
    ax.set_yscale('log')
    # ymin = np.min([cdf0, cdf1, cdf2]) * 0.9
    # ymax = np.quantile([cdf0, cdf1, cdf2], 0.995) * 1.1
    # ax.set_ylim(0, 800)
    ax.tick_params(direction='in')
    ax.grid(True, which="both", ls='dotted', color='grey')
    ax.set_xlim(-5, 105)
    # ax.set_yticks([10, 20, 50, 100, 200, 500, 1000], [10, 20, 50, 100, 200, 500, 1000])
    # ax.set_ylim(0, 2000)
    fig.savefig('exp2_' + str(id) + '.png', bbox_inches='tight')
    id += 1