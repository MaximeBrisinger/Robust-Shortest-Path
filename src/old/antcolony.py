from src.old.inputgraph import InputGraph
from src.old.ant import Ant


class AntColony:
    def __init__(self, input_folder, input_file, time_limit):
        self.input_file = input_file
        self.time_limit = time_limit
        self.graph = InputGraph(input_folder, input_file)

        self.alpha = 0.2  # param for probability
        self.beta = 0.2  # param for probability
        self.Q = 1  # param for pheromones

        self.ants = []
        self.nb_ants = 10

        self.pheromones = {edge: 0.1 for edge in self.graph.edges}

    # pour le coût, on peut ajouter min(sum(Dij), d1)

    def init_ants(self):
        for i in range(self.nb_ants):
            self.ants.append(Ant(self.graph.s))
