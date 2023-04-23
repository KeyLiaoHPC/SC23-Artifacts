#!/bin/bash

cp ../vkern/vkern.c ./exp4.c
cp ../vkern/vkern_sampling.c ./exp4_sampling.c
mkdir exp4_data

V1=0
V2=1
T=0
echo "====== Compiling T=0  ======"
mpicc -o exp4_stiming_T${T}.x -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6291456 -DINIT ./exp4.c -lgsl -lopenblas
mpicc -o exp4_papi_T${T}.x -DUSE_PAPI -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6291456 -DINIT ./exp4.c -lpapi -lgsl -lopenblas
mpicc -o exp4_stiming_T${T}_sampling.x -DUNIFORM -DNTEST=100 -DTBASE=$T -DNSAMP=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6294156 -DINIT ./exp4_sampling.c -lgsl -lopenblas
mpicc -o exp4_papi_T${T}_sampling.x -DUSE_PAPI -DUNIFORM -DNTEST=100 -DTBASE=$T -DNSAMP=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6294156 -DINIT ./exp4_sampling.c -lpapi -lgsl -lopenblas

V1=25
V2=6
T=625
echo "====== Compiling T=625  ======"
mpicc -o exp4_stiming_T${T}.x -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6291456 -DINIT ./exp4.c -lgsl -lopenblas
mpicc -o exp4_papi_T${T}.x -DUSE_PAPI -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6291456 -DINIT ./exp4.c -lpapi -lgsl -lopenblas
mpicc -o exp4_stiming_T${T}_sampling.x -DUNIFORM -DNTEST=100 -DTBASE=$T -DNSAMP=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6294156 -DINIT ./exp4_sampling.c -lgsl -lopenblas
mpicc -o exp4_papi_T${T}_sampling.x -DUSE_PAPI -DUNIFORM -DNTEST=100 -DTBASE=$T -DNSAMP=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6294156 -DINIT ./exp4_sampling.c -lpapi -lgsl -lopenblas

V1=250
V2=6
T=6250
echo "====== Compiling T=6250  ======"
mpicc -o exp4_stiming_T${T}.x -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6291456 -DINIT ./exp4.c -lgsl -lopenblas
mpicc -o exp4_papi_T${T}.x -DUSE_PAPI -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6291456 -DINIT ./exp4.c -lpapi -lgsl -lopenblas
mpicc -o exp4_stiming_T${T}_sampling.x -DUNIFORM -DNTEST=100 -DTBASE=$T -DNSAMP=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6294156 -DINIT ./exp4_sampling.c -lgsl -lopenblas
mpicc -o exp4_papi_T${T}_sampling.x -DUSE_PAPI -DUNIFORM -DNTEST=100 -DTBASE=$T -DNSAMP=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6294156 -DINIT ./exp4_sampling.c -lpapi -lgsl -lopenblas

V1=2500
V2=6
T=62500
echo "====== Compiling T=62500  ======"
mpicc -o exp4_stiming_T${T}.x -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6291456 -DINIT ./exp4.c -lgsl -lopenblas
mpicc -o exp4_papi_T${T}.x -DUSE_PAPI -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6291456 -DINIT ./exp4.c -lpapi -lgsl -lopenblas
mpicc -o exp4_stiming_T${T}_sampling.x -DUNIFORM -DNTEST=100 -DTBASE=$T -DNSAMP=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6294156 -DINIT ./exp4_sampling.c -lgsl -lopenblas
mpicc -o exp4_papi_T${T}_sampling.x -DUSE_PAPI -DUNIFORM -DNTEST=100 -DTBASE=$T -DNSAMP=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6294156 -DINIT ./exp4_sampling.c -lpapi -lgsl -lopenblas

NAME=sc1-S62500+2500x6-INIT+6MiBx40
TBASE=62500
DISTRO=UNIFORM
V1=2500
V2=6
NT=100
FSIZE=6291456
FKERN=INIT

for i in {1..10}
do
    for t in 0 625 6250 62500
    do
        echo "====== Round $i, #DSub = $t ======"
        date
        mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./exp4_stiming_T${t}.x
        cat stiming_time.csv >> exp4_data/exp4-T${t}-STiming.csv
        sleep 1
        mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./exp4_stiming_T${t}_sampling.x
        cat stiming_time_sample.csv >> exp4_data/exp4-T${t}-STiming-sample.csv
        sleep 1
        mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./exp4_papi_T${t}.x
        cat papi_time.csv >> exp4_data/exp4-T${t}-PAPI.csv
        sleep 1
        mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./exp4_papi_T${t}_sampling.x
        cat papi_time_sample.csv >> exp4_data/exp4-T${t}-PAPI-sample.csv
        sleep 1
    done
done

rm *.csv
