#!/bin/bash

data_list=("data/20_USA-road-d.COL.gr" "data/20_USA-road-d.NY.gr" "data/20_USA-road-d.BAY.gr")

for file in ${data_list[@]}; do

    julia main.jl --mode "Duality" --data $file --CPU_time_limit 100 > "logs/test.txt"
    julia main.jl --mode "BranchAndCut" --data $file --CPU_time_limit 100 > "logs/test.txt"
    julia main.jl --mode "CuttingPlanes" --data $file --CPU_time_limit 100 > "logs/test.txt"
done