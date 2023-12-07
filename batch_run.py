import os
import sys
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from model import WormSimulator
import csv

from plotting import plot_mean_with_df

NUM_EXPERIMENTS = 500
GRID_SIZE = 35
N_FOOD = GRID_SIZE**2 * 10


if len(sys.argv) > 1:
    file_name = str(sys.argv[1])
else:
    print("File name set to default")
    file_name = "default"


def run_experiment(social:bool,strain_specific:bool):
    result = []
    for num_spots in [1, 2, 4]:
        timesteps = []
        desc = (f'Running Social: {social} - Strain specific: {strain_specific} with {num_spots} spots')
        for _ in tqdm(range(NUM_EXPERIMENTS), desc=desc,position=0,leave=True):
            model = WormSimulator(n_agents=35, n_food=N_FOOD, clustering=1, dim_grid=GRID_SIZE, social=social,
                                  multispot=True, num_spots=1, clustered=True, strain_specific=strain_specific)

            total_food = model.grid.get_total_food()
            step_count = 0
            while model.grid.get_total_food() >= total_food * 0.1:
                model.step()
                step_count += 1

            timesteps.append(step_count)

        mean = sum(timesteps) / len(timesteps)
        std_dev = (sum((x - mean) ** 2 for x in timesteps) / len(timesteps))**0.5
        result.append([social,strain_specific,num_spots, mean,std_dev])

    return result


results = [["Social","Strain specific","Number of spots","Mean time","Standard deviation"]]
results+=run_experiment(False, True)
results+=run_experiment(False, False)

if not os.path.exists("CSV"):
    os.makedirs("CSV")

with open("CSV/"+file_name+".csv", 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerows(results)

print(f"List has been saved as '{file_name}'")
plot_mean_with_df(file_name)