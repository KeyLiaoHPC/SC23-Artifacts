# SC23-Artifacts
Source codes and scripts for reproducibility.

## Prerequisite
### Hardwares

We suggest using the same(or similar) hardware configurations for reproducing the measurement in the paper:
- Server: Inspur NS5488m5 blade server (in Inspur i48 rack)
- 2 x Intel Xeon Gold 6248 (fixed at 2.5GHz)
- 12 x 16GiB DDR4-2666 RAM

We noted that the memory foot print of the experiment is up to 98GiB, and users need at least 20GiB disk space for experiment data.

### Softwares

The server for running timing and FilT algorithm must have following softwares installed:
- GCC-9.3.0
- Python-3.10
- OpenMPI (>4.0.5)
- Openblas-0.3.17
- GNU Scientific Library - 2.17
- PAPI-6.0.0.1

Meanwhile, all these softwares should be existed in the relative path in environment variables. E.g.:
```bash
$ export
declare -x BLAS="/mnt/nvme/01-App/openblas-0.3.17_gcc930"
declare -x CPATH="/mnt/nvme/01-App/gcc-9.3.0/include:/mnt/nvme/01-App/openmpi-4.0.6_gcc930/include:/mnt/nvme/hpckey/01-App/03-x86-64-linux/papi-6.0.0_gnu9/include:/mnt/nvme/hpckey/01-App/03-x86-64-linux/libpfc_gnu9/include:/mnt/nvme/hpckey/01-App/03-x86-64-linux/gsl-2.7_gcc930/include:/mnt/nvme/hpckey/03-Project/perf_var/PerfHound/src/"
declare -x GCC="/mnt/nvme/01-App/gcc-9.3.0"
declare -x GSL="/mnt/nvme/hpckey/01-App/03-x86-64-linux/gsl-2.7_gcc930"
declare -x LD_LIBRARY_PATH="/mnt/nvme/01-App/gcc-9.3.0/lib:/mnt/nvme/01-App/gcc-9.3.0/lib64:/mnt/nvme/01-App/openmpi-4.0.6_gcc930/lib:/mnt/nvme/hpckey/01-App/03-x86-64-linux/papi-6.0.0_gnu9/lib:/mnt/nvme/hpckey/01-App/03-x86-64-linux/libpfc_gnu9/lib64:/mnt/nvme/01-App/openblas-0.3.17_gcc930/lib:/mnt/nvme/hpckey/01-App/03-x86-64-linux/g
sl-2.7_gcc930/lib:/mnt/nvme/hpckey/03-Project/perf_var/PerfHound/src/probe/lib:/usr/lib:/usr/lib64"
declare -x LIBRARY_PATH="/mnt/nvme/01-App/gcc-9.3.0/lib:/mnt/nvme/01-App/gcc-9.3.0/lib64:/mnt/nvme/01-App/openmpi-4.0.6_gcc930/lib:/mnt/nvme/hpckey/01-App/03-x86-64-linux/papi-6.0.0_gnu9/lib:/mnt/nvme/hpckey/01-App/03-x86-64-linux/libpfc_gnu9/lib64:/mnt/nvme/01-App/openblas-0.3.17_gcc930/lib:/mnt/nvme/hpckey/01-App/03-x86-64-linux/gsl-
2.7_gcc930/lib:/mnt/nvme/hpckey/03-Project/perf_var/PerfHound/src/probe/lib"
declare -x OPENMPI="/mnt/nvme/01-App/openmpi-4.0.6_gcc930"
declare -x PAPI="/mnt/nvme/hpckey/01-App/03-x86-64-linux/papi-6.0.0_gnu9"
declare -x PATH="/mnt/nvme/01-App/gcc-9.3.0/bin:/mnt/nvme/01-App/openmpi-4.0.6_gcc930/bin:/mnt/nvme/hpckey/01-App/03-x86-64-linux/papi-6.0.0_gnu9/bin:/mnt/nvme/hpckey/01-App/03-x86-64-linux/libpfc_gnu9/bin:/mnt/nvme/hpckey/01-App/03-x86-64-linux/gsl-2.7_gcc930/bin:/mnt/nvme/hpckey/03-Project/perf_var/PerfHound/src/probe/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/opt/puppetlabs/bin:/home/hpckey/.local/bin:/home/hpckey/bin"

```

