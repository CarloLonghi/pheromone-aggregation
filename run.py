import sys
from tqdm import tqdm

from model import WormSimulator
import pandas as pd

NUM_EXPERIMENTS = 1
ENV_SIZE = 500
MAX_STEPS = 1000
NUM_AGENTS = 50

if len(sys.argv) > 1:
    file_name = str(sys.argv[1])
else:
    print("File name set to default")
    file_name = "cluster_false_test"


def run_experiment():
    result = []
    #for _ in tqdm(range(NUM_EXPERIMENTS), desc= (f'Running -> '),position=0,leave=True):
    model = WormSimulator(n_agents=NUM_AGENTS, dim_env=ENV_SIZE, social=False,
                            multispot=True, num_spots=1, clustered=False, strain_specific=False)

    step_count = 0
    while step_count <= MAX_STEPS:
        model.step()

        step_count += 1

    # for cell_content in model.env.coord_iter():
    #     x, y = cell_content[1]
    #     agents_on_cell = model.env.get_cell_list_contents((x, y))
    #     for agent in agents_on_cell:
    #         if not isinstance(agent, Food):
    #             # Access and perform actions with each agent here
    #             agent_specific_data = agent.retrieve_foraging_efficiency_data()
    #             data = list(agent_specific_data.values())
    #             frequency.append(round(data[1] / data[0],2))
    #             food_consumption.append(data[2])

    data = model.datacollector.get_agent_vars_dataframe()

    return data

if __name__ == "__main__":
    res = run_experiment()
    res.to_csv('position_data.csv')
