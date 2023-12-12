import mesa
from mesa.space import Coordinate
from typing import Tuple, Sequence
from mesa.datacollection import DataCollector


class SolitaryWorm(mesa.Agent):
    """Class for the solitary worm in the minimal model"""
    def __init__(self, name: str, model: mesa.Model, pos: Tuple[int]):
        super().__init__(name, model)
        self.name = name
        self.pos = pos
        self.feeding_rate = 1
        self.sensing_range = 1
        self.consumed_food = 0


    def sense_food(self) -> bool:
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=True, radius=self.sensing_range)
        food = [self.model.grid.has_food(cell) for cell in neighborhood]
        return sum(food) > 0

    def move(self) -> None:
        radius = 2
        near_food = self.sense_food()
        if near_food:
            radius = 1
        neighborhood = self.model.grid.get_neighborhood_dist(self.pos, moore=True, radius=radius)
        possible_moves = [n for n in neighborhood if self.model.grid.is_cell_free(n)]
        if len(possible_moves) > 0:
            new_pos = self.random.choice(possible_moves)
            self.model.grid.move_agent(self, new_pos)
            self.pos = new_pos



    def consume_food(self) -> None:
        self.model.grid.consume_food(self.pos,self, self.feeding_rate)


    def is_worm(self) -> bool:
        return True

    def step(self) -> None:
        self.consume_food()
        self.move()




class SocialWorm(SolitaryWorm):
    """Class for the social worm in the minimal model"""
    def __init__(self, name: str, model: mesa.Model, pos: Tuple[int]):
        super().__init__(name, model, pos)

    def move(self) -> None:
        near_food = self.sense_food()
        if near_food:
            neighborhood = self.model.grid.get_neighborhood_dist(self.pos, moore=True, radius=1)
            worm_neighbors = self.model.grid.get_neighbors_dist(self.pos, moore=True, radius=1)
            if len(worm_neighbors) > 0:
                neighborhood = self.targeted_step(neighborhood, worm_neighbors)
        else:
            neighborhood = self.model.grid.get_neighborhood_dist(self.pos, moore=True, radius=2)

        possible_moves = [n for n in neighborhood if self.model.grid.is_cell_free(n)]
        if len(possible_moves) > 0:
            new_pos = self.random.choice(neighborhood)
            self.model.grid.move_agent(self, new_pos)
            self.pos = new_pos



    def targeted_step(self, neighborhood: Sequence[Coordinate], worm_neighbors: Sequence[mesa.Agent]) -> Sequence[Coordinate]:
        social_neighborhood = set()
        for worm in worm_neighbors:
            other_neighborhood = self.model.grid.get_neighborhood_dist(worm.pos, moore=True, radius=1)
            common_neighborhood = set(neighborhood).intersection(set(other_neighborhood))
            social_neighborhood = social_neighborhood.union(common_neighborhood)
        return list(social_neighborhood)

class SPSolitaryWorm(SolitaryWorm):
    """Class for the solitary worm in the strain-specific model"""
    def __init__(self, name: str, model: mesa.Model, pos: Tuple[int], leaving_probability: float = 0):
        super().__init__(name, model, pos)
        self.feeding_rate = 0.4
        self.leaving_probability = leaving_probability
        self.sensing_range = 0


    def at_food_border(self) -> bool:
        at_border = False
        direct_neighborhood = self.model.grid.get_neighborhood_dist(self.pos, moore=True, radius=1)
        direct_nofood = [cell for cell in direct_neighborhood if not self.model.grid.has_food(cell)]
        if len(direct_nofood) > 0:
            at_border = True
        return at_border
    
    def move(self) -> None:
        if self.sense_food():
            if self.at_food_border():
                r = self.random.randint(0, 1)
                if r < self.leaving_probability: # leave food
                    neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius=2)
                    neighborhood = [cell for cell in neighborhood if not self.model.grid.has_food(cell)]
                else: # stay on food
                    neighborhood = self.model.grid.get_neighborhood_dist(self.pos, moore=True, radius=1)
                    neighborhood = [cell for cell in neighborhood if self.model.grid.has_food(cell)]
            else:
                neighborhood = self.model.grid.get_neighborhood_dist(self.pos, moore=True, radius=1)
                neighborhood = [cell for cell in neighborhood if self.model.grid.has_food(cell)]
        else:
            neighborhood = self.model.grid.get_neighborhood_dist(self.pos, moore=True, radius=2)

        possible_moves = [n for n in neighborhood if self.model.grid.is_cell_free(n)]
        if len(possible_moves) > 0:
            new_pos = self.random.choice(possible_moves)
            self.model.grid.move_agent(self, new_pos)
            self.pos = new_pos