Finally, before running, the cpu frequency needs to be fixed, and the user-space RDTSCP should be switched on by using the root permission:
``` bash
$ su -
$ cpupower frequency-set  -u 2.5GHz -d 2.5GHz
$ echo 2 > /sys/bus/event_source/devices/cpu/rdpmc
$ modprobe -ar iTCO_wdt iTCO_vendor_support
$ echo 0 > /proc/sys/kernel/nmi_watchdog
```

After timing, following python packages should be installed before interpreting results and plotting:
- pandas-1.4.1
- numpy-1.21.5
- matplotlib-3.5.1

## Reproducibility

### The workflow
There are two scripts for each experiments. Users replicate the experiment by executing these scripts consecutively. The first one is a bash script "exp*_s1.sh". This script first prepares and compiles the source code, and executes timing and in-situ sampling. After timing, csv files of measured results are dumped to the "exp*_data" folder.

The second script, "exp*_s2.py" is for interpreting the result and plotting. There are three types of ouputs. The first type is the Wasserstein metric, such as:
```
t_base, t_mean, w-metric, w90-99.9(R90-99.9), w99-99.9(R99-99.9)
PAPI norm-s0.015
0.1 us: 542.2, 87.8(0.162), 11.3(0.021)
0.2 us: 523.2, 83.1(0.159), 10.7(0.020)
0.3 us: 556.1, 96.3(0.173), 15.9(0.029)
0.4 us: 549.1, 99.3(0.181), 18.5(0.034)
```
The second type is the ε_R and ε_P metrics for evaluating FilT algorithm in experiment 4, 5 and 6. E.g.:
```
64 PAPI ps=0.200000,eP=0.0001,eR=0.003272
64 STiming ps=0.050000,eP=0.0352,eR=0.004348
80 PAPI ps=0.050000,eP=0.2854,eR=0.009168
80 STiming ps=0.050000,eP=0.0000,eR=0.002441
128 PAPI ps=0.200000,eP=0.0000,eR=0.002619
```
The third type is the figure, which maps to corresponding plots in our paper.

We noted that if the compute server has the different *tsc_khz* kernel variable than 2,494,140KHz, users should modify the FREQ variable in exp6_s1.sh script and the *freq* variable in each python script for correctly converting the reading of RDTSCP to nanosecond.

### Experiment 1

Reproducibility info:
- Approx. run time: 5 minutes.
- Corresponding figure: Fig.2
- Outputs: exp1_<0-1>.png.
- Example console output:

```  
$ ./exp1_s1.sh
+ '[' -z '' ']'
+ case "$-" in
+ __lmod_vx=x
+ '[' -n x ']'
+ set +x
Shell debugging temporarily silenced: export LMOD_SH_DBG_ON=1 for this output (/usr/share/lmod/lmod/init/bash)
Shell debugging restarted
+ unset __lmod_vx
+ cp ../stencil/stencil.c ./exp1.c
+ mkdir exp1_data
+ NT=10
+ for narr in 256 4000
+ mpicc -o t1_stiming_C256.x -DNTEST=10 -DNARR=256 -DSTIMING ./exp1.c
+ mpicc -o t1_papi_C256.x -DNTEST=10 -DNARR=256 -DPAPI ./exp1.c -lpapi
+ for narr in 256 4000
+ mpicc -o t1_stiming_C4000.x -DNTEST=10 -DNARR=4000 -DSTIMING ./exp1.c
+ mpicc -o t1_papi_C4000.x -DNTEST=10 -DNARR=4000 -DPAPI ./exp1.c -lpapi
+ for i in '{1..10}'
+ for narr in 256 4000
+ NAME=TL_CALC_W-C256
+ rm 'stiming*.csv'
+ rm 'papi*.csv'
+ mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./t1_stiming_C256.x
NTEST=10, NARR=256, rx=0.841919, ry=0.170247
Warming up for 2000 ms.
Start running.
Run time: 11057201 ns
+ mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./t1_papi_C256.x
NTEST=10, NARR=256, rx=0.696394, ry=0.202002
Warming up for 2000 ms.
Start running.
Run time: 12179926 ns
+ cat stiming_time.csv
+ cat stiming_tot_time.csv
+ cat papi_time.csv
+ cat papi_tot_time.csv
...
```

