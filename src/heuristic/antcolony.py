from src.heuristic.inputgraph import InputGraph
from src.heuristic.ant import Ant
from src.heuristic.utils import save_results_csv
import random
import time
import numpy as np
import networkx as nx


class AntColony:
    def __init__(self, input_folder, input_file, nb_ants, t_max=5, time_limit=10):
        self.input_file = input_file
        self.t_max = t_max
        self.time_limit = time_limit
        self.graph = InputGraph(input_folder, input_file)

        self.m = min(nb_ants, self.graph.n)  # number of ants
        self.alpha = 1  # param for probability (pheromones weight)
        self.beta = 0.8  # param for probability (distance weight)
        self.Q = 1000 / self.m  # param for pheromones
        self.rho = 0.3  # evaporation parameter

        self.penalization_infeasibility = 1.5

        self.ants = []
        self.pheromones = {edge: 30 / len(self.graph.edges) for edge in self.graph.edges}
        self.pheromones_k = {edge: [0 for i in range(self.m)] for edge in self.graph.edges}
        self.probabilities = [{edge: 0 for edge in self.graph.edges} for i in range(self.m)]

        self.interrupted = False

    def init_ants(self):
        nodes = [node for node in self.graph.nodes]
        random.shuffle(nodes)
        if self.graph.s not in nodes[:self.m]:
            nodes[0] = self.graph.s
        for i in range(self.m):
            u = nodes[i]
            su = self.graph.get_shortest_path(self.graph.s, u)
            ut = self.graph.get_shortest_path(u, self.graph.t)
            st = su + ut[1:]
            self.ants.append(Ant(st))
            print(self.ants[-1].nodes)

    def evaporation(self):
        for edge in self.pheromones:
            self.pheromones[edge] = (1 - self.rho) * self.pheromones[edge] + sum(self.pheromones_k[edge])

    def update_pheromones_k(self):
        self.pheromones_k = {edge: [0 for i in range(self.m)] for edge in self.graph.edges}
        for k in range(self.m):
            worst_cost = self.ants[k].get_worst_cost(self.graph)
            admissible, gap = self.ants[k].is_admissible(self.graph)
            if not admissible:
                worst_cost *= (self.penalization_infeasibility + gap)
            if not self.ants[k].is_finished(self.graph):
                worst_cost *= 100 * self.penalization_infeasibility
            for edge in self.ants[k].edges:
                self.pheromones_k[edge][k] = self.Q / worst_cost
            self.ants[k].worst_cost = worst_cost

    def cost_select_node(self, u):
        c = self.graph.ut_distances[u]
        worst_weight = self.graph.nx_graph.nodes[u]["weight"]
        return (c + 400 * worst_weight) / 2

    def update_probabilities_k(self, k):
        self.probabilities[k] = {edge: 0 for edge in self.graph.edges}
        u = self.ants[k].nodes[-1]
        proba_sum = 0
        candidates = self.graph.get_next_nodes(u)
        for v in candidates:
            if self.graph.ut_distances[v] != 0:
                proba = (self.pheromones[(u, v)] ** self.alpha) * ((1 / self.cost_select_node(v)) ** self.beta)
            else:  # for case v = t
                proba = (self.pheromones[(u, v)] ** self.alpha) * ((1 / self.graph.min_distance / 4) ** self.beta)

            self.probabilities[k][(u, v)] = proba
            proba_sum += proba
        for v in candidates:
            self.probabilities[k][(u, v)] /= proba_sum
        return candidates

    def select_next_edge(self, k, candidates):
        cumulative_probability = 0
        r = random.random()
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
            if ant.is_finished(self.graph) and ant.is_admissible(self.graph)[0]:
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
        nb_finished = len([1 for k in range(self.m) if self.ants[k].is_finished(self.graph)])
        print(f"Nb finished : {nb_finished} / {self.m}")

    def count_admissible(self):
        paths_admissible = [1 for k in range(self.m) if
                            self.ants[k].is_admissible(self.graph)[0] and self.ants[k].is_finished(self.graph)]
        nb_admissible = len(paths_admissible)
        print(f"Nb admissible : {nb_admissible}")

    def main(self):
        start_time = time.time()

        self.init_ants()
        # self.ants = [None for i in range(self.m)]
        self.update_pheromones_k()
        self.evaporation()

        best_path_all, best_cost_all = self.select_best_ant()
        # best_path_all, best_cost_all = 100000, 100000
        init_cost, init_path = best_cost_all, best_path_all
        time_for_best_value = round(time.time() - start_time, 2)

        self.count_finished()
        self.count_admissible()

        admissibles = []

        for t in range(self.t_max):
            if time.time() - start_time > self.time_limit:
                self.interrupted = True
                break

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

                if self.ants[k].is_admissible(self.graph)[0] \
                        and self.ants[k].is_finished(self.graph) and self.ants[k].nodes not in admissibles:
                    admissibles.append(self.ants[k].nodes)

                if t == self.t_max - 1:
                    print(self.ants[k].nodes)

            self.update_pheromones_k()
            self.evaporation()
            print(max(self.pheromones.values()))
            print(min(self.pheromones.values()))

            best_path_t, best_cost_t = self.select_best_ant()
            if best_cost_t < best_cost_all:
                best_path_all, best_cost_all = best_path_t, best_cost_t
                time_for_best_value = round(time.time() - start_time, 2)

            self.count_finished()
            self.count_admissible()

        print(f"Nb different admissible path : {len(admissibles)}")
        # print(np.array(admissibles))
        total_time = round(time.time() - start_time, 2)
        return best_path_all, best_cost_all, init_path, init_cost, total_time, time_for_best_value


if __name__ == '__main__':
    file = "700_USA-road-d.NY.gr"

    data_folder = "../data/"
    # 12218

    # "100_USA-road-d.COL.gr" : 1 / 0.8 / 1000 / 0.3 / 30/len / 40ants / 20tmax / c + 400* / no init
    # .........NY : nul
    # 12/....NY : ok

    ac = AntColony(input_folder=data_folder,
                   input_file=file,
                   nb_ants=30,
                   t_max=15,
                   time_limit=60)

    path, cost, initial_path, initial_cost, total_time, time_for_best_value = ac.main()

    print(f"\nBest cost is {cost}, with path {path}")
    print(f"\nInitial best cost was {initial_cost}, with path {initial_path}")
    print(f"\nExecution time : {total_time}s")
    print(f"\nTime to reach best value : {time_for_best_value}s")

    save_results_csv(obj=cost,
                     time=total_time,
                     time_best=time_for_best_value,
                     instance=file,
                     nb_ants=ac.m,
                     t_max=ac.t_max,
                     improve_init=bool(cost < initial_cost),
                     termination_status=(not ac.interrupted)
                     )

# todo : au lieu de laisser les cycle et les virer, direct mettre proba à 0 dans le choix du next node