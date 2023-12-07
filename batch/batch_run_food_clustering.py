import os
import sys
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from model import WormSimulator
import csv

from plotting import plot_mean_with_df

NUM_EXPERIMENTS = 100
GRID_SIZE = 35
N_FOOD = GRID_SIZE**2 * 10


if len(sys.argv) > 1:
    file_name = str(sys.argv[1])
else:
    print("File name set to default")
    file_name = "food_clustering"


def run_experiment(social:bool,strain_specific:bool):
    result = []
    all_gamma = [x / 2 for x in range(0, 7)]
    i = 0
    for gamma in all_gamma:
        timesteps = []
        i+=1
        for _ in tqdm(range(NUM_EXPERIMENTS), desc=(f'Running {i}/{len(all_gamma)} -> Social: {social} - Strain specific: {strain_specific} with {gamma} degree of food clustering')
                ,position=0,leave=True):
            model = WormSimulator(n_agents=40, n_food=N_FOOD, clustering = gamma, dim_grid=GRID_SIZE, social=social,
                                  multispot=False, num_spots=1, clustered=True, strain_specific=strain_specific)

            total_food = model.grid.get_total_food()
            step_count = 0
            while model.grid.get_total_food() >= total_food * 0.1:
                model.step()
                step_count += 1

            timesteps.append(step_count)

        mean = sum(timesteps) / len(timesteps)
        std_dev = (sum((x - mean) ** 2 for x in timesteps) / len(timesteps))**0.5
        result.append([social,strain_specific,gamma, mean,std_dev])

    return result


results = [["Social","Strain specific","Gamma","Mean time","Standard deviation"]]
experiment = [
    [True,False],
    [False,False]
]
for i in range(len(experiment)):
    print(f'Lauching simulation {i+1}/{len(experiment)}')
    results += run_experiment(experiment[i][0], experiment[i][1])


if not os.path.exists("../CSV"):
    os.makedirs("../CSV")

with open("../CSV/"+file_name+".csv", 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerows(results)

print(f"List has been saved as '{file_name}.csv'")
plot_mean_with_df(file_name,"Social","Gamma")