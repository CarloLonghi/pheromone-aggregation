import mesa
from mesa.space import Coordinate
from mesa.agent import Agent
from typing import Sequence, Tuple


class WormEnvironment(mesa.space.ContinuousSpace):

    def __init__(self, dim_env: float, torus: bool) -> None:
        super().__init__(dim_env, dim_env, torus)
        self.dim_env = dim_env
        # Additional attributes to track foraging efficiency metrics
        self.foraging_attempts = 0
        self.successful_foraging_attempts = 0

    def get_neighbor_worms(self, pos: Coordinate, radius: int = 1, include_center: bool = False) -> list[Agent]:
        agents = list(self.get_neighbors(pos, radius, include_center))
        worms = [a for a in agents if a.is_worm]
        return worms
    
    def get_pheromone(self, pos: Coordinate, radius: int = 1, include_center: bool = True) -> list[Agent]:
        agents = list(self.get_neighbors(pos, radius, include_center))
        pheromones = [a for a in agents if not a.is_worm]
        return pheromones 

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
