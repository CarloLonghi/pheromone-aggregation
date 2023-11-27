import mesa
from player import SolitaryWorm, SocialWorm, Food
from environment import WormEnvironment

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

        for i in range(n_food):
            coords = (self.random.randrange(0, dim_grid), self.random.randrange(0, dim_grid))
            f = Food(f'food_{i}', self, coords)
            self.grid.place_food(coords, f)

    def step(self) -> None:
        self.schedule.step()