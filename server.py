from model import WormSimulator, SolitaryWorm, SocialWorm, Food
import mesa
from typing import Dict
from colour import Color

WORM_COLOR = "#FF0000"
FOOD_PALETTE = list(Color('blue').range_to(Color('yellow'), 50))

GRID_SIZE = 35
N_FOOD = GRID_SIZE**2 * 10

def agent_portrayal(agent: mesa.Agent) -> Dict:

    portrayal = {
        "x": agent.pos[0],
        "y": agent.pos[1],
        "Filled": "true",
    }

    if type(agent) is SolitaryWorm:
        portrayal["Shape"] = "circle"
        portrayal["Color"] = WORM_COLOR
        portrayal["r"] = 0.5
        portrayal["Layer"] = 1

    if type(agent) is SocialWorm:
        portrayal["Shape"] = "circle"
        portrayal["Color"] = WORM_COLOR
        portrayal["r"] = 0.5
        portrayal["Layer"] = 1

    elif type(agent) is Food:
        portrayal["Shape"] = "rect"
        portrayal["Color"] = food_color(agent.quantity)
        portrayal["w"] = 0.9
        portrayal["h"] = 0.9
        portrayal["Layer"] = 0

    return portrayal

def food_color(qty: int) -> int:
    if qty >= len(FOOD_PALETTE):
        return FOOD_PALETTE[-1].hex
    else:
        return FOOD_PALETTE[qty].hex
        

model_params = {
    "n_agents": mesa.visualization.Slider(
        "Number of agents",
        40,
        10,
        100,
    ),
    "social": mesa.visualization.Checkbox(
        "Social Agents",
        False,
    ),
    "clustered": mesa.visualization.Checkbox(
        "Clustered Agents",
        False,
    ),
    "n_food": mesa.visualization.Slider(
        "Food Quantity",
        N_FOOD,
        1000,
        100000,
    ),
    "clustering": mesa.visualization.Slider(
        "Food degree of clustering",
        1,
        0,
        3,
    ),
    "dim_grid": GRID_SIZE,
    "multispot": mesa.visualization.Checkbox(
        "Multispot Food Distribution",
        False,
    ),
    "num_spots": mesa.visualization.Choice(
        "Number of food spots",
        1,
        [1, 2, 4],
    ),
}

canvas_element = mesa.visualization.CanvasGrid(agent_portrayal, GRID_SIZE, GRID_SIZE, 600, 600)

chart = mesa.visualization.ChartModule(
    [
        {"Label": "Food", "Color": "#648FFF"},
    ],
    data_collector_name="datacollector"
)

# create instance of Mesa ModularServer
server = mesa.visualization.ModularServer(
    WormSimulator,
    [canvas_element, chart],
    "Worm Model",
    model_params=model_params,
)