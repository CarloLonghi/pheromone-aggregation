import mesa
from mesa.space import Coordinate
from typing import Tuple, Sequence
import math
import numpy as np


class SolitaryWorm(mesa.Agent):
    """Class for the solitary worm in the minimal model"""
    def __init__(self, name: str, model: mesa.Model, pos: Tuple[float], angle: float, speed: float = 5,
                  align_dist: float = 5, align_w: float = 0.2, sensing_range: float = 100, attractive_w = 0.2, repulsive_w = 0.2):
        super().__init__(name, model)
        self.name = name
        self.pos = pos
        self.angle = angle
        self.speed = speed
        self.align_dist = align_dist
        self.sensing_range = sensing_range
        self.is_worm = True

        if align_w + attractive_w + repulsive_w <= 1:
            self.align_w = align_w
            self.attractive_w = attractive_w
            self.repulsive_w = repulsive_w            
        else:
            raise Exception(f'The sum of the alignment, attraction and repulsion weights is {align_w + attractive_w + repulsive_w} but it must be <1.0')

    def sense_pheromone(self) -> bool:
        self.attraction_pheromone = False
        self.repulsion_pheromone = False
        pheromone = self.model.env.get_pheromone(self.pos, self.sensing_range, True)

        att_pheromone = [ph for ph in pheromone if ph.attractive]
        rep_pheromone = [ph for ph in pheromone if not ph.attractive]
        if len(att_pheromone) > 0:
            self.attraction_pheromone = True
            posx = np.array([ph.pos[0] for ph in att_pheromone])
            posx[posx - self.pos[0] > self.sensing_range] -= self.model.env.dim_env
            posx[posx - self.pos[0] < -self.sensing_range] += self.model.env.dim_env
            posy = np.array([ph.pos[1] for ph in att_pheromone])
            posy[posy - self.pos[1] > self.sensing_range] -= self.model.env.dim_env
            posy[posy - self.pos[1] < -self.sensing_range] += self.model.env.dim_env  
            pos = [(posx[p], posy[p]) for p in range(len(att_pheromone))]          
            strength = np.array([ph.quantity for ph in att_pheromone])
            self.attraction_pos = np.average(pos, axis=0, weights=strength)

        if len(rep_pheromone):
            self.repulsion_pheromone = True
            posx = np.array([ph.pos[0] for ph in rep_pheromone])
            posx[posx - self.pos[0] > self.sensing_range] -= self.model.env.dim_env
            posx[posx - self.pos[0] < -self.sensing_range] += self.model.env.dim_env
            posy = np.array([ph.pos[1] for ph in rep_pheromone])
            posy[posy - self.pos[1] > self.sensing_range] -= self.model.env.dim_env
            posy[posy - self.pos[1] < -self.sensing_range] += self.model.env.dim_env  
            pos = [(posx[p], posy[p]) for p in range(len(rep_pheromone))]              
            strength = np.array([ph.quantity for ph in rep_pheromone])
            self.repulsion_pos = np.average(pos, axis=0, weights=strength)
            

    def move(self) -> None:
        self.angle = self.random.random() * math.pi * 2

        worm_neighbors = self.model.env.get_neighbor_worms(self.pos, self.align_dist, False)
        n_neighbors = len(worm_neighbors)
        align_angle = 0; attr_angle = 0; rep_angle = 0
        total_w = 0
        if n_neighbors > 0: # alignment
            neighbors_dirs = [a.angle for a in worm_neighbors]
            align_angle = sum(neighbors_dirs) / n_neighbors
            total_w += self.align_w

        if self.attraction_pheromone: # attraction
            attractive_step = (self.attraction_pos[0] - self.pos[0], self.attraction_pos[1] - self.pos[1])
            attr_angle = np.arctan2(attractive_step[1], attractive_step[0])
            total_w += self.attractive_w

        if self.repulsion_pheromone: # repulsion
            repulsive_step = (self.pos[0] - self.repulsion_pos[0], self.pos[1] - self.repulsion_pos[1])
            rep_angle = np.arctan2(repulsive_step[1], repulsive_step[0])
            total_w += self.repulsive_w

        total_w += 1 - self.align_w - self.attractive_w - self.repulsive_w
        alw = 0; atw = 0; rew = 0; rww = 0
        if n_neighbors > 0:
            alw = self.align_w / total_w
        if self.attraction_pheromone:
            atw = self.attractive_w / total_w
        if self.repulsion_pheromone:
            rew = self.repulsive_w / total_w
        rww = (1 - self.align_w - self.attractive_w - self.repulsive_w) / total_w
        self.angle = alw * align_angle + atw * attr_angle + rew * rep_angle + rww * self.angle

        velx = np.cos(self.angle) * self.speed
        vely = np.sin(self.angle) * self.speed

        # update the position
        newpos = (self.pos[0] + velx, self.pos[1] + vely)
        self.pos = self.model.env.torus_adj(newpos)

    def emit_pheromone(self) -> bool:
        ph_att = Pheromone(self.model.next_id(), self.model, self.pos, attractive=True, speed=10,
                            quantity=1, decay_rate=0.1)
        self.model.schedule.add(ph_att)
        self.model.env.place_agent(ph_att, ph_att.pos)

        ph_rep = Pheromone(self.model.next_id(), self.model, self.pos, attractive=False, speed=1,
                           quantity=1, decay_rate=0.1)
        self.model.schedule.add(ph_rep)
        self.model.env.place_agent(ph_rep, ph_rep.pos)

    def is_worm(self) -> bool:
        return True

    def step(self) -> None:
        self.sense_pheromone()
        self.emit_pheromone()
        self.move()

class Pheromone(mesa.Agent):
    def __init__(self, name: str, model: mesa.Model, pos: Tuple[int], attractive: bool, quantity: float = 1, speed: float = 1, decay_rate: float = 0.01):
        super().__init__(name, model)
        self.name = name
        self.pos = pos
        self.attractive = attractive
        self.quantity = quantity
        self.velx = 0
        self.vely = 0
        self.speed = speed
        self.decay_rate = decay_rate
        self.is_worm = False

    def disperse(self, qty: float) -> None:
        self.quantity -= qty
        if self.quantity <= 0:
            self.model.env.remove_agent(self)
            self.model.schedule.remove(self)

    def move(self) -> None:
        angle = self.random.random() * math.pi * 2
        if self.pos is None:
            print('here')
        self.velx = math.cos(angle) * self.speed
        self.vely = math.sin(angle) * self.speed

        # update the position
        newpos = (self.pos[0] + self.velx, self.pos[1] + self.vely)
        self.pos = self.model.env.torus_adj(newpos)

    def step(self) -> None:
        self.move()
        self.disperse(self.decay_rate)

    def is_worm(self) -> bool:
        return False