import numpy as np
from matplotlib import pyplot as plt
import argparse
from run import MAX_STEPS

def find_clusters(graph, interval):
    to_visit = set(range(len(graph)))
    clusters = []
    while len(to_visit) > 0:
        node = to_visit.pop()
        bfs_list = set([node,])
        cluster = set([node,])
        while len(bfs_list) > 0:
            bfs_node = bfs_list.pop()
            if bfs_node in to_visit:
                to_visit.remove(bfs_node)
            connected = [i for i in range(len(graph[bfs_node])) if graph[bfs_node][i] >= interval]
            connected = [c for c in connected if c in to_visit]
            bfs_list.update(connected)
            cluster.update(connected)
        clusters.append(cluster)
    return clusters

def main(attractive_w, repulsive_w, align_w, test_n):
    adj_mat = np.load(f'aggr_data/adj_{attractive_w}_{repulsive_w}_{align_w}_{test_n}.npy')
    biggest_clusters = np.zeros(MAX_STEPS + 2)
    for t in range(MAX_STEPS):
        clusters = find_clusters(adj_mat[t], 1)
        cluster_size = [len(c) for c in clusters]
        biggest_clusters[t] = max(cluster_size)

    plt.figure(figsize=(10, 5), dpi=80)
    plt.plot(biggest_clusters)
    plt.show()
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', type=float, required=True)
    parser.add_argument('-r', type=float, required=True)
    parser.add_argument('-l', type=float, required=True)
    parser.add_argument('-t', type=int, required=True)
    args = parser.parse_args()
    main(args.a, args.r, args.l, args.t)
