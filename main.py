import networkx as nx
from pyvis.network import Network
from networkx.algorithms.cluster import clustering
from networkx.algorithms.community import greedy_modularity_communities
from networkx.algorithms.bridges import bridges
import matplotlib.colors as mcolors
import os
import json

def loadtwolet(f):
    with open(f, "r") as p:
        return [x.strip() for x in p.readlines()]

def difbyone(w1, w2):
    if len(w1) != len(w2):
        return False
    return sum(1 for a, b in zip(w1, w2) if a != b) == 1

def makegraph(w):
    g = nx.Graph()
    for x in w:
        g.add_node(x)
    for i, w1 in enumerate(w):
        for w2 in w[i + 1:]:
            if difbyone(w1, w2):
                g.add_edge(w1, w2)
    for n in list(g.nodes):
        if g.degree[n] == 0:
            g.remove_node(n)
    return g

def maxdeg(graph, filename):
    mdw, md = max(graph.degree, key=lambda x: x[1], default=(None, 0))
    if mdw:
        neighbors = list(graph.neighbors(mdw))
        with open(filename, "w") as f:
            f.write(f"WORD {mdw} (DEGREE: {md})\n")
            f.write("CONNECTED words:\n")
            f.write("\n".join(neighbors))
    return mdw

def saven(graph, filename):
    nx.write_adjlist(graph, filename)

def findLongestLine(file_path, output_file):
    ml = 0
    mll = ""
    mln = 0

    with open(file_path, "r") as file:
        for ln, line in enumerate(file, start=1):
            ll = len(line)
            if ll > ml:
                ml = ll
                mll = line
                mln = ln

    with open(output_file, "w") as out_file:
        out_file.write(f"{mll.strip()}\n")

def viz(graph, config, outputFile):
    net = Network(notebook=True, height="800px", width="100%")
    net.from_nx(graph)
    com = list(greedy_modularity_communities(graph))
    pal = list(mcolors.TABLEAU_COLORS.keys())

    comcollor = {
        node: mcolors.to_rgb(pal[i % len(pal)])
        for i, community in enumerate(com) for node in community
    }
    maxDegree = max(dict(graph.degree()).values(), default=1)

    for node in net.nodes:
        nodeId = node['id']
        degree = graph.degree[nodeId]
        greenValue = int(255 - (degree / maxDegree) * 255)
        node['color'] = f"rgb(0, {greenValue}, 0)"
        if nodeId in comcollor:
            r, g, b = comcollor[nodeId]
            node['color'] = f"rgb({int(r * 255)}, {int(g * 255)}, {int(b * 255)})"
        node['value'] = degree

    for u, v in bridges(graph):
        for edge in net.edges:
            if (edge['from'] == u and edge['to'] == v) or (edge['from'] == v and edge['to'] == u):
                edge['color'] = 'red'
                edge['width'] = 4

    net.set_options(json.dumps(config))
    net.show(outputFile)

def words(num, config):
    folder = f"data/{num}"
    os.makedirs(folder, exist_ok=True)

    inpf = f"folder/{num}.txt"
    words = loadtwolet(inpf)

    graph = makegraph(words)

    mdf = f"{folder}/{num}.txt"
    maxdeg(graph, mdf)

    gf = f"{folder}/graph.adjlist"
    saven(graph, gf)

    llf = f"{folder}/{num}_longest.txt"
    findLongestLine(gf, llf)

    ghf = f"{folder}/graph.html"
    viz(graph, config, ghf)

def main():

    with open("config.json", "r") as f:
        config = json.load(f)

    for num in range(2, 23):
        words(num, config)

if __name__ == "__main__":
    main()