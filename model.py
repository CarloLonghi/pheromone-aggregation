import mesa
from player import SolitaryWorm, SocialWorm, Food
from environment import WormEnvironment
import math
import random

class WormSimulator(mesa.Model):
    def __init__(self, n_agents: int, n_food: int, dim_grid: int, social: bool):
        super().__init__()
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = WormEnvironment(dim_grid, torus=True)

        for i in range(n_agents):
            coords = (self.random.randrange(0, dim_grid), self.random.randrange(0, dim_grid))
            while not self.grid.is_cell_empty(coords):
                coords = (self.random.randrange(0, dim_grid), self.random.randrange(0, dim_grid))
            if social:
                a = SocialWorm(i, self, coords)
            else:
                a = SolitaryWorm(i, self, coords)
            self.schedule.add(a)
            self.grid.place_agent(a, coords)

        total_food = dim_grid ** 2 * 10
        gamma = n_food
        self.grid.smoothly_varying_food(total_food, self.random, gamma)

        self.datacollector = mesa.DataCollector(model_reporters={"Food": self.grid.get_total_food}, agent_reporters={})
        self.datacollector.collect(self)

    def step(self) -> None:
        self.schedule.step()
        self.datacollector.collect(self)