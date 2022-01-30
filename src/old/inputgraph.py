from src.old.utils import read_data, previous_nodes, next_nodes


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

