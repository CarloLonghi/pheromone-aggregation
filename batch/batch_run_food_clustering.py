import os
import sys

from tqdm import tqdm

from model import WormSimulator
import csv

from player import Food
from plotting import plot_mean_with_df, plot_frequencies

NUM_EXPERIMENTS = 10
GRID_SIZE = 35
N_FOOD = GRID_SIZE**2 * 10


if len(sys.argv) > 1:
    file_name = str(sys.argv[1])
else:
    print("File name set to default")
    file_name = "10gen_1_minimal_food_clustering"


def run_experiment(social:bool,strain_specific:bool):
    result = []
    all_gamma = [0,0.5,1,1.5,2,3,4,5,6,8,10]
    all_frequencies = []
    i = 0
    for gamma in all_gamma:
        timesteps = []
        i+=1
        frequency = []
        food_consumption = []
        for _ in tqdm(range(NUM_EXPERIMENTS), desc=(f'Running {i}/{len(all_gamma)} -> Social: {social} - Strain specific: {strain_specific} with {gamma} degree of food clustering')
                ,position=0,leave=True):
            model = WormSimulator(n_agents=40, n_food=N_FOOD, clustering = gamma, dim_grid=GRID_SIZE, social=social,
                                  multispot=False, num_spots=1, clustered=False, strain_specific=strain_specific)

            total_food = model.grid.get_total_food()
            step_count = 0
            while model.grid.get_total_food() >= total_food * 0.1:
                model.step()
                step_count += 1

            timesteps.append(step_count)

            for cell_content in model.grid.coord_iter():
                x, y = cell_content[1]
                agents_on_cell = model.grid.get_cell_list_contents((x, y))
                for agent in agents_on_cell:
                    if not isinstance(agent, Food):
                        # Access and perform actions with each agent here
                        agent_specific_data = agent.retrieve_foraging_efficiency_data()
                        data = list(agent_specific_data.values())
                        frequency.append(round(data[1] / data[0], 2))
                        food_consumption.append(data[2])
        all_frequencies.append([gamma, social, frequency,food_consumption])
        mean = sum(timesteps) / len(timesteps)
        std_dev = (sum((x - mean) ** 2 for x in timesteps) / len(timesteps))**0.5
        result.append([social,strain_specific,gamma, mean,std_dev])

    return result, all_frequencies


results = [["Social","Strain specific","Gamma","Mean time","Standard deviation"]]
f = [["Gamma","Social","Sense Frequency","Food consumption"]]
experiment = [ # Social, Strain Specific
    [True,True],
    [False,True]
]
for i in range(len(experiment)):
    print(f'Lauching simulation {i+1}/{len(experiment)}')
    exp_result , frequencies = run_experiment(experiment[i][0], experiment[i][1])
    results += exp_result
    f += frequencies

if not os.path.exists("../CSV"):
    os.makedirs("../CSV")

with open("../CSV/"+file_name+".csv", 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerows(results)

with open("../CSV/"+file_name+"_frequencies.csv", 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerows(f)

print(f"List has been saved as '{file_name}.csv'")
plot_mean_with_df(file_name,"Gamma")
plot_mean_with_df(file_name,"Gamma",zoomed=True)
plot_frequencies(file_name, "Gamma")