### Experiment 2

Reproducibility info:
- Approx. run time: 5 minutes.
- Corresponding figure: Fig.4
- Outputs: exp2_<0-3>.png.
- Example console output:

```
$ ./exp2_s1.sh
+ '[' -z '' ']'
+ case "$-" in
+ __lmod_vx=x
+ '[' -n x ']'
+ set +x
Shell debugging temporarily silenced: export LMOD_SH_DBG_ON=1 for this output (/usr/share/lmod/lmod/init/bash)
Shell debugging restarted
+ unset __lmod_vx
+ cp ../vkern/vkern.c ./exp2.c
+ mkdir exp2_data
+ V1=0
+ V2=1
+ T=0
+ mpicc -o exp2_stiming_T0.x -DUNIFORM -DNTEST=100 -DTBASE=0 -DV1=0 -DV2=1 -DFSIZE=6291456 -DINIT ./exp2.c -lgsl -lopenblas
+ mpicc -o exp2_papi_T0.x -DUSE_PAPI -DUNIFORM -DNTEST=100 -DTBASE=0 -DV1=0 -DV2=1 -DFSIZE=6291456 -DINIT ./exp2.c -lpapi -lgsl -lopenblas
+ mpicc -o exp2_stiming_T0_noflush.x -DUNIFORM -DNTEST=100 -DTBASE=0 -DV1=0 -DV2=1 -DFSIZE=0 -DINIT ./exp2.c -lgsl -lopenblas
+ mpicc -o exp2_papi_T0_noflush.x -DUSE_PAPI -DUNIFORM -DNTEST=100 -DTBASE=0 -DV1=0 -DV2=1 -DFSIZE=0 -DINIT ./exp2.c -lpapi -lgsl -lopenblas
+ V1=25
+ V2=6
...
─
+ NAME=sc1-S62500+2500x6-INIT+6MiBx40
+ TBASE=62500
+ DISTRO=UNIFORM
+ V1=2500
+ V2=6
+ NT=100
+ FSIZE=6291456
+ FKERN=INIT
+ for i in '{1..10}'
+ for t in 0 625 6250 62500
+ echo '====== Round 1, #DSub = 0 ======'
====== Round 1, #DSub = 0 ======
+ date
Sun Apr 23 14:27:36 CST 2023
+ mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./exp2_stiming_T0.x
Generating uniform ditribution. Tbase=0, interval=0, nint=1, Ntest=100.
Warming up for 1000 ms.
Start random walking.
+ cat stiming_time.csv
+ sleep 1
...
```

```
$ ./exp2_s2.py
./exp2_data/exp2-T0-STiming.csv MeanTime= 23.68548881575416 W-metric= 23.70917430456991
./exp2_data/exp2-T0-STiming-noflush.csv MeanTime= 18.75565155894248 W-metric= 18.77440721050142
./exp2_data/exp2-T0-PAPI.csv MeanTime= 563.8901098901099 W-metric= 564.454
./exp2_data/exp2-T0-PAPI-noflush.csv MeanTime= 252.1908091908092 W-metric= 252.443
...
```

### Experiment 3

Reproducibility info:
- Approx. run time: 6 hours.
- Corresponding figure: Fig.5
- Outputs: exp3_0.png.
- Example console output:

```
$ ./exp3_s1.sh
mkdir: cannot create directory ‘exp3_data’: File exists
Sun Apr 23 14:29:48 CST 2023
====== Compiling, t_base = 0.1 us ======
====== Compiling, t_base = 0.2 us ======
====== Compiling, t_base = 0.3 us ======
...
Sun Apr 23 14:31:24 CST 2023
====== Round 1, t_base = 0.1 us ======
Sun Apr 23 14:31:24 CST 2023
Generating Pareto ditribution. Tbase=125, alpha=26.0000, Ntest=10000.
Warming up for 1000 ms.
Start random walking.
Generating Pareto ditribution. Tbase=125, alpha=26.0000, Ntest=10000.
Warming up for 1000 ms.
Start random walking.
Generating normal ditribution. Tbase=125, sigma=0.0150, Ntest=10000.
Warming up for 1000 ms.
Start random walking.
Generating normal ditribution. Tbase=125, sigma=0.0150, Ntest=10000.
Warming up for 1000 ms.
Start random walking.
====== Round 1, t_base = 0.2 us ======
Sun Apr 23 14:33:10 CST 2023
Generating Pareto ditribution. Tbase=250, alpha=26.0000, Ntest=10000.
...

```

