#!/bin/bash -x

cp ../stencil/stencil.c ./exp1.c
mkdir exp1_data

NT=10
for narr in 256 4000
do
    mpicc -o t1_stiming_C${narr}.x -DNTEST=${NT} -DNARR=${narr} -DSTIMING ./exp1.c
    mpicc -o t1_papi_C${narr}.x -DNTEST=${NT} -DNARR=${narr} -DPAPI ./exp1.c -lpapi
done

for i in {1..10}
do
    
    for narr in 256 4000
    do
        NAME=TL_CALC_W-C$narr
	rm stiming*.csv
	rm papi*.csv
        mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./t1_stiming_C${narr}.x
        mpirun --mca mtl psm2 --mca btl vader,self --map-by core --bind-to core -np 40 ./t1_papi_C${narr}.x
    
        cat stiming_time.csv     >> exp1_data/${NAME}-STiming.csv
        cat stiming_tot_time.csv >> exp1_data/${NAME}-STiming-tot.csv
        cat papi_time.csv        >> exp1_data/${NAME}-PAPI.csv
        cat papi_tot_time.csv    >> exp1_data/${NAME}-PAPI-tot.csv
    done
done
