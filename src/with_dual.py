from docplex.mp.model import Model



# Model with dual
md = Model('knapsack')
x = md.binary_var_list(N, name="x")