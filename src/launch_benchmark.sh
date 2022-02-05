#!/bin/bash

#data_list=("data/350_USA-road-d.BAY.gr"  "data/350_USA-road-d.NY.gr" "data/350_USA-road-d.COL.gr" "data/400_USA-road-d.BAY.gr"  "data/400_USA-road-d.NY.gr" "data/400_USA-road-d.COL.gr")
dest_list=("NY" "COL" "BAY") #("NY" "COL" "BAY") # "data/400_USA-road-d.BAY.gr"  "data/400_USA-road-d.NY.gr" "data/400_USA-road-d.COL.gr")
list_n=("700" "750") #("20" "40" "60" "80" "100" "120" "140" "160" "180" "200" "250" "350" "400" "450" "500" "550" "600" "650" "700""750" "800" "850" "900" "950" "1000" "1100" "1200") #("20" "40" "60" "80" "100" "120" "140" "160" "180" "200" "250" "350" "400" "450" "500" "550" "600" "650" "700")
method_list=("Static") #CuttingPlanesFloat") #("BranchAndCut" "CuttingPlanesInt" "CuttingPlanesFloat")

for dest in ${dest_list[@]}; do
    for method in ${method_list[@]}; do
        for n in ${list_n[@]}; do
            echo "$method $n $dest"
            julia main.jl --mode $method --data "data/${n}_USA-road-d.${dest}.gr" --CPU_time_limit 100 > "logs/${method}_${n}_${dest}.txt"
        done
    done
done

list_n=("1300" "1400" "1500" "1600" "1700" "1800" "1900" "2000") #("20" "40" "60" "80" "100" "120" "140" "160" "180" "200" "250" "350" "400" "450" "500" "550" "600" "650" "700")
method_list=("Duality") #CuttingPlanesFloat") #("BranchAndCut" "CuttingPlanesInt" "CuttingPlanesFloat")

for dest in ${dest_list[@]}; do
    for method in ${method_list[@]}; do
        for n in ${list_n[@]}; do
            echo "$method $n $dest"
            julia main.jl --mode $method --data "data/${n}_USA-road-d.${dest}.gr" --CPU_time_limit 100 > "logs/${method}_${n}_${dest}.txt"
        done
    done
done