import mesa

class SolitaryWorm(mesa.Agent):
    def __init__(self, name, model, pos):
        super().__init__(name, model)
        self.name = name
        self.pos = pos

    def sense_food(self):
        neighborhood = self.model.grid.get_neighbors(self.pos, moore=True, include_center=True, radius=1)
        on_food = False
        n = 0
        while not on_food and n < len(neighborhood):
            if type(neighborhood[n]) == Food:
                on_food = True
            n += 1
        return on_food

    def move(self):
        near_food = self.sense_food()
        radius = 2
        if near_food:
            radius = 1
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius=radius)
        new_pos = self.random.choice(neighborhood)
        on_cell = self.model.grid.get_neighbors(new_pos, moore=True, include_center=True, radius=0)
        is_occupied = False
        n = 0
        while not is_occupied and n < len(on_cell):
            if type(on_cell[n]) == SolitaryWorm:
                is_occupied = True
            n += 1
        if not is_occupied:
            self.model.grid.move_agent(self, new_pos)
            self.pos = new_pos  

    def consume_food(self):
        on_cell = self.model.grid.get_neighbors(self.pos, moore=True, include_center=True, radius=0)
        ate = False
        n = 0
        while not ate and n < len(on_cell):
            if type(on_cell[n]) == Food:
                self.model.grid.remove_agent(on_cell[n])
                ate = True
            n += 1

    def step(self):
        self.consume_food()
        self.move()

class SocialWorm(SolitaryWorm):
    def __init__(self, name, model, pos):
        super().__init__(name, model, pos)
        self.name = name
        self.pos = pos

    def move(self):
        near_food = self.sense_food()
        radius = 2
        if near_food:
            radius = 1
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius=radius)
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=radius)
        worm_neighbors = [n for n in neighbors if type(n) == SocialWorm]
        if near_food and len(worm_neighbors) > 0:
            social_neighborhood = []
            for worm in worm_neighbors:
                other_neighborhood = self.model.grid.get_neighborhood(worm.pos, moore=True, include_center=False, radius=radius)
                common_neighborhood = list(set(neighborhood).intersection(set(other_neighborhood)))
                social_neighborhood = list(set(social_neighborhood + common_neighborhood))
            neighborhood = social_neighborhood

        new_pos = self.random.choice(neighborhood)
        on_cell = self.model.grid.get_neighbors(new_pos, moore=True, include_center=True, radius=0)
        is_occupied = False
        n = 0
        while not is_occupied and n < len(on_cell):
            if type(on_cell[n]) == SolitaryWorm:
                is_occupied = True
            n += 1
        if not is_occupied:
            self.model.grid.move_agent(self, new_pos)
            self.pos = new_pos

class Food(mesa.Agent):
    def __init__(self, name, model, pos):
        super().__init__(name, model)
        self.name = name
        self.pos = pos