import mesa
from player import SolitaryWorm, SocialWorm, Food
from environment import WormEnvironment
import math
import random

class WormSimulator(mesa.Model):
    def __init__(self, n_agents: int, n_food: int, dim_grid: int, social: bool, multispot: bool, num_spots: int):
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
        if multispot:
            self.multispot_food(total_food, num_spots)
        else:
            gamma = n_food
            self.smoothly_varying_food(total_food, gamma)

        self.datacollector = mesa.DataCollector(model_reporters={"Food": self.grid.get_total_food}, agent_reporters={})
        self.datacollector.collect(self)

    def step(self) -> None:
        self.schedule.step()
        self.datacollector.collect(self)

    def smoothly_varying_food(self, total_food: int, gamma: int = 0):
        if gamma > 0:
            foods = []
            coords = (self.random.randrange(0, self.grid.dim_grid), self.random.randrange(0, self.grid.dim_grid))
            f = Food(f'food_{0}', self, coords)
            self.grid.place_food(coords, f)
            foods.append(f)
            for i in range(1, total_food):
                d = self.random.uniform(0, 1) ** (-1 / gamma)
                if d > self.grid.dim_grid / math.sqrt(2):
                    d = self.random.uniform(1, self.grid.dim_grid / math.sqrt(2))
                starting_pos = self.random.choice(foods).pos
                possible_positions = self.grid.get_cells_from(starting_pos, False, int(d))
                coords = self.random.choice(possible_positions)
                f = Food(f'food_{i}', self, coords)
                self.grid.place_food(coords, f)
                foods.append(f)
        elif gamma == 0:
            for i in range(total_food):
                coords = (self.random.randrange(0, self.grid.dim_grid), self.random.randrange(0, self.dim_grid))
                f = Food(f'food_{i}', self, coords)
                self.grid.place_food(coords, f)

    def multispot_food(self, total_food: int, num_spots: int):
        if num_spots == 1:
            dx = self.grid.dim_grid / 2
            dy = self.grid.dim_grid / 2
            spot_pos = [(round(dx), round(dy))]
            radius = round(self.grid.dim_grid / 6)
        if num_spots == 2:
            dx = self.grid.dim_grid / 4
            dy = self.grid.dim_grid / 4
            spot_pos = [(round(dx), round(dy)), (round(3*dx), round(3*dy))]
            radius = round(self.grid.dim_grid / 8)
        if num_spots == 4:
            dx = self.grid.dim_grid / 4
            dy = self.grid.dim_grid / 4
            spot_pos = [(round(dx), round(dy)), (round(3*dx), round(dy)), (round(dx), round(3*dy)), (round(3*dx), round(3*dy))]
            radius = round(self.grid.dim_grid / 12)

        for i in range(num_spots):
            neighborhood = self.grid.get_neighborhood(spot_pos[i], True, True, radius)
            food_per_cell = total_food // len(neighborhood)
            for cell in neighborhood:
                f = Food(f'food_{i}', self, cell, quantity=food_per_cell)
                self.grid.place_food(cell, f)