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


def sort_csv(data):
    df = pd.DataFrame(data, index=data[:, 0])
    list_files = ['20_USA-road-d.BAY.gr', '20_USA-road-d.COL.gr', '20_USA-road-d.NY.gr', '40_USA-road-d.BAY.gr', '40_USA-road-d.COL.gr', '40_USA-road-d.NY.gr', '60_USA-road-d.BAY.gr', '60_USA-road-d.COL.gr', '60_USA-road-d.NY.gr', '80_USA-road-d.BAY.gr', '80_USA-road-d.COL.gr', '80_USA-road-d.NY.gr', '100_USA-road-d.BAY.gr', '100_USA-road-d.COL.gr', '100_USA-road-d.NY.gr', '120_USA-road-d.BAY.gr', '120_USA-road-d.COL.gr', '120_USA-road-d.NY.gr', '140_USA-road-d.BAY.gr', '140_USA-road-d.COL.gr', '140_USA-road-d.NY.gr', '160_USA-road-d.BAY.gr', '160_USA-road-d.COL.gr', '160_USA-road-d.NY.gr', '180_USA-road-d.BAY.gr', '180_USA-road-d.COL.gr', '180_USA-road-d.NY.gr', '200_USA-road-d.BAY.gr', '200_USA-road-d.COL.gr', '200_USA-road-d.NY.gr', '250_USA-road-d.BAY.gr', '250_USA-road-d.COL.gr', '250_USA-road-d.NY.gr', '300_USA-road-d.BAY.gr', '300_USA-road-d.COL.gr', '300_USA-road-d.NY.gr', '350_USA-road-d.BAY.gr', '350_USA-road-d.COL.gr', '350_USA-road-d.NY.gr', '400_USA-road-d.BAY.gr', '400_USA-road-d.COL.gr', '400_USA-road-d.NY.gr', '450_USA-road-d.BAY.gr', '450_USA-road-d.COL.gr', '450_USA-road-d.NY.gr', '500_USA-road-d.BAY.gr', '500_USA-road-d.COL.gr', '500_USA-road-d.NY.gr', '550_USA-road-d.BAY.gr', '550_USA-road-d.COL.gr', '550_USA-road-d.NY.gr', '600_USA-road-d.BAY.gr', '600_USA-road-d.COL.gr', '600_USA-road-d.NY.gr', '650_USA-road-d.BAY.gr', '650_USA-road-d.COL.gr', '650_USA-road-d.NY.gr', '700_USA-road-d.BAY.gr', '700_USA-road-d.COL.gr', '700_USA-road-d.NY.gr', '750_USA-road-d.BAY.gr', '750_USA-road-d.COL.gr', '750_USA-road-d.NY.gr', '800_USA-road-d.BAY.gr', '800_USA-road-d.COL.gr', '800_USA-road-d.NY.gr', '850_USA-road-d.BAY.gr', '850_USA-road-d.COL.gr', '850_USA-road-d.NY.gr', '900_USA-road-d.BAY.gr', '900_USA-road-d.COL.gr', '900_USA-road-d.NY.gr', '950_USA-road-d.BAY.gr', '950_USA-road-d.COL.gr', '950_USA-road-d.NY.gr', '1000_USA-road-d.BAY.gr', '1000_USA-road-d.COL.gr', '1000_USA-road-d.NY.gr', '1100_USA-road-d.BAY.gr', '1100_USA-road-d.COL.gr', '1100_USA-road-d.NY.gr', '1200_USA-road-d.BAY.gr', '1200_USA-road-d.COL.gr', '1200_USA-road-d.NY.gr', '1300_USA-road-d.BAY.gr', '1300_USA-road-d.COL.gr', '1300_USA-road-d.NY.gr', '1400_USA-road-d.BAY.gr', '1400_USA-road-d.COL.gr', '1400_USA-road-d.NY.gr', '1500_USA-road-d.BAY.gr', '1500_USA-road-d.COL.gr', '1500_USA-road-d.NY.gr', '1600_USA-road-d.BAY.gr', '1600_USA-road-d.COL.gr', '1600_USA-road-d.NY.gr', '1700_USA-road-d.BAY.gr', '1700_USA-road-d.COL.gr', '1700_USA-road-d.NY.gr', '1800_USA-road-d.BAY.gr', '1800_USA-road-d.COL.gr', '1800_USA-road-d.NY.gr', '1900_USA-road-d.BAY.gr', '1900_USA-road-d.COL.gr', '1900_USA-road-d.NY.gr', '2000_USA-road-d.BAY.gr', '2000_USA-road-d.COL.gr', '2000_USA-road-d.NY.gr', '2100_USA-road-d.BAY.gr', '2100_USA-road-d.COL.gr', '2100_USA-road-d.NY.gr', '2200_USA-road-d.BAY.gr', '2200_USA-road-d.COL.gr', '2200_USA-road-d.NY.gr', '2300_USA-road-d.BAY.gr', '2300_USA-road-d.COL.gr', '2300_USA-road-d.NY.gr', '2400_USA-road-d.BAY.gr', '2400_USA-road-d.COL.gr', '2400_USA-road-d.NY.gr', '2500_USA-road-d.BAY.gr', '2500_USA-road-d.COL.gr', '2500_USA-road-d.NY.gr']
    new_data = [["path", "Objective value", "termination status", "Time (s)"]]
    for file in list_files:
        full_name = "data/" + file
        if full_name in df[0]:
            values = list(df.loc[full_name].values)
        else:
            values = [full_name, False, False, False]
        new_data.append(values)
    df = pd.DataFrame(new_data[1:], columns=new_data[0], index=None)
    print(df)
    df.to_csv("dual.csv")
    exit()


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

# To sort csv
# sort_csv(dual)