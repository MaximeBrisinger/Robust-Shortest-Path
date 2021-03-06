from src.heuristic.inputgraph import InputGraph
from docplex.mp.model import Model
import time


class Ant:
    def __init__(self, nodes_explored: list):
        self.nodes = nodes_explored
        self.edges = self.get_edges()
        self.worst_cost = None

    def get_edges(self):
        return [(self.nodes[i], self.nodes[i + 1]) for i in range(len(self.nodes) - 1)]

    def is_finished(self, graph: InputGraph):
        return self.nodes[-1] == graph.t

    def get_weight(self, graph: InputGraph):
        return sum([graph.get_p(u) for u in self.nodes])

    def get_worst_augmentation(self, graph: InputGraph):
        md = Model()
        delta_2 = md.continuous_var_dict(self.nodes, lb=0, ub=2, name="delta_2")
        md.add_constraint(md.sum(delta_2[i] for i in self.nodes) <= graph.d2)

        md.set_objective("max", md.sum(delta_2[i] * graph.get_ph(i) for i in self.nodes))
        start = time.time()
        md.solve()
        execution_time = round(time.time() - start, 5)
        # md.print_solution()

        return md.objective_value

    def is_admissible(self, graph: InputGraph):
        maximum_augmentation = self.get_worst_augmentation(graph)
        maximum_weight = self.get_weight(graph)

        return maximum_augmentation + maximum_weight < graph.S, (maximum_augmentation + maximum_weight - graph.S) / graph.S

    def get_worst_cost(self, graph: InputGraph):
        # static_cost = sum([graph.get_d(i, j) for (i, j) in self.edges])

        md = Model()
        delta_1 = md.continuous_var_dict(self.edges, lb=0, name="delta_1")
        for (i, j) in self.edges:
            md.add_constraint(delta_1[i, j] <= graph.get_D(i, j), ctname="ub")
        md.add_constraint(md.sum(delta_1[i, j] for (i, j) in self.edges) <= graph.d1)

        md.set_objective("max", md.sum(graph.get_d(i, j) * (1 + delta_1[i, j]) for (i, j) in self.edges))
        start = time.time()
        md.solve()
        execution_time = round(time.time() - start, 5)
        # md.print_solution()

        self.worst_cost = md.objective_value

        return self.worst_cost


if __name__ == '__main__':
    file = "100_USA-road-d.NY.gr"
    data_folder = "../data/"

    input_graph = InputGraph(data_folder, file)
    s = time.time()
    print(input_graph.get_shortest_path(input_graph.s, input_graph.t))
    print(time.time() - s)

    # short_path = [74, 21, 3, 4, 10, 44, 59, 105]
    # short_path = [15, 4, 9, 2, 13, 20, 18]
    short_path = [51, 61, 20, 28, 71, 62, 55, 96]
    short_path = [51, 29, 4, 1, 2, 24, 55, 96]

    ant = Ant(short_path)
    print(ant.get_worst_cost(input_graph))
    print(ant.is_admissible(input_graph))
