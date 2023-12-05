import mesa
from typing import Tuple

class SolitaryWorm(mesa.Agent):
    def __init__(self, name: str, model: mesa.Model, pos: Tuple[int]):
        super().__init__(name, model)
        self.name = name
        self.pos = pos

    def sense_food(self) -> bool:
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=True, radius=1)
        food = [self.model.grid.has_food(cell) for cell in neighborhood]
        return sum(food) > 0

    def move(self) -> None:
        radius = 2
        near_food = self.sense_food()
        if near_food:
            radius = 1
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius=radius)
        possible_moves = [n for n in neighborhood if self.model.grid.is_cell_free(n)]
        if len(possible_moves) > 0:
            new_pos = self.random.choice(possible_moves)
            self.model.grid.move_agent(self, new_pos)
            self.pos = new_pos  

    def consume_food(self) -> None:
        self.model.grid.consume_food(self.pos)

    def is_worm(self) -> bool:
        return True

    def step(self) -> None:
        self.consume_food()
        self.move()

class SocialWorm(SolitaryWorm):
    def __init__(self, name: str, model: mesa.Model, pos: Tuple[int]):
        super().__init__(name, model, pos)

    def move(self) -> None:
        radius = 2
        near_food = self.sense_food()
        if near_food:
            radius = 1
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius=radius)
        worm_neighbors = self.model.grid.get_neighbor_worms(self.pos, True, radius)
        if near_food and len(worm_neighbors) > 0:
            social_neighborhood = set()
            for worm in worm_neighbors:
                other_neighborhood = self.model.grid.get_neighborhood(worm.pos, moore=True, include_center=False, radius=radius)
                common_neighborhood = set(neighborhood).intersection(set(other_neighborhood))
                social_neighborhood = social_neighborhood.union(common_neighborhood)
            neighborhood = list(social_neighborhood)

        possible_moves = [n for n in neighborhood if self.model.grid.is_cell_free(n)]
        if len(possible_moves) > 0:
            new_pos = self.random.choice(neighborhood)
            self.model.grid.move_agent(self, new_pos)
            self.pos = new_pos

class Food(mesa.Agent):
    def __init__(self, name: str, model: mesa.Model, pos: Tuple[int], quantity: int = 1):
        super().__init__(name, model)
        self.name = name
        self.pos = pos
        self.quantity = quantity

    def increase(self) -> None:
        self.quantity += 1

    def consume(self) -> None:
        if self.quantity == 0:
            self.model.grid.remove_agent(self)
        else:
            self.quantity -= 1

    def is_worm(self) -> bool:
        return False