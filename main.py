from pprint import pprint
import ast
from math import ceil
from flask import Flask, render_template
from get_related import get_related_papers, GraphVisualization
import requests
from concurrent.futures import ThreadPoolExecutor
# import time
from data import db_session
from data.graphs import Graph


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

db_session.global_init("db/graphs.db")
session = db_session.create_session()


@app.route("/")
def search_empty():
    return render_template("search-empty.html", title="PapersMatch", searchbar=False)


@app.route("/<query>/<int:page>")
def search(query, page):
    query = query.strip()
    # to delete/rework in the future!!!
    with open("searches.txt", "a", encoding='utf-8') as myfile:
        myfile.write(query + ' ' + str(page) + '\n')
    r = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&offset={(page-1)*20}&limit=20"
                     "&fields=title,authors,year,fieldsOfStudy,abstract,citationCount")
    results = r.json()['data'] if r.json()['total'] else []
    total_pages = min(ceil(r.json()['total'] / 20), 499)
    pages_array = []
    if total_pages < 6:
        pages_array = [x for x in range(1, total_pages + 1)]
    elif page < 4:
        pages_array = [1, 2, 3, 4, 5]
    elif page + 2 >= total_pages:
        pages_array = [total_pages - 4, total_pages - 3, total_pages - 2, total_pages - 1, total_pages]
    else:
        pages_array = [page - 2, page - 1, page, page + 1, page + 2]


    return render_template("search.html", results=results, query=query, pages_array=pages_array, total_pages=total_pages,
                           title="PapersMatch: " + query + ' | ' + str(r.json()['total']) + ' результатов', searchbar=False, count=len(results), page=page)


@app.route('/graph/<paper_id>')
def graph(paper_id):
    from_db = session.query(Graph).filter(Graph.paperId == paper_id).first()
    if not from_db:
        G = GraphVisualization()
        origin, related_to_root_list = get_related_papers(paper_id)
        id_to_paper = {paper_id: origin}
        G.addNode(paper_id)
        related_to_root_list = [rel for rel in related_to_root_list if rel['paperId']]
        for rel in related_to_root_list:
            id_to_paper[rel['paperId']] = rel  # save
            G.addEdge(paper_id, rel["paperId"])
        related_to_root_ids = [rel['paperId'] for rel in related_to_root_list]
        with ThreadPoolExecutor(max_workers=40) as pool:
            newrels = list(pool.map(get_related_papers, related_to_root_ids))
        for i in range(len(newrels)):
            for newrel in newrels[i][1]: # для ньюрела из списка релэйтедов к бумге newrels[i][0]
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
        # ЗАПИСАТЬ В БД НОВЫЙ ГРАФ
        new_gr = Graph(paperId=paper_id, articles=str(list(id_to_paper.values())), edges=str(gr.edges), origin=str(origin),
                       year1=years[0] if years else None, year2=years[-1] if years else None)
        session.add(new_gr)
        session.commit()
        # id_to_paper = связь ID со статьей id: {id, title, abstract, year, authors, citationCount, fieldsOfStudy}
        # gr = граф IDшек
        # node_list - список вершин (список ID)
        return render_template('graph.html', articles=id_to_paper.values(), edges=gr.edges, origin=origin,
                               minyear=years[0] if years else None, maxyear=years[-1] if years else None, title="Граф для " + origin['title'], searchbar=True)
    else:
        origin = ast.literal_eval(from_db.origin)
        return render_template('graph.html', articles=ast.literal_eval(from_db.articles), edges=ast.literal_eval(from_db.edges), origin=origin,
                               minyear=from_db.year1, maxyear=from_db.year2, title="Граф для " + origin['title'], searchbar=True)


@app.errorhandler(500)
def page_not_found(e):
    return '''Тут ничево нет. Иди назад.''', 500


app.run()
