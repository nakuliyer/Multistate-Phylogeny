from typing import Set
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


def draw_graph_f(T: nx.DiGraph):
    pos = nx.spring_layout(T)
    edge_labels = nx.get_edge_attributes(T, 'label')
    nx.draw(T, pos, with_labels=True)
    nx.draw_networkx_edge_labels(T, pos, edge_labels=edge_labels)
    plt.show()

def extend_tree_by_row(T: nx.DiGraph, charset: Set[int], taxum_idx: int, taxum_chars: np.ndarray) -> bool:
    edits = set(np.flatnonzero(taxum_chars)) # all the edits made by this taxum 
    additions = []

    curr = "r_0"
    edit_found = True
    while edit_found:
        edit_found = False
        for _, out_node, data in T.out_edges(curr, data=True):
            if data["edit"] in edits:
                # traverse edge
                curr = out_node
                edit_found = True
                edits.remove(data["edit"])
                break
    additions = list(edits)
        
    for edit in additions:
        if edit not in charset:
            return False # collision condition
        charset.add(edit)
        label = "c_" + str(edit + 1)
        T.add_edge(curr, "i" + str(edit), label=label, edit=edit)
    T.add_edge("i" + str(additions[-1]), "r_" + str(taxum_idx + 1), edit=-1)
    return True
    

def two_state_phylo(M: np.ndarray, draw_graph=False) -> bool:
    """Determines whether matrix M accepts a perfect phylogeny"""
    num_edits = M.sum(axis = 1)
    taxa_order = num_edits.argsort() # sets order over rows of M
    charset = set(range(len(M[0])))

    T = nx.DiGraph()
    T.add_node("r_0")

    for taxum_idx in taxa_order:
        if not extend_tree_by_row(T, charset, taxum_idx, M[taxum_idx]):
            return False

    if draw_graph:
        draw_graph_f(T)
    return True
        

def three_state_phylo(M: np.ndarray) -> bool:
    """Determines whether matrix M accepts a perfect phylogeny"""
    pass
