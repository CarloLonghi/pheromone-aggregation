import mesa
from mesa.space import Coordinate
from typing import Tuple, Sequence
import math
import numpy as np


class SolitaryWorm(mesa.Agent):
    """Class for the solitary worm in the minimal model"""
    def __init__(self, name: str, model: mesa.Model, pos: Tuple[float], vel: Tuple[float], speed: float = 5,
                  align_dist: float = 10, align_w: float = 0.2, sensing_range: float = 100, attractive_w = 0.2):
        super().__init__(name, model)
        self.name = name
        self.posx, self.posy = pos
        self.velx, self.vely = vel
        self.speed = speed
        self.align_dist = align_dist
        self.align_w = align_w
        self.sensing_range = sensing_range
        self.attraction_pheromone = False
        self.attractive_w = attractive_w
        self.is_worm = True

    def sense_pheromone(self) -> bool:
        self.attraction_pheromone = False
        self.repulsion_pheromone = False
        pheromone = self.model.env.get_pheromone(self.pos, self.sensing_range, True)

        att_pheromone = [ph for ph in pheromone if ph.attractive]
        rep_pheromone = [ph for ph in pheromone if not ph.attractive]
        if len(att_pheromone) > 0:
            self.attraction_pheromone = True
            pos = np.array([(ph.posx, ph.posy) for ph in att_pheromone])
            strength = np.array([ph.quantity for ph in att_pheromone])
            self.attraction_pos = np.average(pos, axis=0, weights=strength)

        if len(rep_pheromone):
            self.repulsion_pheromone = True
            pos = np.array([(ph.posx, ph.posy) for ph in rep_pheromone])
            strength = np.array([ph.quantity for ph in rep_pheromone])
            self.repulsion_pos = np.average(pos, axis=0, weights=strength)
            

    def move(self) -> None:
        angle = self.random.random() * math.pi * 2
        self.velx = math.cos(angle)
        self.vely = math.sin(angle)

        worm_neighbors = self.model.env.get_neighbor_worms(self.pos, self.align_dist, False)
        n_neighbors = len(worm_neighbors)
        if n_neighbors > 0:
            neighbors_vels = [(a.velx, a.vely) for a in worm_neighbors]
            align_vel = (sum([v[0] for v in neighbors_vels]) / n_neighbors, sum([v[1] for v in neighbors_vels]) / n_neighbors)
            self.velx = self.align_w * align_vel[0] + (1 - self.align_w - self.attractive_w) * self.velx
            self.vely = self.align_w * align_vel[1] + (1 - self.align_w - self.attractive_w) * self.vely

        if self.attraction_pheromone:
            attractive_step = (self.attraction_pos[0] - self.posx, self.attraction_pos[1] - self.posy)
            self.velx += self.attractive_w * attractive_step[0]
            self.vely += self.attractive_w * attractive_step[1]

        if self.repulsion_pheromone:
            repulsive_step = (self.posx - self.repulsion_pos[0], self.posy - self.repulsion_pos[1])
            self.velx += self.attractive_w * repulsive_step[0]
            self.vely += self.attractive_w * repulsive_step[1]

        # normalize the velocity
        speed = math.sqrt(self.velx ** 2 + self.vely ** 2) / self.speed
        self.velx = self.velx / speed
        self.vely = self.vely / speed

        # update the position
        newpos = (self.posx + self.velx, self.posy + self.vely)
        self.posx, self.posy = self.model.env.torus_adj(newpos)

    def emit_pheromone(self) -> bool:
        ph_att = Pheromone(self.model.next_id(), self.model, (self.posx, self.posy), attractive=True)
        self.model.schedule.add(ph_att)
        self.model.env.place_agent(ph_att, (self.posx, self.posy))

        ph_rep = Pheromone(self.model.next_id(), self.model, (self.posx, self.posy), attractive=False)
        self.model.schedule.add(ph_rep)
        self.model.env.place_agent(ph_rep, (self.posx, self.posy))

    def is_worm(self) -> bool:
        return True

    def step(self) -> None:
        self.emit_pheromone()
        self.sense_pheromone()
        self.move()




