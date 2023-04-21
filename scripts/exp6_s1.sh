#!/bin/bash

cp ../stencil/stencil.c ./exp6.c
cp ../stencil/stencil_sampling.c ./exp6_sampling.c
mkdir exp6_data

nsize_arr=(64 80 128 160 256 500 512 1000 1024 2000 2048 4000 4096 6000 8000)
papi_nsamp_arr=()
stiming_nsamp_arr=()
NT=10
FREQ=2.49414

for narr in "${nsize_arr[@]}"
do
    date
    mpicc -o exp6_stiming_C${narr}.x -DNTEST=${NT} -DNARR=${narr} -DSTIMING ./exp6.c
    mpicc -o exp6_papi_C${narr}.x -DNTEST=${NT} -DNARR=${narr} -DPAPI ./exp6.c -lpapi
    
    mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./exp6_stiming_C${narr}.x
    nsamp=$(python3 get_mean.py3  stiming_time.csv $FREQ)
    mpicc -o exp6_stiming_C${narr}_S${nsamp}.x -DNTEST=${NT} -DNARR=${narr} -DNSAMP=$nsamp -DSTIMING ./exp6_sampling.c
    echo "Size=$narr, STiming NSAMP=$nsamp"
    echo "$narr,$nsamp" >> stiming_nsamp.txt
    stiming_nsamp_arr+=($nsamp)
    echo "${stiming_nsamp_arr[@]}"

    mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./exp6_papi_C${narr}.x
    nsamp=$(python3 get_mean.py3  papi_time.csv $FREQ)
    mpicc -o exp6_papi_C${narr}_S${nsamp}.x -DNTEST=${NT} -DNARR=${narr} -DNSAMP=$nsamp -DPAPI ./exp6_sampling.c -lpapi
    echo "Size=$narr, PAPI NSAMP=$nsamp"
    echo "$narr,$nsamp" >> papi_nsamp.txt
    papi_nsamp_arr+=($nsamp)
done

echo "Start timing and in-situ sampling for FilT."

for i in {1..10}
do
    for j in {0..14}
    do
        narr=${nsize_arr[$j]}
        s=${stiming_nsamp_arr[$j]}
        p=${papi_nsamp_arr[$j]}
        NAME=TL_CALC_W-C$narr
        echo "====== Round $i, NARR=$narr ======" 
        date
        echo "- STiming running." 
        mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./exp6_stiming_C${narr}.x
        echo "- STiming in-situ sampling." 
        mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./exp6_stiming_C${narr}_S${s}.x
        echo "- PAPI running." 
        mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./exp6_papi_C${narr}.x
        echo "- PAPI in-situ sampling." 
        mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./exp6_papi_C${narr}_S${p}.x
    
        cat stiming_time.csv     >> exp6_data/${NAME}-STiming.csv
        cat stiming_time_sample.csv >> exp6_data/${NAME}-STiming-sample.csv
        cat papi_time.csv        >> exp6_data/${NAME}-PAPI.csv
        cat papi_time_sample.csv    >> exp6_data/${NAME}-PAPI-sample.csv
    done
done
