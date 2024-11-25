import mesa
from mesa.space import Coordinate
from typing import Tuple, Sequence
import math
import numpy as np


class SolitaryWorm(mesa.Agent):
    """Class for the solitary worm in the minimal model"""
    def __init__(self, name: str, model: mesa.Model, pos: Tuple[float], angle: float, speed: float = 5,
                  align_dist: float = 5, align_w: float = 0.2, sensing_range: float = 100, attractive_w = 0.2, repulsive_w = 0.2,
                  pheromone_prob: int = 0.5):
        super().__init__(name, model)
        self.name = name
        self.pos = pos
        self.angle = angle
        self.speed = speed
        self.align_dist = align_dist
        self.sensing_range = sensing_range
        self.pheromone_prob = pheromone_prob
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

        pheromone, positions, dist = self.model.env.get_pheromone(self.pos)

        att_pheromone = [ph for ph in pheromone if ph.attractive]
        att_pos = [positions[i] for i in range(len(positions)) if pheromone[i].attractive]
        att_dist = [dist[i] for i in range(len(dist)) if pheromone[i].attractive]
        rep_pheromone = [ph for ph in pheromone if not ph.attractive]
        rep_pos = [positions[i] for i in range(len(positions)) if not pheromone[i].attractive]
        rep_dist = [dist[i] for i in range(len(dist)) if not pheromone[i].attractive]
        if len(att_pheromone) > 0:
            self.attraction_pheromone = True
            strengths = [att_pheromone[i].get_val(att_dist[i]) for i in range(len(att_pheromone))]
            self.attraction_pos = np.average(att_pos, axis=0, weights=strengths)

        if len(rep_pheromone):
            self.repulsion_pheromone = True
            strengths = [rep_pheromone[i].get_val(rep_dist[i]) for i in range(len(rep_pheromone))]
            self.repulsion_pos = np.average(rep_pos, axis=0, weights=strengths)
            

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
        if np.random.uniform() > self.pheromone_prob:
            ph_att = Pheromone(self.model.next_id(), self.model, self.pos, attractive=True, quantity=1, diffusion=2, threshold=0.05)
            self.model.schedule.add(ph_att)
            self.model.env.place_agent(ph_att, ph_att.pos)

        if np.random.uniform() > self.pheromone_prob:
            ph_rep = Pheromone(self.model.next_id(), self.model, self.pos, attractive=False, quantity=1, diffusion=1, threshold=0.05)
            self.model.schedule.add(ph_rep)
            self.model.env.place_agent(ph_rep, ph_rep.pos)

    def is_worm(self) -> bool:
        return True

    def step(self) -> None:
        self.sense_pheromone()
        self.emit_pheromone()
        self.move()

class Pheromone(mesa.Agent):
    def __init__(self, name: str, model: mesa.Model, pos: Tuple[int], attractive: bool, quantity: float = 1,
                  diffusion: float = 1.0, threshold: float = 0.1, decay_rate: float = 0.1):
        super().__init__(name, model)
        self.name = name
        self.pos = pos
        self.attractive = attractive
        self.quantity = quantity
        self.velx = 0
        self.vely = 0
        self.is_worm = False
        self.D = diffusion
        self.t = 1
        self.thresh = threshold
        self.range = np.sqrt(-4*self.D*self.t*np.log(self.thresh*np.sqrt(4*np.pi*self.D*self.t)))
        self.decay_rate = decay_rate
        self.model.env.add_pheromone(self)

    def disperse(self,) -> None:
        max = self.quantity / np.sqrt(4 * np.pi * self.D * self.t) - self.decay_rate * self.t
        if max < self.thresh:
            self.model.env.remove_agent(self)
            self.model.schedule.remove(self)

    def update_range(self,) -> None:
        self.range = np.sqrt(-4*self.D*self.t*np.log((self.thresh+self.decay_rate*self.t)*np.sqrt(4*np.pi*self.D*self.t)))

    def get_val(self, dist) -> float:
        val = np.exp(-(dist) / (4 * self.D * self.t)) / np.sqrt(4 * np.pi * self.D * self.t) - self.decay_rate * self.t
        return val

    def step(self) -> None:
        self.disperse()
        self.update_range()
        self.t += 1

    def is_worm(self) -> bool:
        return False