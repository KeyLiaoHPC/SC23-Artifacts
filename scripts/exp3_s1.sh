#!/bin/bash

cp ../vkern/vkern.c ./exp3.c
mkdir exp3_data

FSIZE=6291456
FKERN=INIT
WALK=-DWALK_FILE

date
for i in 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1 2 3 4 5 6 7 8 9 10 20 30 40 50 60 70 80 90 100
do
    echo "====== Compiling, t_base = $i us ======"
    tbase=$(bc <<< "$i*1250")
    tbase=$(printf '%.0f\n' $tbase)
    mpicc  -o exp3_pareto_t${i}_stiming.x \
        -DNTEST=10000 -DNPASS=1 -DTBASE=$tbase -DPARETO -DV1=26 -DHCUT=1.34 -DINIT -DFSIZE=$FSIZE \
        ./exp3.c -lgsl -lopenblas

    mpicc  -o exp3_pareto_t${i}_papi.x \
        -DUSE_PAPI -DNTEST=10000 -DNPASS=1 -DTBASE=$tbase -DPARETO -DV1=26 -DHCUT=1.34 -DINIT -DFSIZE=$FSIZE \
        ./exp3.c -lpapi -lgsl -lopenblas

    mpicc  -o exp3_normal_t${i}_stiming.x \
        -DNTEST=10000 -DNPASS=1 -DTBASE=$tbase -DNORMAL -DV1=0.015 -DLCUT=0.95 -DHCUT=1.05 -DINIT -DFSIZE=$FSIZE \
        ./exp3.c -lgsl -lopenblas

    mpicc  -o exp3_normal_t${i}_papi.x \
        -DUSE_PAPI -DNTEST=10000 -DNPASS=1 -DTBASE=$tbase -DNORMAL -DV1=0.015 -DLCUT=0.95 -DHCUT=1.05 -DINIT -DFSIZE=$FSIZE \
        ./exp3.c -lpapi -lgsl -lopenblas

done

date
for r in {1..10}
do
    for i in 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1 2 3 4 5 6 7 8 9 10 20 30 40 50 60 70 80 90 100
    do
        echo "====== Round $r, t_base = $i us ======"
        NAME1=sc2-pareto-b26-${i}us
        NAME2=sc2-norm-s0.015-${i}us

        date
        mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./exp3_pareto_t${i}_stiming.x
        sleep 1
        mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./exp3_pareto_t${i}_papi.x
        sleep 1
        
        cat  stiming_time.csv   >> exp3_data/${NAME1}-STiming.csv
        cat  papi_time.csv  >> exp3_data/${NAME1}-PAPI.csv

	    mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./exp3_normal_t${i}_stiming.x
        sleep 1
        mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./exp3_normal_t${i}_papi.x
        sleep 1

        cat  stiming_time.csv   >> exp3_data/${NAME2}-STiming.csv
        cat  papi_time.csv  >> exp3_data/${NAME2}-PAPI.csv
        rm stiming_time.csv
        rm papi_time.csv
    done
done
