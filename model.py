import mesa
from player import SolitaryWorm, SocialWorm, Food

class WormSimulator(mesa.Model):
    def __init__(self, n_agents, n_food, dim_grid, social):
        super().__init__()
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.MultiGrid(dim_grid, dim_grid, torus=True)

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
            self.grid.place_agent(f, coords)

    def step(self):
        self.schedule.step()