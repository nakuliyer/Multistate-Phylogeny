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

def extend_tree_for_taxum(T: nx.DiGraph, M: np.ndarray, taxum_idx: int) -> bool:
    """Extends a tree by a row

    Args:
        T (nx.DiGraph): tree
        M (np.ndarray): matrix
        taxum_idx (int): an id for the taxa

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
    
    # Get all the edits already used in T (i.e. all the edge-labels of T)
    edits_already_made = set(map(lambda x: x[2], T.edges.data("edit")))
    
    for edit in edits:
        if edit in edits_already_made:
            return False # collision condition
        T.add_edge(curr, "i" + str(edit), edit=edit)
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


def two_state_sorted_phylo(M: np.ndarray) -> nx.DiGraph:
    """Determines whether matrix M (with columns pre-sorted in descneding by number of 1s) accepts a perfect two-state phylogeny

    Args:
        M (np.ndarray): matrix

    Returns:
        nx.DiGraph: tree is perfect phylogeny exists, else None
    """
    T = nx.DiGraph()
    T.add_node("r0")

    num_taxa = M.shape[0]
    for taxum_idx in range(num_taxa):
        if not extend_tree_for_taxum(T, M, taxum_idx):
            return None
    return T
    

def two_state_phylo(M: np.ndarray, draw=False) -> nx.DiGraph:
    """Determines whether matrix M accepts a perfect two-state phylogeny"""
    M, char_order = sort_characters(M)
    T = two_state_sorted_phylo(M)
    if draw and T:
        for _, _, d in T.edges(data=True):
            edit = d["edit"]
            if edit != -1:
                d["label"] = "c" + str(char_order[edit] + 1)
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
        M_2s, char_order = sort_characters(M_2s)
        T = two_state_sorted_phylo(M_2s)
        if T:
            if draw:
                for _, _, d in T.edges(data=True):
                    edit_2s = d["edit"]
                    if edit_2s != -1:
                        char = char_order[edit_2s] // 2 + 1
                        edit = char_order[edit_2s] % 2 + 1
                        d["label"] = "c" + str(char) + " -> " + str(edit)
                draw_graph(T)
            return T
    return None
        
