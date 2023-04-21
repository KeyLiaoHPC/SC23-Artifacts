# SC23-Artifacts
Source codes and scripts for reproducibility.

## Prerequisite
First, We suggest using the same(or similar) hardware configurations for reproducing:
- Server: Inspur NS5488m5 blade server (in Inspur i48 rack)
- 2 x Intel Xeon Gold 6248 (fixed at 2.5GHz)
- 12 x 16GiB DDR4-2666 RAM

Second, The server for running timing and FilT algorithm must have following softwares installed:
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

## Reproducing
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

We noted that if the compute server has the different *tsc_khz* kernel variable than 2.49414KHz, users should modify the FREQ variable in exp6_s1.sh script and the *freq* variable in each python script for correctly converting the reading of RDTSCP to nanosecond.