import sys
from tqdm import tqdm

from model import WormSimulator
import pandas as pd
import mesa
import numpy as np
import argparse
import os

NUM_EXPERIMENTS = 1
ENV_SIZE = 400
MAX_STEPS = 500
NUM_AGENTS = 75

if len(sys.argv) > 1:
    file_name = str(sys.argv[1])
else:
    print("File name set to default")
    file_name = "cluster_false_test"


def run_experiment(attractive_w, repulsive_w, align_w):
    model = WormSimulator(n_agents=NUM_AGENTS, dim_env=ENV_SIZE, max_steps=MAX_STEPS, multispot=False, num_spots=1, clustered=False,
                            attractive_w=attractive_w, repulsive_w=repulsive_w, align_w=align_w)

    step_count = 0
    while step_count <= MAX_STEPS:
        model.step()

        step_count += 1

    data = model.datacollector.get_agent_vars_dataframe()

    return data, model.adj_matrix

def main(attractive_w, repulsive_w, align_w, test_n):
    res, adj_mat = run_experiment(attractive_w, repulsive_w, align_w)
    res['posx'] = [p[0] for p in res['pos'].values]
    res['posy'] = [p[1] for p in res['pos'].values]
    res = res.drop('pos', axis=1)
    res.to_csv(f'position_data.csv')
    np.save(f'aggr_data/adj_{attractive_w}_{repulsive_w}_{align_w}_{test_n}.npy', adj_mat)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', type=float, required=True)
    parser.add_argument('-r', type=float, required=True)
    parser.add_argument('-l', type=float, required=True)
    parser.add_argument('-t', type=int, required=True)
    args = parser.parse_args()
    main(args.a, args.r, args.l, args.t)
