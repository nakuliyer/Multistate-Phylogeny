from implementation import *

M = np.array([[1, 1, 0, 0, 0], [0, 0, 1, 0, 0], [1, 1, 0, 0, 1], [0, 0, 1, 1, 0], [0, 1, 0, 0, 0]])
print(two_state_phylo(M, draw_graph=True))