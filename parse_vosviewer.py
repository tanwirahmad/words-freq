import sys
import codecs
import re
import csv
import pygraphviz as pgv    
from collections import defaultdict
from argparse import ArgumentParser

g_colors = [
    "red",
    "aquamarine4",
    "azure4",
    "bisque3",
    "blue1",
    "brown",
    "burlywood",
    "cadetblue",
    "chartreuse",
    "chocolate",
    "coral",
    "cornflowerblue",
    "cornsilk4",
    "cyan3",
    "darkgoldenrod3",
    "darkolivegreen1",
    "darkorange1",
    "darkorchid1",
    "darkseagreen",
    "darkslateblue",
    "darkslategray4",
    "deeppink1"
    ]

# ===================== Loading a User Model ============   
parser = ArgumentParser()

parser.add_argument("corpus", help="Path of a corpus file")

parser.add_argument("map", help="Path of a VOSViewer map file")

parser.add_argument("network", help="Path of a VOSViewer network file")

parser.add_argument("-i", help="Show only intercluster edges in the graph. Default is False", dest="show_intercluster_edges", action="store_true", default=False)

args = parser.parse_args()

input_file =  args.corpus # "megamart_dragos_corpus.txt" #sys.argv[1]
map_file =  args.map #"megamart_dragos_map.txt" #sys.argv[1]
network_file =  args.network #"megamart_dragos_network.txt" #sys.argv[1]
show_only_intercluster_edge = args.show_intercluster_edges #True
A=pgv.AGraph(layout='dot', splines=True, overlap=True,
                    nodesep=0.6)
color_idx = 0

pat_non_alphabets = re.compile("[^a-zA-Z0-9_\s]")

def remove_non_alphbets(text):
    new_text = re.sub(pat_non_alphabets, '', text)
    return new_text


# This dict will hold the clusters of different key terms
cluster_of_keys = {}

# Reading the map file
docs_map = {}
with open(map_file, 'rb') as csvfile:
    reader = csv.reader(csvfile, dialect='excel-tab')
    skip_header = True
    for row in reader:
        if skip_header:
            skip_header= False
            continue
        docs_map[row[0]] = {
            'term': row[1], 
            'cluster':row[4], 
            'weight':row[5], 
            'weight_total':row[6], 
            'docs':[],
            'graph_node': None,
            'docs_node_name': ''
            }

# Reading documents in the corpus file
with codecs.open(input_file, 'r', 'utf-8') as fp:
    raw_abstracts = fp.readlines()

# Map the documents to the cluster by searching the terms in the document
#new_abstracts = []
for n, abs in enumerate(raw_abstracts):
    ntext = remove_non_alphbets(abs.lower())
    #new_abstracts.append(ntext)
    for id in docs_map:
        term = docs_map[id]["term"]
        if re.search(term, ntext):
            docs_map[id]['docs'].append(n)

# Building a Graph structure to represent cluster information collected above
for id in docs_map:
    # If we already have formed the cluster for this particular cluster ID
    cluster_id = docs_map[id]["cluster"]
    term = docs_map[id]["term"]

    if cluster_id in cluster_of_keys:
        cluster = cluster_of_keys[cluster_id]
    else:
        cluster =  A.add_subgraph([], 
                    name="cluster_" + cluster_id, 
                    color=g_colors[color_idx],
                    label="cluster " + cluster_id)
        cluster_of_keys[cluster_id] = cluster
        color_idx += 1

    
    term_cluster_name = "cluster_" + term
    docs_node_name = ', '.join(map(str, docs_map[id]["docs"]))

    cluster.add_node(docs_node_name)
    docs_map[id]["graph_node"] = cluster.add_subgraph([docs_node_name,], name=term_cluster_name, label=term)
    docs_map[id]["docs_node_name"] = docs_node_name

# Connecting edges among clusters based on the network file
with open(network_file, 'rb') as csvfile:
    reader = csv.reader(csvfile, dialect='excel-tab')
    skip_header = True
    for row in reader:
        if skip_header:
            skip_header= False
            continue

        
        src_node =  docs_map[row[0]]["docs_node_name"]
        dst_node =  docs_map[row[1]]["docs_node_name"]
        weight = row[2]

        if not show_only_intercluster_edge or (docs_map[row[0]]["cluster"] != docs_map[row[1]]["cluster"]):
            A.add_edge(src_node, dst_node, penwidth=weight)

# Reading information from the Cluster Graph and presenting it in a textual format
for cluster in A.subgraphs():
    print cluster.graph_attr["label"]

    terms_in_cluster = [(term.graph_attr["label"], term.nodes()[0], len(term.nodes()[0].split(','))) for term in cluster.subgraphs()]
    terms_in_cluster.sort(key=lambda tup: tup[2], reverse=True) 

    for label, docs, freq in terms_in_cluster:
        print "\t{}:{}".format(label, freq)
        print "\tDocs: {}\n".format(docs)
    #print "\n"

print "Exporting cluster graph as an image file..."
#print A.string()
A.draw('words.png', prog='neato')