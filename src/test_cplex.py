from docplex.mp.model import Model


m = Model(name='single variable')
x = m.continuous_var(name="x", lb=0)
c1 = m.add_constraint(x >= 2, ctname="const1")
m.set_objective("min", 3 * x)
m.print_information()
m.solve()
m.print_solution()
print()

# Knapsack
w = [4, 2, 5, 4, 5, 1, 3, 5]
v = [10, 5, 18, 12, 15, 1, 2, 8]
C = 15
N = len(w)

knapsack_model = Model('knapsack')
x = knapsack_model.binary_var_list(N, name="x")
knapsack_model.add_constraint(sum(w[i] * x[i] for i in range(N)) <= C)
obj_fn = sum(v[i] * x[i] for i in range(N))
knapsack_model.set_objective("max", obj_fn)
knapsack_model.print_information()
sol = knapsack_model.solve()
knapsack_model.print_solution()
if sol is None:
    print("Infeasible")