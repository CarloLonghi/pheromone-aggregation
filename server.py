from model import WormSimulator, SolitaryWorm, SocialWorm, Food
import mesa

WORM_COLOR = "#00CC00"
FOOD_COLOR = "#FFFF00"

GRID_SIZE = 50

def agent_portrayal(agent):

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
        portrayal["Color"] = FOOD_COLOR
        portrayal["w"] = 0.9
        portrayal["h"] = 0.9
        portrayal["Layer"] = 0

    return portrayal

model_params = {
    "n_agents": mesa.visualization.Slider(
        "Number of agents",
        200,
        100,
        500,
    ),
    "n_food": mesa.visualization.Slider(
        "Number of food spots",
        1000,
        500,
        10000,
    ),
    "dim_grid": GRID_SIZE,
    "social": mesa.visualization.Checkbox(
        "Social Agents",
        False,
    )
}

canvas_element = mesa.visualization.CanvasGrid(agent_portrayal, GRID_SIZE, GRID_SIZE, 700, 700)

# create instance of Mesa ModularServer
server = mesa.visualization.ModularServer(
    WormSimulator,
    [canvas_element],
    "Worm Model",
    model_params=model_params,
)