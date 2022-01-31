from src.old.inputgraph import InputGraph
from src.old.ant import Ant
from random import random
import numpy as np
import networkx as nx


class AntColony:
    def __init__(self, input_folder, input_file, nb_ants=None, t_max=5, time_limit=10):
        self.input_file = input_file
        self.t_max = t_max
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
            worst_cost = self.ants[k].get_worst_cost(self.graph)
            if not self.ants[k].is_admissible(self.graph):
                worst_cost *= self.penalization_infeasibility
            for edge in self.ants[k].edges:
                self.pheromones_k[edge][k] = self.Q / worst_cost

    def update_probabilities_k(self, k):
        self.probabilities[k] = {edge: 0 for edge in self.graph.edges}
        u = self.ants[k].nodes[-1]
        proba_sum = 0
        candidates = self.graph.get_next_nodes(u)
        for v in candidates:
            if self.graph.ut_distances[v] != 0:
                proba = (self.pheromones[(u, v)] ** self.alpha) * ((1 / self.graph.ut_distances[v]) ** self.beta)
            else:  # for case v = t
                proba = (self.pheromones[(u, v)] ** self.alpha) * ((1 / self.graph.min_distance / 2) ** self.beta)

            self.probabilities[k][(u, v)] = proba
            proba_sum += proba
        for v in candidates:
            self.probabilities[k][(u, v)] /= proba_sum
        return candidates

    def select_next_edge(self, k, candidates):
        cumulative_probability = 0
        r = random()
        print("PROBA")
        print(self.probabilities[k])
        for node in candidates:
            edge = (self.ants[k].nodes[-1], node)
            cumulative_probability += self.probabilities[k][edge]
            if cumulative_probability >= r:
                return edge

    def select_best_ant(self, verbose=True):
        costs = [ant.worst_cost for ant in self.ants]
        best_cost = min(costs)
        best_ant_index = costs.index(best_cost)
        best_ant = self.ants[best_ant_index]
        best_path = best_ant.nodes

        if verbose:
            print(f"Current best cost is {best_cost}, with path {best_path}")
        return best_path, best_cost

    def main(self):
        self.init_ants()
        self.update_pheromones_k()
        self.evaporation()

        best_path, best_cost = self.select_best_ant()

        for t in range(self.t_max):
            print(f"Iteration {t + 1} / {self.t_max}")
            for k in range(self.m):
                self.ants[k] = Ant([self.graph.s])
                count = 0
                while (not self.ants[k].is_finished(self.graph)) and count < self.graph.n:
                    candidates = self.update_probabilities_k(k)
                    next_edge = self.select_next_edge(k, candidates)
                    self.ants[k].edges.append(next_edge)
                    self.ants[k].nodes.append(next_edge[1])
                    count += 1
            self.update_pheromones_k()
            self.evaporation()
            best_path, best_cost = self.select_best_ant()

        return best_path, best_cost


if __name__ == '__main__':
    file = "20_USA-road-d.BAY.gr"
    data_folder = "../data/"
    ac = AntColony(data_folder, file)
    path, cost = ac.main()
