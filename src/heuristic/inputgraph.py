from src.heuristic.utils import read_data, previous_nodes, next_nodes
import networkx as nx


class InputGraph:
    def __init__(self, data_folder, input_file):
        self.input_file = input_file

        params = read_data(data_folder, input_file)

        self.n = params["n"]
        self.s, self.t = params["s"], params["t"]
        self.S = params["S"]
        self.d1, self.d2 = params["d1"], params["d2"]
        self.p, self.ph = params["p"], params["ph"]
        self.d, self.D = params["d"], params["D"]

        self.edges = [(i + 1, j + 1) for i in range(self.n) for j in range(self.n) if self.d[i][j] != 0]
        self.nodes = [i for i in range(1, self.n + 1)]

        self.nx_graph = self.init_nx_graph()
        self.ut_distances = self.init_ut_distances()

        self.min_distance = sorted(self.ut_distances.items(), key=lambda item: item[1])[1][1]

    def init_nx_graph(self):
        graph = nx.DiGraph()
        for u in self.nodes:
            worst_weight = self.get_p(u) + 2 * self.get_ph(u)
            graph.add_node(u, weight=worst_weight)
        for (i, j) in self.edges:
            worst_cost = self.get_d(i, j) * (1 + self.get_D(i, j))
            graph.add_edge(i, j, weight=worst_cost)
        return graph

    def get_shortest_path(self, s, t):
        return nx.shortest_path(self.nx_graph, source=s, target=t, weight="weight")

    def init_ut_distances(self):
        ut_distances = {node: 0 for node in self.nodes}
        for u in self.nodes:
            ut_distances[u] = nx.shortest_path_length(self.nx_graph, source=u, target=self.t, weight="weight")
        return ut_distances

    def get_previous_nodes(self, node):
        return previous_nodes(self.edges, node)

    def get_next_nodes(self, node):
        return next_nodes(self.edges, node)

    def get_d(self, u, v):
        return self.d[u - 1, v - 1]

    def get_D(self, u, v):
        return self.D[u - 1, v - 1]

    def get_p(self, u):
        return self.p[u - 1]

    def get_ph(self, u):
        return self.ph[u - 1]

