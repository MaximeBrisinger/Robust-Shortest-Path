#!/bin/bash

data_list=("data/40_USA-road-d.NY.gr") # "data/20_USA-road-d.NY.gr" "data/20_USA-road-d.COL.gr")

for file in ${data_list[@]}; do

    #julia main.jl --mode "Duality" --data $file --CPU_time_limit 100 > "logs/test.txt"
    #julia main.jl --mode "BranchAndCut" --data $file --CPU_time_limit 100 > "logs/test.txt"
    julia main.jl --mode "CuttingPlanes" --data $file --CPU_time_limit 30 > "logs/test.txt"
done