class SPSocialWorm(SPSolitaryWorm, SocialWorm):
    """Class for the social worm in the strain-specific model"""
    def __init__(self, name: str, model: mesa.Model, pos: Tuple[int], leaving_probability: float = 0):
        super().__init__(name, model, pos, leaving_probability)
        self.feeding_rate = 0.4 * 0.62


    def at_food_border(self) -> bool:
        at_border = False
        direct_neighborhood = self.model.grid.get_neighborhood_dist(self.pos, moore=True, radius=1)
        remote_neighborhood = self.model.grid.get_neighborhood_dist(self.pos, moore=True, radius=2)
        direct_neighbors = self.model.grid.get_neighbors_dist(self.pos, moore=True, radius=1)
        remote_neighbors = self.model.grid.get_neighbors_dist(self.pos, moore=True, radius=2)
        direct_nofood = [cell for cell in direct_neighborhood if not self.model.grid.has_food(cell)]
        remote_nofood = [cell for cell in remote_neighborhood if not self.model.grid.has_food(cell)]
        if len(direct_neighbors) > 0 and len(direct_nofood) > 0:
            at_border = True
        elif len(direct_neighbors) == 0 and len(remote_neighbors) > 0 and len(remote_nofood) > 0:
            at_border = True
        elif len(direct_neighbors) == 0 and len(remote_neighbors) == 0 and len(remote_nofood) > 0:
            at_border = True
        return at_border
    
    def move(self) -> None:
        if self.sense_food():
            r = self.random.randint(0, 1)
            if self.at_food_border() and r < self.leaving_probability: # leave food
                neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius=2)
                neighborhood = [cell for cell in neighborhood if not self.model.grid.has_food(cell)]
            else:
                direct_neighbors = self.model.grid.get_neighbors_dist(self.pos, moore=True, radius=1)
                if len(direct_neighbors) > 0:
                    neighborhood = self.model.grid.get_neighborhood_dist(self.pos, moore=True, radius=1)
                    neighborhood = self.targeted_step(neighborhood, direct_neighbors)
                    neighborhood = [cell for cell in neighborhood if self.model.grid.has_food(cell)]
                else:
                    remote_neighbors = self.model.grid.get_neighbors_dist(self.pos, moore=True, radius=2)
                    if len(remote_neighbors) > 0:
                        neighborhood = self.model.grid.get_neighborhood_dist(self.pos, moore=True, radius=2)
                        neighborhood = self.targeted_step(neighborhood, remote_neighbors)
                        neighborhood = [cell for cell in neighborhood if self.model.grid.has_food(cell)]
                    else:
                        neighborhood = self.model.grid.get_neighborhood_dist(self.pos, moore=True, radius=2)
                        neighborhood = [cell for cell in neighborhood if self.model.grid.has_food(cell)]
        else:
            neighborhood = self.model.grid.get_neighborhood_dist(self.pos, moore=True, radius=2)
            
        possible_moves = [n for n in neighborhood if self.model.grid.is_cell_free(n)]
        if len(possible_moves) > 0:
            new_pos = self.random.choice(possible_moves)
            self.model.grid.move_agent(self, new_pos)
            self.pos = new_pos


class Food(mesa.Agent):
    def __init__(self, name: str, model: mesa.Model, pos: Tuple[int], quantity: float = 1):
        super().__init__(name, model)
        self.name = name
        self.pos = pos
        self.quantity = quantity

    def increase(self) -> None:
        self.quantity += 1

    def consume(self, qty: float) -> None:
        self.quantity -= qty
        if self.quantity <= 0:
            self.model.grid.remove_agent(self)

    def is_worm(self) -> bool:
        return False