import mesa
from mesa.space import Coordinate
from mesa.agent import Agent
from player import Food, SocialWorm, SolitaryWorm

class WormEnvironment(mesa.space.MultiGrid):

    def __init__(self, width: int, height: int, torus: bool) -> None:
        super().__init__(width, height, torus)

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
