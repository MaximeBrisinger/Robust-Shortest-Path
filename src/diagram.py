import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

results_folder = "saves/"
methods = ["heuristic", "BC", "CP", "dual"]
files = [(results_folder + "benchmark_" + method + ".csv") for method in methods]


def read_heuristic(file):
    data = pd.read_csv(file)
    data = data[["path", "Objective value", "Time to best value (s)"]]
    data = data.to_numpy()
    return data


def read_exact(file):
    data = pd.read_csv(file)
    data = data[["path", "Objective value", "termination status", "Time (s)"]]
    data = data.to_numpy()
    return data


def keep_optimal(data):
    for line in data:
        if not line["termination status"]:
            line["Time (s)"] = 10e3
    print(data)
    return data


def numpy_to_plot(methods, time):
    plt.figure("Diagramme de performances", figsize=(13, 13))
    for method in methods:
        data = methods[method]
        if data is not None:
            y = []
            times = data[:, -1]
            for t in time:
                y.append(sum(times <= t))
            plt.step(time, y, label=method)

    plt.xlabel("Temps (s)")
    plt.ylabel("Nombre d'instances résolues")
    plt.legend(loc='upper right')
    plt.show()


# Time steps
time = np.linspace(0, 20, 40)

# Read data
heuristic = read_heuristic(files[0])
bc = read_exact(files[1])
cp = read_exact(files[2])
dual = read_exact(files[3])

methods = {
    "Heuristic": heuristic,
    "Branch & Cut": bc,
    "Cutting Planes": None,
    "Dual": dual
}

# Plot
numpy_to_plot(methods, time)
