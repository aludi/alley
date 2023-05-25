from alley import mesa, MoneyModel, Experiment
from agents import  MoneyAgent, DNA
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

data_list = [["agent type", "LR DNA", "LR Witness", "LR Alibi", "LR Statement"]]
for i in range(0, 6):
    e = Experiment(run=50)
    data_list.append(e.thief_LR)
    data_list.append(e.other_LR)

for row in data_list:
    if "agent type" not in row:
        print(f"{row[0]} \t\t {round(row[1],2)} \t\t {round(row[2],2)} \t\t {round(row[3],2)} \t\t {round(row[4], 2)}")
    else:
        print(row)


'''grid = mesa.visualization.CanvasGrid(agent_portrayal, 20, 20, 500, 500)
server = mesa.visualization.ModularServer(MoneyModel,
                       [grid],
                       "Money Model",
                       {"N":8, "width":20, "height":20})
server.port = 8521 # The default
server.launch()'''