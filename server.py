from model import WormSimulator, SolitaryWorm, SocialWorm, Food
import mesa
from typing import Dict

WORM_COLOR = "#00CC00"
FOOD_COLOR = ["#b3cde0", "#6497b1", "#005b96", "#03396c", "#011f4b"]

GRID_SIZE = 50


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
        portrayal["Color"] = FOOD_COLOR[food_level(agent.quantity)]
        portrayal["w"] = 0.9
        portrayal["h"] = 0.9
        portrayal["Layer"] = 0

    return portrayal

def food_level(qty: int) -> int:
    if qty < 2:
        return 0
    elif qty < 3:
        return 1
    elif qty < 5:
        return 2
    elif qty < 7:
        return 3
    else:
        return 4

model_params = {
    "n_agents": mesa.visualization.Slider(
        "Number of agents",
        200,
        100,
        500,
    ),
    "dim_grid": GRID_SIZE,
    "social": mesa.visualization.Checkbox(
        "Social Agents",
        False,
    ),
    "clustering": mesa.visualization.Slider(
        "Food degree of clustering",
        200,
        0,
        1000,
    ),
    "n_spot": mesa.visualization.Slider(
        "Number of food spot",
        1,
        1,
        4,
    ),
    "multispot_food": mesa.visualization.Checkbox(
        "Multispot",
        False,
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