from implementation import *

M = np.array([[1, 1, 0, 0, 0], 
              [0, 0, 1, 0, 0], 
              [1, 1, 0, 0, 1], 
              [0, 0, 1, 1, 0], 
              [0, 1, 0, 0, 0]])
print(two_state_phylo(M, draw=True))

# M = np.array([[1, 1, 0, 0, 0], 
#               [0, 0, 1, 0, 0], 
#               [1, 1, 0, 0, 1], 
#               [0, 0, 1, 1, 0], 
#               [0, 1, 0, 0, 1]])
# print(two_state_phylo(M, draw=False))

# M = np.array([[1, 1, 0, 0, 0], 
#               [0, 0, 1, 0, 0], 
#               [1, 1, 0, 0, 1], 
#               [0, 0, 1, 1, 0], 
#               [0, 1, 0, 0, 0]])
# print(three_state_phylo(M, draw=False))

# M = np.array([[1, 0],
#               [2, 2],
#               [2, 1],
#               [1, 1]])
# print(three_state_phylo(M, draw=False))

# M = np.array([[1, 0],
#               [0, 1],
#               [1, 0],
#               [0, 1]])
# print(three_state_phylo(M, draw=False))