# FilT algorithm
# Mitigating timing fluctuations from measurement results
import pandas as pd
import numpy as np


# Class MesVar:
# Class for handling a measurement result
class MetResult:
    # met_file: The measurement result file.
    # col_id: Target column id in the file.
    def __init__(self, met_file='', col_id=1, freq_ghz=2.5, tick_ghz=1):
        # Pandas dataframe of Measurement data
        if not len(met_file):
            raise ValueError('Expecting a file path.')
        met_df = pd.read_csv(met_file, header=None, dtype=float)
        # Attributes
        self.met_arr = met_df[col_id].to_numpy() / tick_ghz # 1D Numpy array, measurement data.
        self.tnoise_arr = None  # 1D Numpy array, timing fluctuation sample data.
        self.denoise_arr = None # [[time,probability], ...]. 2D Numpy array, denoise bins data.
        self.denoise_cdf_arr = None # [[quantile,time], ...]. 2D Numpy array, denoise CDF.
        self.denoise_res = None # scalar, the number of bins of the final data.
        self.restore_cdf_arr = None # CDF restore from denoised signal for validation
        self.freq_ghz = freq_ghz # Main frequency of CPU
        self.tick_ghz = tick_ghz # tick per nanosec

    # Slice raw data into histo
    # nsper
    def _slice_hist(self, roundto=10, prob_low=0.0025, prob_start=0.2, arr=np.zeros(1), debug=False):
        # t_round_arr = np.round(arr, 0).astype(int)
        t_round_arr = np.round(arr / roundto) * roundto
        t_round_arr.sort()
        t_bins, t_counts = np.unique(t_round_arr, return_counts=True)
        tot_count = np.sum(t_counts)
        if debug:
            print("[Slicing] Ticks per bin: %d, initial probability: %f, recursion probability: %f" %
              (roundto, prob_start, prob_low))
            print("[Slicing] Total point: %d" % (tot_count))
        t_plist = list()
        point_count = 0 # prob total
        target_count = int(prob_start * tot_count)
        ids = 0
        # === Initial probability ===
        while True:
            point_count += t_counts[ids]
            ids += 1
            if point_count >= target_count:
                break
        # Weighted mean
        t_mean = np.sum([t_bins[j] * t_counts[j] for j in range(0, ids)])
        # Adjusting the count of last bin
        # t_counts[ids] = point_count - target_count
        # t_mean = t_mean - t_bins[ids] * t_counts[ids]
        t_mean /= point_count
        # Rount to ticks per bin
        t_mean = np.round(t_mean / roundto) * roundto
        t_plist.append([t_mean, point_count / tot_count])

        # === slicing for recursion ===
        target_count = prob_low * tot_count
        while ids < len(t_counts):
            point_count = 0
            ide = ids
            while True:
                point_count += t_counts[ide]
                ide += 1
                if point_count >= target_count:
                    break
                if ide >= len(t_counts):
                    break
            # Weighted mean
            t_mean = np.sum([t_bins[j] * t_counts[j] for j in range(ids, ide)])
            # Adjusting the count of last bin
            # t_counts[ide] = point_count - target_count
            # t_mean = t_mean - t_bins[ids] * t_counts[ids]
            t_mean /= point_count
            t_mean = np.round(t_mean / roundto) * roundto
            t_plist.append([t_mean, point_count / tot_count])
            # Set ids to the start point of next bin
            ids = ide
        return np.array(t_plist)

    # Load the timing fluctuation sample.
    # tnoise_file: The timing fluctuation sample csv file.
    def _load_tnoise_sample(self, tnoise_file, col, vkern_count):
        tnoise_df = pd.read_csv(tnoise_file, header=None, dtype=float)
        self.tnoise_arr = tnoise_df[col].to_numpy() / self.tick_ghz - vkern_count * 2 / self.freq_ghz

    # function filt
    # tnoise_file: The timing fluctuation sample csv file.
    # is_multi_sample[=False]: Set to True if the timing range map to multiple timing fluctuation samples.
    # tnoise_file: timing fluctuations sampling files
    # col: valid column of files
    # vkern_count: how many vkern kernel is sampled, used as the theoretical run time in timing fluctuation samples
    # is_multi_sample: whether samples based on different vkern_count are used
    # roundto: round all times into the base, 10ns for default
    # met_pl: The lowest threshold of the probability of a measurement data bin
    # met_ps: The lowest threshold of the probability of the first data bin in measurement results
    # tf_pl: Similar to met_pl, for timing fluctuations
    # tf_ps: Similar to met_ps, for timing fluctuations
    # mix: Enable mixing probability in residual array for nagative probability
    def filt(self, tnoise_file, col=1, vkern_count=0, is_multi_sample=False, roundto=10,
             met_pl=0.001, met_ps=0.001, tf_pl=0.001, tf_ps=0.05, mix=False, debug=False, validate=True):
        self._load_tnoise_sample(tnoise_file, col, vkern_count)
        # Slicing raw data in bins.
        # *_bins = [[time, prob], ...]
        met_bins = self._slice_hist(roundto=roundto, prob_low=met_pl, prob_start=met_ps, arr=self.met_arr)
        noise_bins = self._slice_hist(roundto=roundto, prob_low=tf_pl, prob_start=tf_ps, arr=self.tnoise_arr)
        denoise_bins = np.copy(met_bins)
        denoise_list = list()
        met_len = len(met_bins)
        noise_len = len(noise_bins)
        rt_pt = 0.0  # Total real time probability
        for im in range(0, met_len):
            # === START: Single step ===
            # corresponding real time
            t0 = denoise_bins[im, 0]
            pm = denoise_bins[im, 1]
            r = t0 - noise_bins[0, 0] #real time
            if pm <= 0:
                # this bin has all been substracted by noise
                denoise_list.append([r, 0])
            else:
                if im < met_len - 1:
                    t1 = denoise_bins[im + 1, 0]
                else:
                    # this is tha last number in measurement array
                    t1 = 0x7fffffff - 1
                pv = 0
                jv = 0  # start id for subsequent probability subtracting
                for iv in range(0, noise_len):
                    if r + noise_bins[iv, 0] >= t1:
                        # summarizing probability until the measurement value hits the next bin
                        jv = iv
                        break
                    pv += noise_bins[iv, 1]
                pr = pm / pv
                rt_pt += pr
                denoise_list.append([r, pr])
                denoise_bins[im][1] = 0
                while jv < noise_len:
                    t = r + noise_bins[jv, 0]
                    if t > denoise_bins[-1, 0]:
                        denoise_bins[-1, 1] -= pr * noise_bins[jv, 1]
                    else:
                        for jm in range(im + 1, met_len - 1):
                            if denoise_bins[jm, 0] <= t < denoise_bins[jm + 1, 0]:
                                denoise_bins[jm, 1] -= pr * noise_bins[jv, 1]
                                if mix and denoise_bins[jm, 1] < 0:
                                    avg_prob = (denoise_bins[jm, 1] + denoise_bins[jm + 1, 1]) / 2
                                    denoise_bins[jm, 1] = avg_prob
                                    denoise_bins[jm + 1, 1] = avg_prob
                                break
                    jv += 1
            if rt_pt > 1:
                denoise_list[-1][1] -= (rt_pt - 1)
                break
        self.denoise_arr = np.array(denoise_list)
        # self.denoise_cdf_arr = np.cumsum(denoise_list[:, 1])
        if validate:
            # Convoluting data after denoise
            from .utils import bin_to_cdf, raw_to_cdf, calc_wasserstein
            residual = np.sum(np.abs(denoise_bins[:, 1]))
            restore_bins = list()
            for bin in denoise_list:
                for noise in noise_bins:
                    t = bin[0] + noise[0]
                    p = bin[1] * noise[1]
                    if len(restore_bins) == 0:
                        restore_bins.append([t, p])
                    else:
                        for i in range(0, len(restore_bins)):
                            if t == restore_bins[i][0]:
                                restore_bins[i][1] += p
                                break
                            if t < restore_bins[i][0]:
                                restore_bins.insert(i, [t, p])
                                break
                            if i+1 == len(restore_bins):
                                restore_bins.append([t, p])
            restore_cdf = bin_to_cdf(np.array(restore_bins), 1000)
            met_cdf = raw_to_cdf(self.met_arr, 1000)
            wd = calc_wasserstein(restore_cdf, met_cdf, [999,1000])
            self.restore_cdf_arr = np.array(restore_cdf)
            return denoise_list, residual, wd[0]
        return denoise_list

    # Calculating Wasserstein distance
#    def calc_wasserstein(self):

