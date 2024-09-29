import pygame
from pygame.locals import *
import pandas as pd
from run import ENV_SIZE, MAX_STEPS

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

            pygame.time.delay(30)

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_BACKSPACE:
                        running = False
                elif event.type == QUIT:
                    running = False

            canvas.fill((0, 0, 0))

            for i in range(self.num_agents):
                agent_data = self.pos_data.loc[(self.pos_data['Step'] == step) & (self.pos_data['AgentID'] == i)].iloc[0]
                pos = (agent_data['posx'], agent_data['posy'])
                #pos = (self.pos_data.iloc[step]['posx'], self.pos_data.iloc[step]['posy'])
                pygame.draw.circle(canvas, "red", pos, (5))
            
            pygame.display.update()
            step += 1



if __name__ == "__main__":
    pos_data = pd.read_csv('position_data.csv')
    sim = Simulator(pos_data)
    sim.run()