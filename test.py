from pprint import pprint
import requests
from concurrent.futures import ThreadPoolExecutor
import networkx as nx
import matplotlib.pyplot as plt


p_id = '37620f9e06ec42066b34d3047b3838323a566041'


def get_related_papers(paper_id):
    r = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}?fields=title,abstract,year,authors,fieldsOfStudy,"
                     f"citationCount,citations.citationCount,citations.title,citations.abstract,citations.year,"
                     f"citations.authors,citations.fieldsOfStudy,"
                     "references.citationCount,references.title,references.abstract,references.year,references.authors,references.fieldsOfStudy").json()
    references = sorted(r['references'], key=lambda x: x['citationCount'] if x['citationCount'] else 0, reverse=True)[:20]
    citations = sorted(r['citations'], key=lambda x: x['citationCount'] if x['citationCount'] else 0, reverse=True)[:20]
    del r['references']
    del r['citations']
    return r, references + citations


class GraphVisualization:
    def __init__(self):
        self.visual = []

    def addEdge(self, a, b):
        temp = [a, b]
        self.visual.append(temp)

    def get_graph(self):
        G = nx.Graph()
        G.add_edges_from(self.visual)
        for limit in range(15, -1, -1):
            f = 1
            while f:
                f = 0
                for node in list(G.nodes):
                    if G.degree[node] < limit:
                        f = 1
                        G.remove_node(node)
            if len(G.nodes) == 0:
                print(limit)
                G.add_edges_from(self.visual)
            else:
                if len(G.nodes) < 10 and len(G.nodes) != 1:
                    G.clear()
                    G.add_edges_from(self.visual)
                    continue
                break

        return G


G = GraphVisualization()

origin, related_to_root_list = get_related_papers(p_id)
pprint(origin)
id_to_paper = {p_id: origin}
related_to_root_list = [rel for rel in related_to_root_list if rel['paperId']]
for rel in related_to_root_list:
    id_to_paper[rel['paperId']] = rel # save
    G.addEdge(p_id, rel["paperId"])
new_ids = []
related_to_root_ids = [rel['paperId'] for rel in related_to_root_list]

with ThreadPoolExecutor(max_workers=50) as pool:
    newrels = list(pool.map(get_related_papers, related_to_root_ids))


for i in range(len(newrels)):
    for newrel in newrels[i][1]:
        if newrel['paperId']:
            id_to_paper[newrel['paperId']] = newrel
            G.addEdge(related_to_root_ids[i], newrel['paperId'])

gr = G.get_graph()
node_list = list(gr.nodes)
all_keys = list(id_to_paper.keys())
for key in all_keys:
    if key not in node_list:
        del id_to_paper[key]
print("Записей в словаре:", len(id_to_paper))
print("Вершин в графе:", len(node_list))
for edge in gr.edges:
    print(edge[0], edge[1])

# id_to_paper = связь ID со статьей id: {title, abstract, year, authors, citationCount, fieldsOfStudy}
# gr = граф IDшек
# node_list - список вершин (список ID)