```
$ ./exp3_s2.py
t_base, t_mean, w-metric, w90-99.9(R90-99.9), w99-99.9(R99-99.9)
PAPI norm-s0.015
0.1 us: 542.2, 87.8(0.162), 11.3(0.021)
0.2 us: 523.2, 83.1(0.159), 10.7(0.020)
0.3 us: 556.1, 96.3(0.173), 15.9(0.029)
...
```

### Experiment 4

Reproducibility info:
- Approx. run time: 10 minutes.
- Corresponding figure: Fig.11
- Outputs: exp4_<0-2>.png.
- Example console output:

```
$ ./exp4_s1.sh
====== Compiling T=0  ======
====== Compiling T=625  ======
====== Compiling T=6250  ======
====== Compiling T=62500  ======
====== Round 1, #DSub = 0 ======
Sun Apr 23 14:35:48 CST 2023
Generating uniform ditribution. Tbase=0, interval=0, nint=1, Ntest=100.
Warming up for 1000 ms.
Start random walking.
Generating uniform ditribution. Tbase=0, interval=0, nint=1, Ntest=100.
Warming up for 1000 ms.
Start random walking.
Generating uniform ditribution. Tbase=0, interval=0, nint=1, Ntest=100.
Warming up for 1000 ms.
Start random walking.
Generating uniform ditribution. Tbase=0, interval=0, nint=1, Ntest=100.
Warming up for 1000 ms.
Start random walking.
====== Round 1, #DSub = 625 ======
Sun Apr 23 14:36:01 CST 2023
Generating uniform ditribution. Tbase=625, interval=25, nint=6, Ntest=100.
Warming up for 1000 ms.
...
```

```
$ exp4_s2.py
625 PAPI bin_p_st= 0.2 ep= 0.054603398138516245 eR= 0.009866444669112143
625 STiming bin_p_st= 0.05 ep= 0.05262445028180117 eR= 0.013861269289053221
w_met_papi= 536.293 w_filter_papi= 24.63 w_met_stiming= 37.297331184296034 w_filter_stiming= 10.73
6250 PAPI bin_p_st= 0.2 ep= 0.10840920483024813 eR= 0.008136763867832108
6250 STiming bin_p_st= 0.05 ep= 0.0001361110148056413 eR= 0.0011240415813730334
w_met_papi= 619.378 w_filter_papi= 57.38 w_met_stiming= 168.56778528871718 w_filter_stiming= 49.08
```

### Experiment 5

Reproducibility info:
- Approx. run time: 20 hours.
- Corresponding figure: Fig.12
- Outputs: exp5_<0-3>.png.
- Example console output:

```
$ ./exp5_s1.sh
Sun Apr 23 14:36:12 CST 2023
====== Compiling, t_base = 0.1 us ======
====== Compiling, t_base = 0.2 us ======
====== Compiling, t_base = 0.3 us ======
====== Compiling, t_base = 0.4 us ======
...
Sun Apr 23 14:39:24 CST 2023
====== Round 1, t_base = 0.1 us ======
Sun Apr 23 14:39:24 CST 2023
Sun Apr 23 14:39:24 CST 2023
Generating Pareto ditribution. Tbase=125, alpha=26.0000, Ntest=10000.
Warming up for 1000 ms.
Start random walking.
Generating Pareto ditribution. Tbase=125, alpha=26.0000, Ntest=10000.
Warming up for 1000 ms.
Start random walking.
Generating Pareto ditribution. Tbase=125, alpha=26.0000, Ntest=10000.
Warming up for 1000 ms.
Start random walking.
...
```

