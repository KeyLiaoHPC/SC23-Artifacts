#!/bin/bash -x
cp ../vkern/vkern.c ./exp2.c
mkdir exp2_data

V1=0
V2=1
T=0
mpicc -o exp2_stiming_T${T}.x -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6291456 -DINIT ./exp2.c -lgsl -lopenblas
mpicc -o exp2_papi_T${T}.x -DUSE_PAPI -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6291456 -DINIT ./exp2.c -lpapi -lgsl -lopenblas
mpicc -o exp2_stiming_T${T}_noflush.x -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=0 -DINIT ./exp2.c -lgsl -lopenblas
mpicc -o exp2_papi_T${T}_noflush.x -DUSE_PAPI -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=0 -DINIT ./exp2.c -lpapi -lgsl -lopenblas


V1=25
V2=6
T=625
mpicc -o exp2_stiming_T${T}.x -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6291456 -DINIT ./exp2.c -lgsl -lopenblas
mpicc -o exp2_papi_T${T}.x -DUSE_PAPI -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6291456 -DINIT ./exp2.c -lpapi -lgsl -lopenblas
mpicc -o exp2_stiming_T${T}_noflush.x -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=0 -DINIT ./exp2.c -lgsl -lopenblas
mpicc -o exp2_papi_T${T}_noflush.x -DUSE_PAPI -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=0 -DINIT ./exp2.c -lpapi -lgsl -lopenblas

V1=250
V2=6
T=6250
mpicc -o exp2_stiming_T${T}.x -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6291456 -DINIT ./exp2.c -lgsl -lopenblas
mpicc -o exp2_papi_T${T}.x -DUSE_PAPI -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6291456 -DINIT ./exp2.c -lpapi -lgsl -lopenblas
mpicc -o exp2_stiming_T${T}_noflush.x -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=0 -DINIT ./exp2.c -lgsl -lopenblas
mpicc -o exp2_papi_T${T}_noflush.x -DUSE_PAPI -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=0 -DINIT ./exp2.c -lpapi -lgsl -lopenblas

V1=2500
V2=6
T=62500
mpicc -o exp2_stiming_T${T}.x -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6291456 -DINIT ./exp2.c -lgsl -lopenblas
mpicc -o exp2_papi_T${T}.x -DUSE_PAPI -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=6291456 -DINIT ./exp2.c -lpapi -lgsl -lopenblas
mpicc -o exp2_stiming_T${T}_noflush.x -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=0 -DINIT ./exp2.c -lgsl -lopenblas
mpicc -o exp2_papi_T${T}_noflush.x -DUSE_PAPI -DUNIFORM -DNTEST=100 -DTBASE=$T -DV1=$V1 -DV2=$V2 -DFSIZE=0 -DINIT ./exp2.c -lpapi -lgsl -lopenblas

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
        mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./exp2_stiming_T${t}.x
        cat stiming_time.csv >> exp2_data/exp2-T${t}-STiming.csv
        sleep 1
        mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./exp2_papi_T${t}.x
        cat papi_time.csv >> exp2_data/exp2-T${t}-PAPI.csv
        sleep 1
        date
        mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./exp2_stiming_T${t}_noflush.x
        cat stiming_time.csv >> exp2_data/exp2-T${t}-STiming-noflush.csv
        sleep 1
        mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./exp2_papi_T${t}_noflush.x
        cat papi_time.csv >> exp2_data/exp2-T${t}-PAPI-noflush.csv
        sleep 1
    done
done

rm *.csv
