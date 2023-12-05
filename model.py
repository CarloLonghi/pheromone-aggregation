import mesa
from player import SolitaryWorm, SocialWorm, Food
from environment import WormEnvironment
import math
import random

class WormSimulator(mesa.Model):
    def __init__(self, n_agents: int, n_food: int, dim_grid: int, social: bool):
        super().__init__()
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = WormEnvironment(dim_grid, dim_grid, torus=True)

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

        total_food = dim_grid ** 2
        gamma = n_food/100
        food_init = [random.randint(0, dim_grid-1), random.randint(0, dim_grid-1)]
        coords = (food_init[0], food_init[1])
        f = Food(f'food_{0}', self, coords)
        self.grid.place_food(coords, f)
        for i in range(total_food):
            d = random.uniform(1, dim_grid / math.sqrt(2))
            if gamma > 0:
                d = random.uniform(0,1) ** (-1 / gamma)
                if d > dim_grid / math.sqrt(2):
                    d = random.uniform(1, dim_grid / math.sqrt(2))
            angle = random.uniform(0, 2 * math.pi)
            x = food_init[0] + int(d * math.cos(angle))
            y = food_init[1] + int(d * math.sin(angle))

            if not(x < 0 or x >= dim_grid or y < 0 or y >= dim_grid):
                coords = (x,y)
                f = Food(f'food_{i+1}', self, coords)
                self.grid.place_food(coords, f)

        self.datacollector = mesa.DataCollector(model_reporters={"Food": self.grid.get_total_food}, agent_reporters={})
        self.datacollector.collect(self)

    def step(self) -> None:
        self.schedule.step()
        self.datacollector.collect(self)