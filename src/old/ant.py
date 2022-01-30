from src.old.inputgraph import InputGraph
from docplex.mp.model import Model
import time


class Ant:
    def __init__(self, nodes_explored: list):
        self.partial_solution = nodes_explored
        self.edges = self.get_edges()

    def get_edges(self):
        return [(self.partial_solution[i], self.partial_solution[i + 1]) for i in range(len(self.partial_solution) - 1)]

    def is_finished(self, graph: InputGraph):
        return self.partial_solution[-1] == graph.t

    def get_weight(self, graph: InputGraph):
        return sum([graph.get_p(u) for u in self.partial_solution])

    def get_worst_augmentation(self, graph: InputGraph):
        md = Model()
        delta_2 = md.continuous_var_dict(self.partial_solution, lb=0, ub=2, name="delta_2")
        md.add_constraint(md.sum(delta_2[i] for i in self.partial_solution) <= graph.d2)

        md.set_objective("max", md.sum(delta_2[i] * graph.get_ph(i) for i in self.partial_solution))
        start = time.time()
        md.solve()
        execution_time = round(time.time() - start, 5)
        # md.print_solution()

        print(f"time : {execution_time}")

        return md.objective_value

    def is_admissible(self, graph: InputGraph):
        maximum_augmentation = self.get_worst_augmentation(graph)
        maximum_weight = self.get_weight(graph)

        return maximum_augmentation + maximum_weight < graph.S

    def get_worst_cost(self, graph: InputGraph):
        # static_cost = sum([graph.get_d(i, j) for (i, j) in self.edges])

        md = Model()
        delta_1 = md.continuous_var_dict(self.edges, lb=0, name="delta_2")
        for (i, j) in self.edges:
            md.add_constraint(delta_1[i, j] <= graph.get_D(i, j), ctname="ub")
        md.add_constraint(md.sum(delta_1[i, j] for (i, j) in self.edges) <= graph.d1)

        md.set_objective("max", md.sum(graph.get_d(i, j) * (1 + delta_1[i, j]) for (i, j) in self.edges))
        start = time.time()
        md.solve()
        execution_time = round(time.time() - start, 5)
        # md.print_solution()

        print(f"time : {execution_time}")

        return md.objective_value


file = "20_USA-road-d.BAY.gr"
data_folder = "../data/"

graph = InputGraph(data_folder, file)
short_path = [15, 19, 1, 5, 17]
ant = Ant(short_path)
print(ant.get_worst_cost(graph))