```
$ ./exp5_s2.py
norm-s0.015
0.1 PAPI ps=0.100000,eP=0.0613,eR=0.012751
0.1 STiming ps=0.050000,eP=0.0127,eR=0.015968
0.2 PAPI ps=0.200000,eP=0.0644,eR=0.012380
0.2 STiming ps=0.050000,eP=0.0344,eR=0.008929
...
0 0.1 PAPI, w-metric: 559.3304 35.254400000000004 w90: 94.6006000000001 5.0166000000000075
0 0.1 STiming, w_raw= 33.58177244902051 w_filtered= 1.4029999999999985 w90_raw= 5.240000089810511 w90_filtered= 0.29359999999999986
1 0.2 PAPI, w-metric: 556.863 33.332600000000006 w90: 96.86600000000004 6.399000000000008
1 0.2 STiming, w_raw= 34.074924647373464 w_filtered= 1.4882000000000026 w90_raw= 4.94231172267796 w90_filtered= 0.18400000000000016
...
pareto-b26
0.1 PAPI ps=0.200000,eP=0.1060,eR=0.029260
0.1 STiming ps=0.050000,eP=0.2410,eR=0.016422
0.2 PAPI ps=0.200000,eP=0.0889,eR=0.026503
0.2 STiming ps=0.050000,eP=0.0431,eR=0.016847
...
0 0.1 PAPI, w-metric: 514.817 29.074 w90: 78.7604 0.4346000000000032
0 0.1 STiming, w_raw= 30.450176108799035 w_filtered= 3.5839999999999996 w90_raw= 3.8977647830514712 w90_filtered= 1.2896
1 0.2 PAPI, w-metric: 521.4789999999999 20.531599999999997 w90: 81.30939999999987 1.1983999999999995
1 0.2 STiming, w_raw= 30.708986889268466 w_filtered= 5.141 w90_raw= 3.802381524693889 w90_filtered= 1.1845999999999997
...
```

### Experiment 6

Reproducibility info:
- Approx. run time: 1.5 hours.
- Corresponding figure: Fig.13, Fig.14
- Outputs: exp6_<0-1>.png.
- Example console output:

```
$ ./exp6_s1.sh
mkdir: cannot create directory ‘exp6_data’: File exists
Sun Apr 23 14:41:23 CST 2023
NTEST=10, NARR=64, rx=0.187913, ry=0.510888
Warming up for 2000 ms.
Start running.
Run time: 657059 ns
Size=64, STiming NSAMP=795
795
NTEST=10, NARR=64, rx=0.381623, ry=0.142063
Warming up for 2000 ms.
Start running.
Run time: 936256 ns
Size=64, PAPI NSAMP=1073
Sun Apr 23 14:41:32 CST 2023
NTEST=10, NARR=80, rx=0.437054, ry=0.135585
Warming up for 2000 ms.
Start running.
Run time: 1111074 ns
Size=80, STiming NSAMP=1190
795 1190
NTEST=10, NARR=80, rx=0.475835, ry=0.297682
Warming up for 2000 ms.
...
Size=8000, PAPI NSAMP=103866
Start timing and in-situ sampling for FilT.
====== Round 1, NARR=64 ======
Sun Apr 23 14:45:32 CST 2023
- STiming running.
NTEST=10, NARR=64, rx=0.496720, ry=0.320065
Warming up for 2000 ms.
Start running.
Run time: 682025 ns
- STiming in-situ sampling.
NTEST=10, NARR=64, rx=0.021333, ry=0.305375
Warming up for 2000 ms.
Start running.
Finish benchmarking. Writing.
Run time: 1238796 ns
- PAPI running.
NTEST=10, NARR=64, rx=0.372036, ry=0.836339
Warming up for 2000 ms.
Start running.
Run time: 948445 ns
- PAPI in-situ sampling.
NTEST=10, NARR=64, rx=0.774357, ry=0.239303
Warming up for 2000 ms.
Start running.
Finish benchmarking. Writing.
Run time: 1726943 ns
...
```

```
$ ./exp6_s2.py
64 PAPI ps=0.050000,eP=0.1365,eR=0.005131
64 STiming ps=0.050000,eP=0.0000,eR=0.001966
80 PAPI ps=0.050000,eP=0.3416,eR=0.005790
80 STiming ps=0.050000,eP=0.0000,eR=0.010920
128 PAPI ps=0.200000,eP=0.0001,eR=0.003646
128 STiming ps=0.050000,eP=0.0000,eR=0.002193
...
64 wd_raw= 214.80018583559857 wd_filtered= 4.48
80 wd_raw= 210.6965782594401 wd_filtered= 18.745
...
```