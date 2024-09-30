import pygame
from pygame.locals import *
import pandas as pd
from run import ENV_SIZE, MAX_STEPS
import math
import numpy as np

class Simulator():

    width: int
    height: int
    margin: int

    def __init__(
            self,
            pos_data: pd.DataFrame,
            width: int = ENV_SIZE,
            height: int = ENV_SIZE,
    ) -> None:
        self.width = width
        self.height = height
        self.pos_data = pos_data
        self.num_agents = pos_data['AgentID'].max() + 1

    def run(self) -> None:
        pygame.init()

        canvas = pygame.display.set_mode((self.width, self.height))
        
        pygame.display.set_caption("Trajectories")
        
        running = True

        step = 0
        while running and step < MAX_STEPS:

            pygame.time.delay(100)

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_BACKSPACE:
                        running = False
                elif event.type == QUIT:
                    running = False

            canvas.fill((0, 0, 0))

            agent_positions = self.pos_data.loc[(self.pos_data['Step'] == step)][['posx', 'posy']].to_numpy()
            agent_velocities = self.pos_data.loc[(self.pos_data['Step'] == step)][['velx', 'vely']].to_numpy()

            for i in range(self.num_agents):
                color = 'red'
                distances = np.sqrt((agent_positions[i, 0] - agent_positions[:, 0]) ** 2 + (agent_positions[i, 1] - agent_positions[:, 1]) ** 2)
                neighbors = distances <= 10
                if sum(neighbors) > 1:
                    color = 'green'
                pos = agent_positions[i]
                vel = agent_velocities[i]

                pygame.draw.circle(canvas, color, pos, (5))
                arrow(canvas, "white", (255, 255, 255), pos, pos + vel * 10, 4, 2)
            
            pygame.display.update()
            step += 1


def arrow(screen, lcolor, tricolor, start, end, trirad, thickness=2):
    rad = math.pi / 180
    pygame.draw.line(screen, lcolor, start, end, thickness)
    rotation = (math.atan2(start[1] - end[1], end[0] - start[0])) + math.pi/2
    pygame.draw.polygon(screen, tricolor, ((end[0] + trirad * math.sin(rotation),
                                        end[1] + trirad * math.cos(rotation)),
                                       (end[0] + trirad * math.sin(rotation - 120*rad),
                                        end[1] + trirad * math.cos(rotation - 120*rad)),
                                       (end[0] + trirad * math.sin(rotation + 120*rad),
                                        end[1] + trirad * math.cos(rotation + 120*rad))))


if __name__ == "__main__":
    pos_data = pd.read_csv('position_data.csv')
    sim = Simulator(pos_data)
    sim.run()