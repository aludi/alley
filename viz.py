from alley import mesa, MoneyModel, MoneyAgent, DNA, Experiment
import random

def agent_portrayal(agent):
    if type(agent) == MoneyAgent:
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 0,
                     "Color": agent.color,
                     "r": 0.5}
    if type(agent) == DNA:
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 0,
                     "Color": agent.owner.color,
                     "r": 0.1}


    return portrayal


Experiment(run=10)
'''grid = mesa.visualization.CanvasGrid(agent_portrayal, 20, 20, 500, 500)
server = mesa.visualization.ModularServer(MoneyModel,
                       [grid],
                       "Money Model",
                       {"N":8, "width":20, "height":20})
server.port = 8521 # The default
server.launch()'''