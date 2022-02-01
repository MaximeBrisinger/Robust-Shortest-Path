from src.old.inputgraph import InputGraph
from src.old.ant import Ant
from src.old.utils import save_results_csv
from random import random
import time
import numpy as np
import networkx as nx


class AntColony:
    def __init__(self, input_folder, input_file, nb_ants=None, t_max=5, time_limit=10):
        self.input_file = input_file
        self.t_max = t_max
        self.time_limit = time_limit
        self.graph = InputGraph(input_folder, input_file)

        self.m = nb_ants if nb_ants is not None else self.graph.n  # number of ants
        self.alpha = 0.9  # param for probability
        self.beta = 0.1  # param for probability
        self.Q = 10  # param for pheromones
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
            if not self.ants[k].is_finished(self.graph):
                worst_cost *= 100 * self.penalization_infeasibility
            for edge in self.ants[k].edges:
                self.pheromones_k[edge][k] = self.Q / worst_cost
            self.ants[k].worst_cost = worst_cost

    def update_probabilities_k(self, k):
        self.probabilities[k] = {edge: 0 for edge in self.graph.edges}
        u = self.ants[k].nodes[-1]
        proba_sum = 0
        candidates = self.graph.get_next_nodes(u)
        for v in candidates:
            if self.graph.ut_distances[v] != 0:
                proba = (self.pheromones[(u, v)] ** self.alpha) * ((1 / self.graph.ut_distances[v]) ** self.beta)
            else:  # for case v = t
                proba = (self.pheromones[(u, v)] ** self.alpha) * ((1 / self.graph.min_distance / 4) ** self.beta)

            self.probabilities[k][(u, v)] = proba
            proba_sum += proba
        for v in candidates:
            self.probabilities[k][(u, v)] /= proba_sum
        return candidates

    def select_next_edge(self, k, candidates):
        cumulative_probability = 0
        r = random()
        # print("PROBA")
        # print([(edge, self.probabilities[k][edge]) for edge in self.probabilities[k] if self.probabilities[k][edge] != 0])
        for node in candidates:
            edge = (self.ants[k].nodes[-1], node)
            cumulative_probability += self.probabilities[k][edge]
            if cumulative_probability >= r:
                return edge

    def select_best_ant(self, verbose=True):
        costs = []
        for ant in self.ants:
            if ant.is_finished(self.graph):
                costs.append(ant.worst_cost)
            else:
                costs.append(10e10)
        best_cost = min(costs)
        best_ant_index = costs.index(best_cost)
        best_ant = self.ants[best_ant_index]
        best_path = best_ant.nodes

        if verbose:
            print(f"Current best cost is {best_cost}, with path {best_path}")
        return best_path, best_cost

    def count_finished(self):
        nb_finished = sum([1 for k in range(self.m) if self.ants[k].is_finished(self.graph)])
        print(f"Nb finished : {nb_finished} / {self.m}")

    def main(self):
        self.init_ants()
        self.update_pheromones_k()
        self.evaporation()

        best_path_all, best_cost_all = self.select_best_ant()
        init_cost, init_path = best_cost_all, best_path_all
        self.count_finished()

        for t in range(self.t_max):
            print(f"\nIteration {t + 1} / {self.t_max}")
            for k in range(self.m):
                self.ants[k] = Ant([self.graph.s])
                count = 0
                while (not self.ants[k].is_finished(self.graph)) and count < self.graph.n:
                    candidates = self.update_probabilities_k(k)
                    next_edge = self.select_next_edge(k, candidates)
                    next_node = next_edge[1]
                    if next_node not in self.ants[k].nodes:
                        self.ants[k].edges.append(next_edge)
                        self.ants[k].nodes.append(next_edge[1])
                    else:  # delete cycles
                        node_index = self.ants[k].nodes.index(next_node)
                        self.ants[k].nodes = self.ants[k].nodes[:node_index + 1]
                        self.ants[k].edges = self.ants[k].get_edges()
                    count += 1
                if t == self.t_max - 1:
                    print(self.ants[k].nodes)
            self.update_pheromones_k()
            self.evaporation()

            best_path_t, best_cost_t = self.select_best_ant()
            if best_cost_t < best_cost_all:
                best_path_all, best_cost_all = best_path_t, best_cost_t

            self.count_finished()

        return best_path_all, best_cost_all, init_path, init_cost


if __name__ == '__main__':
    file = "60_USA-road-d.BAY.gr"
    # 12218
    data_folder = "../data/"

    start = time.time()
    ac = AntColony(data_folder, file, nb_ants=30, t_max=13)
    path, cost, initial_path, initial_cost = ac.main()
    total_time = round(time.time() - start, 2)

    print(f"\nBest cost is {cost}, with path {path}")
    print(f"\nInitial best cost was {initial_cost},  with path {initial_path}")
    print(f"\nExecution time : {total_time}s")

    save_results_csv(obj=cost,
                     time=total_time,
                     instance=file,
                     nb_ants=ac.m,
                     t_max=ac.t_max,
                     improve_init=bool(cost < initial_cost)
                     )
