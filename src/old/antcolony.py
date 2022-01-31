from src.old.inputgraph import InputGraph
from src.old.ant import Ant
import networkx as nx


class AntColony:
    def __init__(self, input_folder, input_file, nb_ants=None, time_limit=10):
        self.input_file = input_file
        self.time_limit = time_limit
        self.graph = InputGraph(input_folder, input_file)

        self.m = nb_ants if nb_ants is not None else self.graph.n  # number of ants
        self.alpha = 0.2  # param for probability
        self.beta = 0.2  # param for probability
        self.Q = 1  # param for pheromones
        self.rho = 0.3  # evaporation parameter

        self.penalization_infeasibility = 1.5

        self.ants = []

        self.pheromones = {edge: 0.1 for edge in self.graph.edges}
        self.pheromones_k = {edge: [0 for i in range(self.m)] for edge in self.graph.edges}
        self.probabilities = [{edge: 0 for edge in self.graph.edges} for i in range(self.m)]

    def init_ants(self):
        for i in range(self.m):
            u = self.graph.nodes[i]
            su = self.graph.get_shortest_path(self.graph.s, u)
            ut = self.graph.get_shortest_path(u, self.graph.t)
            st = su + ut[1:]
            self.ants.append(Ant(st))
            print(self.ants[-1].nodes)

    def evaporation(self):
        for edge in self.pheromones:
            self.pheromones[edge] = (1 - self.rho) * self.pheromones[edge] + sum(self.pheromones_k[edge])

    def update_pheromones_k(self):
        for k in range(self.m):
            worst_cost = self.ants[k].get_wors_cost(self.graph)
            if not self.ants[k].is_admissible():
                worst_cost *= self.penalization_infeasibility
            for edge in self.ants[k].edges:
                self.pheromones_k[edge][k] = self.Q / worst_cost

    def update_probabilities_k(self):
        for k in range(self.m):
            if not self.ants[k].is_finished():
                self.probabilities[k] = {edge: 0 for edge in self.graph.edges}
                u = self.ants[k].nodes[-1]
                proba_sum = 0
                candidates = self.graph.get_next_nodes(u)
                for v in candidates:
                    proba = (self.pheromones[(u, v)] ** self.alpha) * \
                            ((1 / self.graph.ut_distances[v]) ** self.beta)  # pb with v = t
                    self.probabilities[k][(u, v)] = proba
                    proba_sum += proba
                for v in candidates:
                    self.probabilities[k][(u, v)] /= proba_sum


if __name__ == '__main__':
    file = "20_USA-road-d.BAY.gr"
    data_folder = "../data/"
    ac = AntColony(data_folder, file)
    ac.init_ants()