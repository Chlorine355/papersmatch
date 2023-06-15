from flask import Flask, render_template
from get_related import get_related_papers, GraphVisualization
import requests
from concurrent.futures import ThreadPoolExecutor
import networkx as nx
from pprint import pprint


app = Flask(__name__)


@app.route("/")
def search_empty():
    # r = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&offset=00&limit=20"
    #                  "&fields=title,authors,year,fieldsOfStudy,abstract,citationCount")
    return render_template("search-empty.html")


@app.route("/<query>")
def search(query):
    r = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&offset=00&limit=20"
                     "&fields=title,authors,year,fieldsOfStudy,abstract,citationCount")
    return render_template("search.html", results=r.json()['data'] if r.json()['total'] else [], query=query)


@app.route('/graph/<paper_id>')
def graph(paper_id):
    G = GraphVisualization()

    origin, related_to_root_list = get_related_papers(paper_id)
    id_to_paper = {paper_id: origin}
    G.addNode(paper_id)
    related_to_root_list = [rel for rel in related_to_root_list if rel['paperId']]
    for rel in related_to_root_list:
        id_to_paper[rel['paperId']] = rel  # save
        G.addEdge(paper_id, rel["paperId"])
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

    years = sorted([article['year'] for article in id_to_paper.values() if article['year'] is not None])
    # id_to_paper = связь ID со статьей id: {title, abstract, year, authors, citationCount, fieldsOfStudy}
    # gr = граф IDшек
    # node_list - список вершин (список ID)
    return render_template('graph.html', articles=id_to_paper.values(), edges=gr.edges, origin=origin, minyear=years[0],
                           maxyear=years[-1])


app.run()
