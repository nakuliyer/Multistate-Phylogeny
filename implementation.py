import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from typing import Set, Tuple

from utilities import hierarchy_pos

def draw_graph(T: nx.DiGraph):
    """Draws a tree"""
    
    pos = hierarchy_pos(T, "r0")
    edge_labels = nx.get_edge_attributes(T, 'label')
    labeldict = {}
    for node in T.nodes:
        if node[0] == "r":
            labeldict[node] = node # leaf/root nodes
        else:
            labeldict[node] = "" # internal nodes
    nx.draw(T, pos, labels=labeldict, with_labels=True)
    nx.draw_networkx_edge_labels(T, pos, edge_labels=edge_labels)
    plt.show()

def extend_tree_for_taxum(T: nx.DiGraph, M: np.ndarray, charset: Set[int], taxum_idx: int, char_order: np.array) -> bool:
    """Extends a tree by a row

    Args:
        T (nx.DiGraph): tree
        charset (Set[int]): set of characters available to use in extending the tree (i.e. not already used)
        taxum_idx (int): an id for the taxa
        taxum_chars (np.ndarray): the actual row of chars in the matrix corresponding to this taxa

    Returns:
        bool: true if the tree was able to be extended, false if the tree had a conflict
    """
    edits = np.flatnonzero(M[taxum_idx]) # all the edits made by this taxum

    curr = "r0"
    edit_found = True
    while edit_found:
        edit_found = False
        for _, out_node, data in T.out_edges(curr, data=True):
            if data["edit"] in edits:
                # traverse edge
                curr = out_node
                edit_found = True
                edits = np.delete(edits, np.where(edits == data["edit"]))
                break
    
    for edit in edits:
        if edit not in charset:
            return False # collision condition
        charset.remove(edit)
        label = "c" + str(char_order[edit] + 1)
        T.add_edge(curr, "i" + str(edit), label=label, edit=edit)
        curr = "i" + str(edit)
    if len(edits):
        T.add_edge("i" + str(edits[-1]), "r" + str(taxum_idx + 1), edit=-1)
    else:
        T.add_edge(curr, "r" + str(taxum_idx + 1), edit=-1) # taxa is same as another one
    return True


def sort_characters(M: np.ndarray) -> Tuple[np.ndarray, np.array]:
    """Sorts the columns of matrix M out-of-place such that the sum of the values in each column
    is descending. Returns both the column-sorted matrix and an array indicating the ordering so that
    the original matrix may be recovered."""
    num_edits = M.sum(axis = 0)
    char_order = num_edits.argsort()[::-1]
    M = M[:, char_order]
    return M, char_order
    

def two_state_phylo(M: np.ndarray, draw=False) -> nx.DiGraph:
    """Determines whether matrix M accepts a perfect two-state phylogeny"""
    M, char_order = sort_characters(M)
    charset = set(range(len(M[0])))

    T = nx.DiGraph()
    T.add_node("r0")

    num_taxa = M.shape[0]
    for taxum_idx in range(num_taxa):
        if not extend_tree_for_taxum(T, M, charset, taxum_idx, char_order):
            return None

    if draw:
        draw_graph(T)
    return T
        

def three_state_phylo(M: np.ndarray, draw=False) -> nx.DiGraph:
    """Determines whether matrix M accepts a perfect three-state phylogeny"""
    
    num_taxa = M.shape[0]
    num_chars = M.shape[1]
    
    state_trees = [] # holds all 3^c possible state trees
    def add_state_tree(i: int, l: list):
        if i == num_chars:
            state_trees.append(l)
        else:
            add_state_tree(i + 1, l + [0]) # 0 -> 1 state, then 1 -> 2 state
            add_state_tree(i + 1, l + [1]) # 0 -> 2 state, then 2 -> 1 state
            add_state_tree(i + 1, l + [2]) # 0 -> 1 state and 1 -> 2 state independently
    add_state_tree(0, [])
    
    for state_tree in state_trees:
        M_2s = np.zeros((M.shape[0], M.shape[1] * 2))
        for taxum_idx in range(num_taxa):
            for char_idx in range(num_chars):
                # settings cols (2 * char_idx) for -> 1 change and 
                # (2 * char_idx + 1) for -> 2 change
                cladistic_char_tree = state_tree[char_idx]
                char = M[taxum_idx][char_idx]
                if cladistic_char_tree == 0:
                    M_2s[taxum_idx][2 * char_idx] = int(char == 1 or char == 2)
                    M_2s[taxum_idx][2 * char_idx + 1] = int(char == 2)
                elif cladistic_char_tree == 1:
                    M_2s[taxum_idx][2 * char_idx] = int(char == 1)
                    M_2s[taxum_idx][2 * char_idx + 1] = int(char == 2 or char == 1)
                elif cladistic_char_tree == 2:
                    M_2s[taxum_idx][2 * char_idx] = int(char == 1)
                    M_2s[taxum_idx][2 * char_idx + 1] = int(char == 2)
        T = two_state_phylo(M_2s)
        if T:
            if draw:
                for _, _, d in T.edges(data=True):
                    if "label" in d:
                        char_2s = int(d["label"][1:]) - 1
                        char = char_2s // 2 + 1
                        edit = char_2s % 2 + 1
                        d["label"] = "c" + str(char) + " -> " + str(edit)
                draw_graph(T)
            return T
    return None
        