class SocialWorm(SolitaryWorm):
    """Class for the social worm in the minimal model"""
    def __init__(self, name: str, model: mesa.Model, pos: Tuple[int]):
        super().__init__(name, model, pos)

    def move(self) -> None:
        near_food = self.sense_food()
        if near_food:
            neighborhood = self.model.env.get_neighborhood_dist(self.pos, moore=True, radius=1)
            worm_neighbors = self.model.env.get_neighbors_dist(self.pos, moore=True, radius=1)
            if len(worm_neighbors) > 0:
                neighborhood = self.targeted_step(neighborhood, worm_neighbors)
        else:
            neighborhood = self.model.env.get_neighborhood_dist(self.pos, moore=True, radius=2)

        possible_moves = [n for n in neighborhood if self.model.env.is_cell_free(n)]
        if len(possible_moves) > 0:
            new_pos = self.random.choice(neighborhood)
            self.model.env.move_agent(self, new_pos)
            self.pos = new_pos

    def targeted_step(self, neighborhood: Sequence[Coordinate], worm_neighbors: Sequence[mesa.Agent]) -> Sequence[Coordinate]:
        social_neighborhood = set()
        for worm in worm_neighbors:
            other_neighborhood = self.model.env.get_neighborhood_dist(worm.pos, moore=True, radius=1)
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
        direct_neighborhood = self.model.env.get_neighborhood_dist(self.pos, moore=True, radius=1)
        direct_nofood = [cell for cell in direct_neighborhood if not self.model.env.has_food(cell)]
        if len(direct_nofood) > 0:
            at_border = True
        return at_border
    
    def move(self) -> None:
        if self.sense_food():
            if self.at_food_border():
                r = self.random.randint(0, 1)
                if r < self.leaving_probability: # leave food
                    neighborhood = self.model.env.get_neighborhood(self.pos, moore=True, include_center=False, radius=2)
                    neighborhood = [cell for cell in neighborhood if not self.model.env.has_food(cell)]
                else: # stay on food
                    neighborhood = self.model.env.get_neighborhood_dist(self.pos, moore=True, radius=1)
                    neighborhood = [cell for cell in neighborhood if self.model.env.has_food(cell)]
            else:
                neighborhood = self.model.env.get_neighborhood_dist(self.pos, moore=True, radius=1)
                neighborhood = [cell for cell in neighborhood if self.model.env.has_food(cell)]
        else:
            neighborhood = self.model.env.get_neighborhood_dist(self.pos, moore=True, radius=2)

        possible_moves = [n for n in neighborhood if self.model.env.is_cell_free(n)]
        if len(possible_moves) > 0:
            new_pos = self.random.choice(possible_moves)
            self.model.env.move_agent(self, new_pos)
            self.pos = new_pos





class SPSocialWorm(SPSolitaryWorm, SocialWorm):
    """Class for the social worm in the strain-specific model"""
    def __init__(self, name: str, model: mesa.Model, pos: Tuple[int], leaving_probability: float = 0):
        super().__init__(name, model, pos, leaving_probability)
        self.feeding_rate = 0.4 * 0.62


    def at_food_border(self) -> bool:
        at_border = False
        direct_neighborhood = self.model.env.get_neighborhood_dist(self.pos, moore=True, radius=1)
        remote_neighborhood = self.model.env.get_neighborhood_dist(self.pos, moore=True, radius=2)
        direct_neighbors = self.model.env.get_neighbors_dist(self.pos, moore=True, radius=1)
        remote_neighbors = self.model.env.get_neighbors_dist(self.pos, moore=True, radius=2)
        direct_nofood = [cell for cell in direct_neighborhood if not self.model.env.has_food(cell)]
        remote_nofood = [cell for cell in remote_neighborhood if not self.model.env.has_food(cell)]
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
                neighborhood = self.model.env.get_neighborhood(self.pos, moore=True, include_center=False, radius=2)
                neighborhood = [cell for cell in neighborhood if not self.model.env.has_food(cell)]
            else:
                direct_neighbors = self.model.env.get_neighbors_dist(self.pos, moore=True, radius=1)
                if len(direct_neighbors) > 0:
                    neighborhood = self.model.env.get_neighborhood_dist(self.pos, moore=True, radius=1)
                    neighborhood = self.targeted_step(neighborhood, direct_neighbors)
                    neighborhood = [cell for cell in neighborhood if self.model.env.has_food(cell)]
                else:
                    remote_neighbors = self.model.env.get_neighbors_dist(self.pos, moore=True, radius=2)
                    if len(remote_neighbors) > 0:
                        neighborhood = self.model.env.get_neighborhood_dist(self.pos, moore=True, radius=2)
                        neighborhood = self.targeted_step(neighborhood, remote_neighbors)
                        neighborhood = [cell for cell in neighborhood if self.model.env.has_food(cell)]
                    else:
                        neighborhood = self.model.env.get_neighborhood_dist(self.pos, moore=True, radius=2)
                        neighborhood = [cell for cell in neighborhood if self.model.env.has_food(cell)]
        else:
            neighborhood = self.model.env.get_neighborhood_dist(self.pos, moore=True, radius=2)
            
        possible_moves = [n for n in neighborhood if self.model.env.is_cell_free(n)]
        if len(possible_moves) > 0:
            new_pos = self.random.choice(possible_moves)
            self.model.env.move_agent(self, new_pos)
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
            self.model.env.remove_agent(self)

    def is_worm(self) -> bool:
        return False
    
class Pheromone(mesa.Agent):
    def __init__(self, name: str, model: mesa.Model, pos: Tuple[int], attractive: bool, quantity: float = 1, speed: float = 1, volatility_rate: float = 0.01):
        super().__init__(name, model)
        self.name = name
        self.posx, self.posy = pos
        self.attractive = attractive
        self.quantity = quantity
        self.velx = 0
        self.vely = 0
        self.speed = speed
        self.volatility_rate = volatility_rate
        self.is_worm = False

    def disperse(self, qty: float) -> None:
        self.quantity -= qty
        if self.quantity <= 0:
            self.model.env.remove_agent(self)
            self.model.schedule.remove(self)

    def move(self) -> None:
        angle = self.random.random() * math.pi * 2
        self.velx = math.cos(angle)
        self.vely = math.sin(angle)

        # normalize the velocity
        speed = math.sqrt(self.velx ** 2 + self.vely ** 2) * self.speed
        self.velx = self.velx / speed
        self.vely = self.vely / speed

        # update the position
        newpos = (self.posx + self.velx, self.posy + self.vely)
        self.posx, self.posy = self.model.env.torus_adj(newpos)

    def step(self) -> None:
        self.disperse(self.volatility_rate)
        self.move()

    def is_worm(self) -> bool:
        return False