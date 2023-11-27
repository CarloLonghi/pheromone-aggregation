from model import WormSimulator
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt

model = WormSimulator(200, 1000, 50, True)
for i in range(200):
    model.step()