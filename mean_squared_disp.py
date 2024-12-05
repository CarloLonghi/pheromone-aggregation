import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from run import ENV_SIZE, MAX_STEPS, NUM_AGENTS

SPEED = 5

df = pd.read_csv('position_data.csv')
pos_data = df[df['worm'] == True][['posx', 'posy']].values

agent_pos = np.empty((MAX_STEPS, NUM_AGENTS, 2))
for step in range(MAX_STEPS):
    agent_pos[step] = pos_data[step * NUM_AGENTS: (step + 1) * NUM_AGENTS]

for step in range(1, MAX_STEPS):
    pos_x = agent_pos[step, :, 0]
    pos_y = agent_pos[step, :, 1]
    prev_x = agent_pos[step - 1, :, 0]
    prev_y = agent_pos[step - 1, :, 1]
    dx = pos_x - prev_x
    dy = pos_y - prev_y
    agent_pos[step, dx > SPEED, 0] -= ENV_SIZE
    agent_pos[step, dy > SPEED, 1] -= ENV_SIZE
    agent_pos[step, dx < -SPEED, 0] += ENV_SIZE
    agent_pos[step, dy < -SPEED, 1] += ENV_SIZE

disp = np.empty((MAX_STEPS - 1, NUM_AGENTS))
for step in range(1, MAX_STEPS):
    pos = agent_pos[step]
    disp[step - 1, :] = (pos[:,0] - agent_pos[0,:,0]) ** 2 + (pos[:,1] - agent_pos[0,:,1]) ** 2

mean = np.mean(disp, axis=1)
x = np.linspace(0, MAX_STEPS-1, MAX_STEPS-1)
plt.plot(x, mean)

plt.show()