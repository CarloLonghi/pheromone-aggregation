import mesa
from mesa.space import Coordinate
from mesa.agent import Agent
from player import Food, SocialWorm, SolitaryWorm
from typing import Sequence
import math
from random import Random

class WormEnvironment(mesa.space.MultiGrid):

    def __init__(self, dim_grid: int, torus: bool) -> None:
        super().__init__(dim_grid, dim_grid, torus)
        self.dim_grid = dim_grid

    def is_cell_free(self, pos: Coordinate) -> bool:
        x, y = pos
        num_worms = sum([type(agent) != Food for agent in self._grid[x][y]])
        return num_worms == 0
    
    def has_food(self, pos: Coordinate) -> bool:
        x, y = pos
        num_food = sum([type(agent) == Food for agent in self._grid[x][y]])
        return num_food > 0
    
    def get_neighbor_worms(self, pos: Coordinate, moore: bool, radius: int = 1) -> list[Agent]:
        agents = list(self.iter_neighbors(pos, moore, False, radius))
        worms = [a for a in agents if a.is_worm()]
        return worms
    
    def place_food(self, pos: Coordinate, f: Food) -> None:
        x, y = pos
        food = [agent for agent in self._grid[x][y] if type(agent) == Food]
        if len(food) > 0:
            food[0].increase()
        else:
            self._grid[x][y].append(f)
            if self._empties_built:
                self._empties.discard(pos)

    def consume_food(self, pos: Coordinate) -> None:
        x, y = pos
        food = [agent for agent in self._grid[x][y] if type(agent) == Food]
        if len(food) > 0:
            food[0].consume()

    def food_quantity(self, pos: Coordinate) -> int:
        x, y = pos
        return sum([agent.quantity for agent in self._grid[x][y] if type(agent) == Food])

    def get_total_food(self) -> int:
        return sum([self.food_quantity(pos) for _, pos in self.coord_iter()])
    
    def get_cells_from(self, pos: Coordinate, moore: bool = False, radius: int = 1) -> Sequence[Coordinate]:
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

        for cell in self.iter_neighborhood(pos, moore, False, radius):
            dx = abs(cell[0] - x)
            dy = abs(cell[1] - y)
            if self.torus:
                dx = min(dx, self.dim_grid - dx)
                dy = min(dy, self.dim_grid - dy)
            if moore:
                if dx == radius or dy == radius:
                    cells.append(cell)
            else:
                if dx + dy == radius:
                    cells.append(cell)
        return cells
