import numpy as np
import json
from pathlib import Path
import csv


def read_data(data_folder, file_name):
    file = data_folder + file_name

    n = int(file_name.split("_")[0])
    file = Path(file)
    dij = np.zeros((n, n))
    Dij = np.zeros((n, n))

    dict_data = dict()
    dict_data["n"] = n

    lines = []
    with open(file) as f:
        lines += f.readlines()
    matrix = "Mat"
    for line in lines:
        if " = " in line and matrix not in line:
            line_split = line.split(" = ")
            param_name = line_split[0]
            value = line_split[1]
            if "[" not in value:
                value = int(value)
            else:
                value = value.replace("[", "").replace("]", "")
                list_values = value.split(",")
                value = [int(val) for val in list_values]

            dict_data[param_name] = value
        else:
            if " = " not in line:
                line_split = line.replace(";", "").replace("]", "").split(" ")
                i, j, d, D = line_split
                i, j = int(i) - 1, int(j) - 1
                dij[i][j] = int(d)
                Dij[i][j] = float(D)

    dict_data["d"] = dij
    dict_data["D"] = Dij
    return dict_data


def solve_and_display(model):
    model.print_information()
    md_solve = model.solve()
    model.print_solution()
    print()
    return md_solve


def next_nodes(edges, i):
    delta_plus_i = list()
    for a in edges:
        if a[0] == i:
            delta_plus_i.append(a[1])
    return delta_plus_i


def previous_nodes(edges, i):
    delta_minus_i = list()
    for a in edges:
        if a[1] == i:
            delta_minus_i.append(a[0])
    return delta_minus_i


def save_results(obj, time, instance, method):
    summary = {
        "objective": obj,
        "time": time,
        "method": method
    }

    results_folder = f"src/results/{instance}/"
    root = Path(results_folder)

    results_file = results_folder + f"{method}.json"
    root_file = Path(results_file)

    if not root.exists():
        root.mkdir(parents=True)
    if root_file.exists():
        raise ValueError(f'File {root_file} already exists.')

    with open(root_file, 'w+') as outfile:
        json.dump(summary, outfile, indent=4, sort_keys=True)


def save_results_csv(obj, time, instance, nb_ants, t_max, improve_init, termination_status):
    summary = {
        "Objective value": round(obj, 2),
        "Time (s)": round(time, 2),
        "path": instance,
        "Number ants": nb_ants,
        "Number iterations": t_max,
        "Improve initial": improve_init,
        "Termination status": termination_status
    }

    results_folder = f"../results/benchmark_heuristic.csv"
    root = Path(results_folder)

    with open(root, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=summary.keys())

        # writer.writeheader()
        writer.writerow(summary)
