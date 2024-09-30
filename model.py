import mesa
from player import SolitaryWorm, SocialWorm, SPSocialWorm, SPSolitaryWorm
from environment import WormEnvironment
import math
from typing import Tuple

class WormSimulator(mesa.Model):
    def __init__(self, n_agents: int, dim_env: float, social: bool,
                  multispot: bool, num_spots: int, clustered: bool, strain_specific: bool):
        super().__init__()
        self.schedule = mesa.time.RandomActivation(self)
        self.env = WormEnvironment(dim_env, torus=True)

        if clustered:
            self.clustered_agents(n_agents, social, strain_specific, multispot, num_spots)
        else:
            for i in range(n_agents):
                pos = (self.random.uniform(0, dim_env), self.random.uniform(0, dim_env))
                vel = (self.random.gauss(mu = 0., sigma = 1.), self.random.gauss(mu = 0., sigma = 1.))
                a = WormSimulator.create_agent(self, social, strain_specific, i, pos, vel)
                self.schedule.add(a)
                self.env.place_agent(a, (a.posx, a.posy))

        self.datacollector = mesa.DataCollector(agent_reporters={'posx': 'posx', 'posy': 'posy', 'velx': 'velx', 'vely': 'vely'})
        self.datacollector.collect(self)

    def step(self) -> None:
        self.schedule.step()
        self.datacollector.collect(self)

    def clustered_agents(self, num_agents: int, social: bool, strain_specific: bool = False,
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
            a = WormSimulator.create_agent(self, social, strain_specific, i, positions[i])
            self.schedule.add(a)
            self.env.place_agent(a, a.pos)

    @staticmethod
    def create_agent(model: mesa.Model, social: bool, strain_specific: bool, n: int, pos: Tuple[float], vel: Tuple[float]) -> mesa.Agent:
        agent = None
        if strain_specific:
            if social:
                agent = SPSocialWorm(n, model, pos)
            else:
                agent = SPSolitaryWorm(n, model, pos)
        else:
            if social:
                agent = SocialWorm(n, model, pos)
            else:
                agent = SolitaryWorm(n, model, pos, vel)
        return agent