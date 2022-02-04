#!/bin/bash

data_list=("data/350_USA-road-d.BAY.gr"  "data/350_USA-road-d.NY.gr" "data/350_USA-road-d.COL.gr" "data/400_USA-road-d.BAY.gr"  "data/400_USA-road-d.NY.gr" "data/400_USA-road-d.COL.gr")

for file in ${data_list[@]}; do

    julia main.jl --mode "Duality" --data $file --CPU_time_limit 100 > "logs/test.txt"
    # julia main.jl --mode "BranchAndCut" --data $file --CPU_time_limit 100 > "logs/test.txt"
    # julia main.jl --mode "CuttingPlanes" --data $file --CPU_time_limit 30 > "logs/test.txt"
done