from docplex.mp.model import Model
import time
from src.utils import read_data, solve_and_display, previous_nodes, next_nodes, save_results

# import os

# os.environ["CPLEX_STUDIO_BINARIES"] = "C:/Program Files/IBM/ILOG/CPLEX_Studio1210/cplex/bin/x64_win64/"


def duality(file_name, time_limit):
    data_folder = "src/data/"
    params = read_data(data_folder, file_name)

    n = params["n"]
    s, t = params["s"], params["t"]
    S = params["S"]
    d1, d2 = params["d1"], params["d2"]
    p, ph = params["p"], params["ph"]
    d, D = params["d"], params["D"]

    edges = [(i + 1, j + 1) for i in range(n)
             for j in range(n) if d[i][j] != 0]
    nodes = [i for i in range(1, n + 1)]


    # Model with dual
    md = Model('dual')

    # Variables
    x = md.binary_var_dict(edges, name="x")
    y = md.binary_var_dict(nodes, name="y")
    z = md.continuous_var_dict(edges, lb=0, name="z")
    zprim = md.continuous_var_dict(nodes, lb=0, name="zprim")

    t1, t2 = md.continuous_var(name="t1", lb=0), md.continuous_var(name="t2", lb=0)

    # Constraints
    c_flow_s = md.add_constraint(md.sum(x[s, i] for i in next_nodes(edges, s)) == 1,
                                 ctname="constraint_flow_s")
    c_flow_t = md.add_constraint(md.sum(x[i, t] for i in previous_nodes(edges, t)) == 1,
                                 ctname="constraint_flow_t")

    md.add_constraint(y[t] == 1, ctname="constraint_def_y_t")  # error in the correction, to check..
    for v in nodes:
        if v not in (s, t):
            md.add_constraint(md.sum(x[v, i] for i in next_nodes(edges, v))
                              == md.sum(x[i, v] for i in previous_nodes(edges, v)),
                              ctname="constraint_flow_" + str(v))
        if v != t:
            md.add_constraint(y[v] == md.sum(x[v, j] for j in next_nodes(edges, v)),
                              ctname="constraint_def_y_" + str(v))

        md.add_constraint(t2 + zprim[v] >= ph[v - 1] * y[v], ctname="constraint_t2_zprim_" + str(v))

    for (i, j) in edges:
        md.add_constraint(t1 + z[i, j] >= d[i - 1, j - 1] * x[i, j], ctname=f"constraint_t1_x_{i}_{j}")

    md.add_constraint(t2 * d2 + md.sum(p[v - 1] * y[v] + 2 * zprim[v] for v in nodes) >= S,
                      ctname="constraint_S")

    # Objective
    obj_expression_d = md.sum(d[i - 1, j - 1] * x[i, j] for (i, j) in edges)
    obj_expression_D = md.sum(D[i - 1, j - 1] * z[i, j] for (i, j) in edges)

    md.set_objective("min", d1 * t1 + obj_expression_d + obj_expression_D)

    start = time.time()
    solve_and_display(md)
    execution_time = round(time.time() - start, 5)

    save_results(md.objective_value, execution_time, file_name, "duality")
