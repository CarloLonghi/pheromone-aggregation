import mesa
from mesa.space import Coordinate
from mesa.agent import Agent
from typing import Sequence, Tuple, List
from player import Pheromone
import numpy as np

class WormEnvironment(mesa.space.ContinuousSpace):

    def __init__(self, dim_env: float, torus: bool) -> None:
        super().__init__(dim_env, dim_env, torus)
        self.dim_env = dim_env
        # Additional attributes to track foraging efficiency metrics
        self.foraging_attempts = 0
        self.successful_foraging_attempts = 0
        self.pheromone = []

    def get_neighbor_worms(self, pos: Coordinate, radius: int = 1, include_center: bool = False) -> list[Agent]:
        agents = list(self.get_neighbors(pos, radius, include_center))
        worms = [a for a in agents if a.is_worm]
        return worms

    def get_neighborhood_dist(self, pos: Coordinate, moore: bool = False, radius: int = 1) -> Sequence[Coordinate]:
        """
        Returns a list of cells at a certain distance of a certain point.
        It works as get_neighborhood but only returns those cells on the border of the neighborhood.
        Args:
            pos: Coordinate tuple for the neighborhood to get.
            moore: If True, return Moore neighborhood
                   (including diagonals)
                   If False, return Von Neumann neighborhood
                   (exclude diagonals)
            radius: radius, in cells, of neighborhood to get.

        Returns:
            A list of coordinate tuples representing the cells at distance d.
        """
        x, y = pos
        cells = []

        for cell in self.get_neighborhood(pos, moore, False, radius):
            dx = abs(cell[0] - x)
            dy = abs(cell[1] - y)
            if self.torus:
                dx = min(dx, self.dim_env - dx)
                dy = min(dy, self.dim_env - dy)
            if moore:
                if dx == radius or dy == radius:
                    cells.append(cell)
            else:
                if dx + dy == radius:
                    cells.append(cell)
        return cells

    def get_neighbors_dist(self, pos: Coordinate, moore: bool = False, radius: int = 1) -> Sequence[Coordinate]:
        """
        Returns a list of neighbors at a certain distance of a certain point.
        It works as get_neighborhood but only returns those cells on the border of the neighborhood.
        Args:
            pos: Coordinate tuple for the neighborhood to get.
            moore: If True, return Moore neighborhood
                   (including diagonals)
                   If False, return Von Neumann neighborhood
                   (exclude diagonals)
            radius: radius, in cells, of neighborhood to get.

        Returns:
            A list of coordinate tuples representing the cells at distance d.
        """
        neighborhood = self.get_neighborhood_dist(pos, moore, radius)
        neighbors = list(self.iter_cell_list_contents(neighborhood))
        return [n for n in neighbors if n.is_worm()]

    def add_pheromone(self, ph: Pheromone):
        self.pheromone += [ph,]

    def get_pheromone(self, pos: Coordinate) -> List[Pheromone]:
        if len(self.pheromone) > 0:
            posx = np.array([ph.pos[0] for ph in self.pheromone])
            diffx = posx - pos[0]
            pos_diff = diffx > 0
            diffx = np.abs(diffx)
            torus_adj = diffx > (self.dim_env / 2)
            posx[pos_diff * torus_adj] -= self.dim_env
            posx[(~pos_diff) * torus_adj] += self.dim_env
            diffx[torus_adj] = self.dim_env - diffx[torus_adj]
            posy = np.array([ph.pos[1] for ph in self.pheromone])
            diffy = posy - pos[1]
            pos_diff = diffy > 0
            diffy = np.abs(diffy)
            torus_adj = diffy > (self.dim_env / 2)
            posy[pos_diff * torus_adj] -= self.dim_env
            posy[(~pos_diff) * torus_adj] += self.dim_env
            diffy[torus_adj] = self.dim_env - diffy[torus_adj]
            dist = [diffx[i]**2 + diffy[i]**2 for i in range(len(self.pheromone))]
            active = [dist[i] < self.pheromone[i].range**2 for i in range(len(self.pheromone))]
            positions = list(zip(posx, posy))

            return ([self.pheromone[i] for i in range(len(self.pheromone)) if active[i]],
                    [positions[i] for i in range(len(positions)) if active[i]],
                    [dist[i] for i in range(len(dist)) if active[i]])
        else:
            return [], [], []
        
    def remove_agent(self, agent):
        if not agent.is_worm:
            self.pheromone.remove(agent)
        return super().remove_agent(agent)