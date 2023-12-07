from model import WormSimulator
import pandas as pd

NUM_EXPERIMENTS = 500

GRID_SIZE = 35
N_FOOD = GRID_SIZE**2 * 10

for num_spots in [1, 2, 4]:
    timesteps = []
    for i in range(NUM_EXPERIMENTS):
        model = WormSimulator(n_agents=35, n_food=N_FOOD, clustering=1, dim_grid=GRID_SIZE, social=True,
                            multispot=True, num_spots=num_spots, clustered=True, strain_specific=True)

        total_food = model.grid.get_total_food()
        step_count = 0
        while model.grid.get_total_food() >= total_food * 0.1:
            model.step()
            step_count += 1

        timesteps.append(step_count)

    final = sum(timesteps) / len(timesteps)
    print(f'Social - Number of spots {num_spots} = {final}')