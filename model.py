import mesa
from player import SolitaryWorm
from environment import WormEnvironment
import math
from typing import Tuple
import numpy as np

class WormSimulator(mesa.Model):
    def __init__(self, n_agents: int, dim_env: float, max_steps: int, multispot: bool, num_spots: int, clustered: bool,
                  attractive_w: float, repulsive_w: float, align_w: float):
        super().__init__()
        self.schedule = mesa.time.RandomActivation(self)
        self.env = WormEnvironment(dim_env, torus=True)

        self.adj_matrix = np.zeros((max_steps + 2, n_agents, n_agents))

        if clustered:
            self.clustered_agents(n_agents, multispot, num_spots)
        else:
            for i in range(n_agents):
                pos = (self.random.uniform(0, dim_env), self.random.uniform(0, dim_env))
                angle = self.random.random() * math.pi * 2 - math.pi
                a = WormSimulator.create_agent(self, self.next_id(), pos, angle, attractive_w, repulsive_w, align_w)
                self.schedule.add(a)
                self.env.place_agent(a, a.pos)

        self.adj_matrix[self.schedule.steps] = self.get_adj_matrix()

        self.datacollector = mesa.DataCollector(agent_reporters={'pos': 'pos', 'velx': 'velx', 'vely': 'vely', 
                                                                 'worm': 'is_worm', 'attractive': 'attractive', 'range': 'range'})
        self.datacollector.collect(self)

    def step(self) -> None:
        self.schedule.step()
        self.adj_matrix[self.schedule.steps] = self.get_adj_matrix()
        self.datacollector.collect(self)

    def get_adj_matrix(self) -> np.ndarray:
        worm_pos = np.array([a.pos for a in self.schedule.agents if a.is_worm])
        dist_mat = np.zeros(self.adj_matrix.shape[1:])
        for w in range(len(worm_pos)):
            dist_mat[w] = np.sqrt((worm_pos[w, 0] - worm_pos[:, 0]) ** 2 + (worm_pos[w, 1] - worm_pos[:, 1]) ** 2)
        adj_mat = np.zeros(self.adj_matrix.shape[1:])
        adj_mat[dist_mat <= 20] = 1 # max distance: 20
        adj_mat[dist_mat > 20] = 0
        return adj_mat
        
    def clustered_agents(self, num_agents: int,
                          multispot: bool = False, num_spots: int = 1) -> None:
        """Implements the clustered initial positions for the worms"""
        radius = math.ceil(math.sqrt(num_agents) / 2)
        if multispot:
            if num_spots == 1 or num_spots == 2:
                cluster_position = (self.env.dim_env - radius - 1, radius)
            else:
                cluster_position = (self.env.dim_env // 2, self.env.dim_env // 2)
        else:
            cluster_position = (self.random.randrange(0, self.env.dim_env), self.random.randrange(0, self.env.dim_env))
        neighborhood = self.env.get_neighborhood(cluster_position, True, True, radius)
        positions = self.random.sample(neighborhood, num_agents)
        for i in range(num_agents):
            a = WormSimulator.create_agent(self, i, positions[i])
            self.schedule.add(a)
            self.env.place_agent(a, a.pos)

    @staticmethod
    def create_agent(model: mesa.Model, n: int, pos: Tuple[float], vel: Tuple[float],
                    attractive_w = 0.4, repulsive_w = 0.4, align_w = 0.2) -> mesa.Agent:
        agent = SolitaryWorm(n, model, pos, vel, attractive_w=attractive_w, repulsive_w=repulsive_w, 
                             align_w=align_w, sensing_range=20, align_dist=10, pheromone_prob=0.5)
        return agent