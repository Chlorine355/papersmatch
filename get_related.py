import networkx as nx
import requests


# p_id = '37620f9e06ec42066b34d3047b3838323a566041'


def get_related_papers(paper_id):
    r = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}?fields=title,abstract,year,authors,"
                     f"fieldsOfStudy,"
                     f"citationCount,citations.citationCount,citations.title,citations.abstract,citations.year,"
                     f"citations.authors,citations.fieldsOfStudy,"
                     "references.citationCount,references.title,references.abstract,references.year,"
                     "references.authors,references.fieldsOfStudy").json()
    references = sorted(r['references'], key=lambda x: x['citationCount'] if x['citationCount'] else 0,
                        reverse=True)[:20]
    citations = sorted(r['citations'], key=lambda x: x['citationCount'] if x['citationCount'] else 0, reverse=True)[:20]
    del r['references']
    del r['citations']
    return r, references + citations


class GraphVisualization:
    def __init__(self):
        self.visual = []
        self.nodes = []

    def addEdge(self, a, b):
        temp = [a, b]
        self.visual.append(temp)

    def addNode(self, a):
        self.nodes.append(a)

    def get_graph(self):
        G = nx.Graph()
        G.add_edges_from(self.visual)
        G.add_nodes_from(self.nodes)
        if len(G.nodes) < 5:
            return G
        for limit in range(15, -1, -1):
            f = 1
            while f:
                f = 0
                for node in list(G.nodes):
                    if G.degree[node] < limit:
                        f = 1
                        G.remove_node(node)
            if len(G.nodes) == 0:
                G.add_edges_from(self.visual)
            else:
                if len(G.nodes) < 10 and len(G.nodes) != 1:
                    G.clear()
                    G.add_edges_from(self.visual)
                    continue
                break

        return G
