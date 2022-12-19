from implementation import *
import random
import time


def create_2state_base():
    T = nx.DiGraph()
    char_set = set(["c" + str(i) for i in range(1, 3)])
    T.add_node("r0")

    if random.choice([True, False]):
        first = char_set.pop()
        T.add_edge("r0", "1", label=first)
        T.add_edge("1", "r1")
        second = char_set.pop()
        T.add_edge("1", "r2", label=second)
    else:
        first = char_set.pop()
        T.add_edge("r0", "r1", label=first)
        second = char_set.pop()
        T.add_edge("r0", "r2", label=second)
    return T


def add_char_2state(T: nx.DiGraph, satisfy):
    leaves = [item for item in T.edges().data() if item[1][0] == "r" and item[2]]
    chars = [item for item in T.edges().data() if item[2]]
    new_char = "c" + str(len(chars) + 1)

    if satisfy:
        to_add = leaves[random.randint(0, len(leaves) - 1)]
        temp = str(len(T.nodes()) + 1)
        T.remove_edge(to_add[0], to_add[1])
        T.add_edge(to_add[0], temp, label=to_add[2]["label"])
        T.add_edge(temp, to_add[1], label=new_char)
    else:
        r_idx = random.randint(0, len(leaves) - 1)
        start = leaves[r_idx][1]
        end = leaves[r_idx - 1][1]
        T.add_edge(start, end, label=new_char)


def add_leaf_2state(T: nx.DiGraph):
    leaves = [item for item in T.edges().data() if item[1][0] == "r"]
    new_leaf = "r" + str(len(leaves) + 1)
    targets = [
        item
        for item in T.edges().data()
        if item[0][0] != "r" and T.out_degree(item[0]) == 1
    ]
    if not targets:
        return

    target = targets[random.randint(0, len(targets) - 1)]
    T.add_edge(target[0], new_leaf)


def create_matrix(T: nx.DiGraph, two_state, d):
    paths = []
    for taxa in T.nodes():
        if T.out_degree(taxa) == 0:
            paths.append(nx.shortest_path(T, "r0", taxa))

    # create paths with chars
    if two_state:
        chars = [item for item in T.edges().data() if item[2]]
        char_len = len(chars)
    else:
        char_len = len(d)

    leaves = [item for item in T.edges().data() if item[1][0] == "r"]
    leaf_len = len(leaves)

    matrix = [None] * leaf_len
    for path in paths:
        taxa_arr = [0] * char_len
        for i in range(1, len(path)):
            curr_data = T.get_edge_data(path[i - 1], path[i])
            if curr_data:
                if two_state:
                    curr_char = curr_data["label"]
                    taxa_arr[int(curr_char[1:]) - 1] = 1
                else:
                    curr_label = curr_data["label"]
                    curr_char = curr_label[: curr_label.index(":")]
                    taxa_arr[int(curr_char[1:]) - 1] = int(
                        curr_label[curr_label.index(":") + 2 :]
                    )
        matrix[int(path[-1][1:]) - 1] = taxa_arr

    return np.array(matrix)


def test_layered_2state(success):
    T = create_2state_base()
    for i in range(10):
        add_char_2state(T, True)
        add_leaf_2state(T)

    if success:
        add_char_2state(T, True)
        add_leaf_2state(T)
    else:
        add_char_2state(T, False)
        add_leaf_2state(T)

    return T


def create_3state_base():
    T = nx.DiGraph()
    char_set = set(["c" + str(i) for i in range(1, 3)])
    char_dict = {}
    T.add_node("r0")

    if random.choice([True, False]):
        first = char_set.pop()
        char_dict[first] = char_dict.get(first, 0) + 1
        T.add_edge("r0", "1", label=first + ": " + str(char_dict[first]))
        T.add_edge("1", "r1")
        second = char_set.pop()
        char_dict[second] = char_dict.get(second, 0) + 1
        T.add_edge("1", "r2", label=second + ": " + str(char_dict[second]))
    else:
        first = char_set.pop()
        char_dict[first] = char_dict.get(first, 0) + 1
        T.add_edge("r0", "r1", label=first + ": " + str(char_dict[first]))
        second = char_set.pop()
        char_dict[second] = char_dict.get(second, 0) + 1
        T.add_edge("r0", "r2", label=second + ": " + str(char_dict[second]))
    return T, char_dict


def add_char_3state(T: nx.DiGraph, d, satisfy):
    leaves = [item for item in T.edges().data() if item[1][0] == "r" and item[2]]
    new_char = "c" + str(len(d) + 1)
    d[new_char] = d.get(new_char, 0) + 1

    if satisfy:
        to_add = leaves[random.randint(0, len(leaves) - 1)]
        temp = str(len(T.nodes()) + 1)
        T.remove_edge(to_add[0], to_add[1])
        T.add_edge(to_add[0], temp, label=to_add[2]["label"])
        T.add_edge(temp, to_add[1], label=new_char + ": " + str(d[new_char]))
    else:
        r_idx = random.randint(0, len(leaves) - 1)
        to_add = leaves[r_idx]
        char, count = random.choice(list(d.items()))
        temp = str(len(T.nodes()) + 1)
        T.remove_edge(to_add[0], to_add[1])
        T.add_edge(to_add[0], temp, label=to_add[2]["label"])
        T.add_edge(temp, to_add[1], label=char + ": " + str(count))

        leaves = [item for item in T.edges().data() if item[1][0] == "r" and item[2]]
        r_idx1 = random.randint(0, len(leaves) - 1)
        to_add1 = leaves[r_idx1]
        char, count = random.choice(list(d.items()))
        temp1 = str(len(T.nodes()) + 1)
        T.remove_edge(to_add1[0], to_add1[1])
        T.add_edge(to_add1[0], temp1, label=to_add1[2]["label"])
        T.add_edge(temp1, to_add1[1], label=char + ": " + str(count))

        leaves = [item for item in T.edges().data() if item[1][0] == "r" and item[2]]
        r_idx2 = random.randint(0, len(leaves) - 1)
        to_add2 = leaves[r_idx2]
        char, count = random.choice(list(d.items()))
        temp2 = str(len(T.nodes()) + 1)
        T.remove_edge(to_add2[0], to_add2[1])
        T.add_edge(to_add2[0], temp2, label=to_add2[2]["label"])
        T.add_edge(temp2, to_add2[1], label=char + ": " + str(count))


def change_char_3state(T: nx.DiGraph, d):
    leaves = [item for item in T.edges().data() if item[1][0] == "r" and item[2]]
    r_idx = random.randint(0, len(leaves) - 1)
    path = nx.shortest_path(T, "r0", leaves[r_idx][1])
    temp = []
    for i in range(1, len(path)):
        curr_data = T.get_edge_data(path[i - 1], path[i])
        if curr_data:
            curr_label = curr_data["label"]
            curr_char = curr_label[: curr_label.index(":")]
            temp.append(curr_char)
    for key in temp:
        if d[key] == 1:
            d[key] = 2
            to_add = leaves[r_idx]
            temp1 = str(len(T.nodes()) + 1)
            T.remove_edge(to_add[0], to_add[1])
            T.add_edge(to_add[0], temp1, label=to_add[2]["label"])
            T.add_edge(temp1, to_add[1], label=key + ": " + str(d[key]))
            break


def add_leaf_3state(T: nx.DiGraph):
    leaves = [item for item in T.edges().data() if item[1][0] == "r"]
    new_leaf = "r" + str(len(leaves) + 1)
    targets = [
        item
        for item in T.edges().data()
        if item[0][0] != "r" and T.out_degree(item[0]) == 1
    ]
    if not targets:
        return

    target = targets[random.randint(0, len(targets) - 1)]
    T.add_edge(target[0], new_leaf)


def test_layered_3state(success, changes):
    T, d = create_3state_base()
    for i in range(changes):
        add_char_3state(T, d, True)
        change_char_3state(T, d)
        add_leaf_3state(T)

    if success:
        add_char_3state(T, d, True)
        add_leaf_3state(T)
    else:
        add_char_3state(T, d, False)
        add_leaf_3state(T)

    return T, d


num_success = 0
total = 0
start = time.time()
for i in range(2, 6):  # generate various trees between 2 to 5 iterations of extensions
    for j in range(100):  # test each iteration 25 times
        G, d = test_layered_3state(True, i)
        M = create_matrix(G, False, d)
        total += 1
        if three_state_phylo(M, False) != None:
            num_success += 1
end = time.time()
elapsed = end - start
print(num_success, f"out of {total} perfect phylogeny matrices were reconstructible in {elapsed} seconds")


num_fail = 0
total = 0
start = time.time()
for i in range(4, 6):  # generate various trees between 4 and 5 iterations of extensions
    for j in range(25):  # test each iteration 25 times
        G, d = test_layered_3state(False, i)
        M = create_matrix(G, False, d)
        total += 1
        if three_state_phylo(M, False) == None:
            num_fail += 1
end = time.time()
elapsed = end - start
print(num_fail, f"out of {total} non-perfect phylogeny matrices were not reconstructible in {elapsed} seconds")
