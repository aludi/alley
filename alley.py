import mesa
import random
import numpy as np
import math
import copy
from agents import MoneyAgent, DNA



class MoneyModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, N, width, height):
        self.reported = False
        self.ag_count = 0
        self.num_agents = N
        self.grid = mesa.space.MultiGrid(width, height, False)
        self.steal_time = -1

        grid_list = []
        self.accessible_grid_coordinates = []
        for i in range(0, self.grid.width):
            for j in range(0, self.grid.height):
                place = (i, j)
                val = self.func(i, j)
                if val == 1:
                    self.accessible_grid_coordinates.append(place)

        self.goal_locations = [(0, 0), (self.grid.width -1, 0), (self.grid.width-1, self.grid.height-1), (0, self.grid.height-1)]
        self.thief_location = (random.randint(5, 9), random.randint(4, 15))

        self.schedule = mesa.time.RandomActivation(self)
        self.agent_list = []

        colors = ["green", "blue", "gold", "purple", "orange", "lime", "pink"]
        # Create agents
        for i in range(self.num_agents):
            a = MoneyAgent(self.ag_count, self, colors[i%len(colors)])
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(1)
            y = self.random.randrange(1)
            self.grid.place_agent(a, (x, y))
            a.halfway_point = a.halfway_point_calc()
            a.waypoints=[a.halfway_point, a.goal]
            a.thief = False
            #self.schedule.step()
            self.agent_list.append(a)

        self.agent_list[0].set_thief()
        self.crime_model = CrimeModel(self)



    def func(self, i, j):
        if ( 0 <= i < 5 and 3 < j < 16):
            return 0
        if ( 10 <= i and 3 < j < 16):
            return 0
        else:
            return 1

    def collect_probabilities(self):

        # indexing the whole space
        #for i in range(0, self.grid.width):
        #    for j in range(0, self.grid.height):
        #        print(self.grid[i][j])

        # finding DNA in alley
        Pr = {"find DNA in alley | suspect_Guilty":0,
              "find DNA in alley | suspect_Innocent":0,
              }
        for i in range(5, 10):
            for j in range(3, 16):
                for agent in self.grid[i][j]:
                    if type(agent) == DNA:
                        if agent.owner.thief == True:
                            Pr["find DNA in alley | suspect_Guilty"] += 1
                        else:
                            Pr["find DNA in alley | suspect_Innocent"] += 1
        print(Pr)


    def step(self):
        self.schedule.step()
        #self.collect_probabilities()
        #print("steps", self.schedule.steps)
        '''if 500 < self.schedule.steps:
            if self.crime_model.victim != 0:
                self.crime_model.select_trace()
                self.crime_model.select_eye_witness()
            self.running = False'''

class Experiment():
    '''odds = p/(1-p)
    odds*(1-p) = p
    odds - p*odds = p
    odds = p + p*odds
    odds = p(1+odds)
    p = odds/(1+odds)'''
    def __init__(self, run):
        prob_correct_match = 0
        prob_math_innocent = 0

        prob_random_trace_match_thief = 0
        prob_random_trace_match_arbit = 0

        prior_random = []
        prior_thief = []
        random_draw_from_thief = 0

        witness_guilt = []
        witness_in = []
        witness_base_rate = []

        alibi_guilt = []
        alibi_in = []
        alibi_base_rate = []

        num_agents = 10

        for i in range(0, run):
            model = MoneyModel(N=num_agents, width=20, height=20)
            for j in range(500):
                model.step()
                if model.reported == True:
                    break
            model.crime_model.select_trace()
            model.crime_model.select_eye_witness()
            model.crime_model.calculate_alibi()

            if model.crime_model.sim_ran == 1:
                prob_math_innocent+= 1
            if model.crime_model.sim_thief == 1:
                prob_correct_match += 1
            if model.crime_model.sim_ran_ran == 1:
                prob_random_trace_match_arbit+= 1
            if model.crime_model.sim_thief_ran == 1:
                prob_random_trace_match_thief += 1
            if model.crime_model.random_draw.owner.thief:
                random_draw_from_thief += 1

            #print(model.crime_model.total_witness_guilt)
            #print(model.crime_model.total_witness_inn)

            witness_guilt.append(model.crime_model.total_witness_guilt)
            witness_in.append(model.crime_model.total_witness_inn)
            witness_base_rate.append(model.crime_model.base_rate_surrounding)

            alibi_guilt.append(model.crime_model.alibi_guilt)
            alibi_in.append(model.crime_model.alibi_inn)
            alibi_base_rate.append(model.crime_model.base_rate_alibi)

            prior_random.append(model.crime_model.prior_random)
            prior_thief.append(model.crime_model.prior_thief)


        #print(prob_correct_match)
        #print(prob_math_innocent)

        PR_random = sum(prior_random)/len(prior_random)
        PR_thief = sum(prior_thief)/len(prior_thief)
        if prob_math_innocent == 0:
            prob_math_innocent = 0.000001
        if prob_random_trace_match_arbit == 0:
            prob_random_trace_match_arbit = 0.00001

        print("======================    DNA TRACE    ============================")
        print(f"LR_trace(thief) == {prob_correct_match/prob_math_innocent}")
        print(f"posteriorODDS_trace(thief) == {run*(prob_correct_match/prob_math_innocent)}")
        odds1 = (prob_correct_match/prob_math_innocent)
        print(f"posteriorPROB_trace(thief) left by thief == {odds1 / (1 + odds1)}")
        print(f"posteriorPROB_trace(thief) left by innocent == {1 - (odds1 / (1 + odds1))}")
        print("====================================================================")
        print(f"Random trace from thief in {random_draw_from_thief} out of {run} runs")
        print(f"LR_trace(random) == {prob_random_trace_match_thief/prob_random_trace_match_arbit}")
        print(f"posteriorODDS_trace(random) == {(PR_thief/PR_random)*(prob_random_trace_match_thief/prob_random_trace_match_arbit)}")
        odds = (PR_thief / PR_random) * (prob_random_trace_match_thief / prob_random_trace_match_arbit)

        print(f"posteriorPROB_trace(random) left by thief == {odds/(1+odds)}")
        print(f"posteriorPROB_trace(random) left by innocent == {1 - (odds/(1+odds))}")
        print("====================================================================")

        print("======================    WITNESSES     ============================")
        print(witness_guilt)
        print(witness_in)
        print(witness_base_rate)
        av_guilt = sum(witness_guilt)/len(witness_guilt)
        av_in = sum(witness_in)/len(witness_in)
        av_base = sum(witness_base_rate)/len(witness_base_rate)

        print(f"average number of witness guilt {av_guilt}")
        print(f"average number of witness inn {av_in}")
        print(f"average number of witness base rate {av_base}")
        print("====================================================================")

        print(f"LR_witness(thief) == {av_guilt/av_base}")
        print(f"posteriorOdds_witness(thief) == {(1/(num_agents-1))*(av_guilt/av_base)}")
        odds2 = (1/(num_agents-1))*(av_guilt/av_base)
        print(f"posteriorPROB_witness(thief) by thief == {odds2 / (1 + odds2)}")
        print(f"posteriorPROB_witness(thief) by innocent == {1 - (odds2 / (1 + odds2))}")

        print("====================================================================")

        print(f"LR_witness(innocent) == {av_in/av_base}")
        print(f"posteriorOdds_witness(innocent) == {(1/(num_agents-1))*(av_in/av_base)}")
        odds3 = (1/(num_agents-1))*(av_in/av_base)
        print(f"posteriorPROB_witness(innocent) left by thief == {odds3 / (1 + odds3)}")
        print(f"posteriorPROB_witness(innocent) left by innocent == {1 - (odds3 / (1 + odds3))}")

        print("======================      ALIBI       ============================")
        print(alibi_guilt)
        print(alibi_in)
        print(alibi_base_rate)
        av_guilt = sum(alibi_guilt) / len(alibi_guilt)
        av_in = sum(alibi_in) / len(alibi_in)
        av_base = sum(alibi_base_rate) / len(alibi_base_rate)
        print(av_guilt)
        print(av_in)
        print(av_base)

        print(f"average number of witness guilt {av_guilt}")
        print(f"average number of witness inn {av_in}")
        print(f"average number of witness base rate {av_base}")
        print("====================================================================")

        print(f"LR_witness(thief) == {av_guilt / av_base}")
        print(f"posteriorOdds_witness(thief) == {(1 / (num_agents - 1)) * (av_guilt / av_base)}")
        odds2 = (1 / (num_agents - 1)) * (av_guilt / av_base)
        print(f"posteriorPROB_witness(thief) by thief == {odds2 / (1 + odds2)}")
        print(f"posteriorPROB_witness(thief) by innocent == {1 - (odds2 / (1 + odds2))}")

        print("====================================================================")

        print(f"LR_witness(innocent) == {av_in / av_base}")
        print(f"posteriorOdds_witness(innocent) == {(1 / (num_agents - 1)) * (av_in / av_base)}")
        odds3 = (1 / (num_agents - 1)) * (av_in / av_base)
        print(f"posteriorPROB_witness(innocent) left by thief == {odds3 / (1 + odds3)}")
        print(f"posteriorPROB_witness(innocent) left by innocent == {1 - (odds3 / (1 + odds3))}")

        print("====================================================================")



class CrimeModel():
    def __init__(self, model):
        self.model = model
        ### set suspects: thief, and random ###
        # thief
        self.thief = self.model.agent_list[0]
        # random suspect
        self.random=self.thief
        while self.random == self.thief:
            self.random = random.choice(self.model.agent_list)
        #print(self.random.color)
        # victim
        self.victim = 0
        self.total_witness_inn = 0
        self.total_witness_guilt = 0
        self.reported_time = 0

    def set_victim_and_random(self, agent):
        self.victim = agent
        while self.random == self.thief or self.random == self.victim:
            self.random = random.choice(self.model.agent_list)

    def set_reported_time(self, t):
        self.reported_time = t

    def personal_testimony(self):
        for agent in self.model.agent_list:
            # ask agents: "where were you at the time




    def select_eye_witness(self):

        #print("suspect (thief) color ", self.thief.color)

        #print("suspect (innocent) color ", self.random.color)

        #print("victim color ", self.victim.color)

        self.total_witness_inn = 0
        self.total_witness_guilt = 0
        self.base_rate_surrounding = 0

        for agent in self.model.agent_list:
            #print(agent.visual_buffer)
            for key in range(max(0, self.reported_time-10), self.reported_time):  # final recall
                pos_thief = (-3, -3)
                pos_victim = (-1, -1)
                pos_random = (-2, -2)
                if key in agent.visual_buffer.keys():
                    val = agent.visual_buffer[key]
                    if val != []:
                        #print(val)
                        #print(list(zip(*val)))
                        #print(self.thief in list(zip(*val))[0])
                        if (self.thief in list(zip(*val))[0] or self.random in list(zip(*val))[0]) and self.victim in list(zip(*val))[0]:
                            #print(f"at time {key}, agent {agent.color} saw:")
                            for item in val:
                                if type(item[0]) == MoneyAgent:
                                    #print(f"\t {item[0].color} at location {item[1]}")
                                    if self.thief == item[0]:
                                        pos_thief = item[1]
                                    if self.victim == item[0]:
                                        pos_victim = item[1]
                                    if self.random == item[0]:
                                        pos_random = item[1]
                                    if item[0] not in [self.thief, self.victim]:
                                        if item[1] == pos_victim:
                                            # base rate per agent
                                            self.base_rate_surrounding += 1

                # can we find statistical trends in this?
                # sometimes there is consensus
                if pos_thief == pos_victim:
                    print("position of thief == position of victim at ", key, "according to ", agent.color)
                    self.total_witness_guilt += 1

                if pos_random == pos_victim:
                    print("position of innocent == position of victim", key, "according to ", agent.color)
                    self.total_witness_inn += 1



        print("wg", self.total_witness_guilt)
        print("wi", self.total_witness_inn)
        print("br", self.base_rate_surrounding)

        if self.total_witness_guilt > 0:
            self.total_witness_guilt = 1
        if self.total_witness_inn > 0:
            self.total_witness_inn = 1
        if self.base_rate_surrounding > 0:
            self.base_rate_surrounding = 1

    def calculate_alibi(self):
        self.alibi_guilt = 0
        self.alibi_inn = 0
        self.base_rate_alibi = 0
        for agent in self.model.agent_list:
            for key in range(max(0, self.reported_time-10), self.reported_time):  # final recall
                pos_thief = (-3, -3)
                pos_victim = (-1, -1)
                pos_random = (-2, -2)
                if key in agent.visual_buffer.keys():
                    val = agent.visual_buffer[key]
                    if val != []:
                        if (self.thief in list(zip(*val))[0] or self.random in list(zip(*val))[0]):
                            print(f"at time {key}, agent {agent.color} saw:")
                            for item in val:
                                if type(item[0]) == MoneyAgent:
                                    print(f"\t {item[0].color} at location {item[1]}")
                                    if self.thief == item[0]:
                                        pos_thief = item[1]
                                    if self.victim == item[0]:
                                        pos_victim = item[1]
                                    if self.random == item[0]:
                                        pos_random = item[1]
                                    if item[0] not in [self.thief, self.victim]:
                                        if self.get_distance(item[1], pos_victim) > 2:
                                            # base rate per agent
                                            self.base_rate_alibi+= 1

                # can we find statistical trends in this?
                # sometimes there is consensus
                if pos_thief != (-3, -3) and pos_victim != (-1, -1) and pos_random != (-2, -2):
                    if self.get_distance(pos_thief, pos_victim) > 2:
                        print("position of thief FAR AWAY position of victim at ", key, "according to ", agent.color)
                        self.alibi_guilt += 1

                    if self.get_distance(pos_random, pos_victim)> 2:
                        print("position of innocent FAR AWAY position of victim", key, "according to ", agent.color)
                        self.alibi_inn += 1

        print(self.alibi_guilt, self.alibi_inn, self.base_rate_alibi)
        if self.alibi_guilt > 0:
            self.alibi_guilt = 1
        if self.alibi_inn > 0:
            self.alibi_inn = 1
        if self.base_rate_alibi > 0:
            self.base_rate_alibi = 1


    def get_distance(self, pos_1, pos_2):
        """Get the distance between two points
        Args:
            pos_1, pos_2: Coordinate tuples for both points.
        """
        x1, y1 = pos_1
        x2, y2 = pos_2
        dx = x1 - x2
        dy = y1 - y2
        return math.sqrt(dx ** 2 + dy ** 2)



    def select_trace(self):
        collect_DNA_random = []
        collect_DNA_thief_subset = []
        for i in range(5, 10):
            for j in range(3, 16):
                for agent in self.model.grid[i][j]:
                    if type(agent) == DNA:
                        if agent.owner.thief == True:
                            collect_DNA_thief_subset.append(agent)
                        else:
                            collect_DNA_random.append(agent)
        if collect_DNA_random != []:
            self.trace_random = random.choice(collect_DNA_random)
        else:
            self.trace_random = 0

        if collect_DNA_thief_subset != []:
            self.trace_thief = random.choice(collect_DNA_thief_subset)
        else:
            self.trace_thief = 0

        if len(collect_DNA_thief_subset) + len(collect_DNA_random) == 0:
            self.prior_random = 0
            self.prior_thief = 0
            self.collect = 0
            self.random_draw = 0
        else:
            self.prior_random = len(collect_DNA_random)/(len(collect_DNA_thief_subset)+len(collect_DNA_random))
            self.prior_thief = len(collect_DNA_thief_subset)/(len(collect_DNA_thief_subset)+len(collect_DNA_random))
            self.collect = collect_DNA_thief_subset + collect_DNA_random
            self.random_draw = random.choice(self.collect)
            print()
            print()
            print(self.prior_random)
            print(self.prior_thief)
            print(self.random_draw.owner.color)
            print()
            print()
        if self.trace_random != 0 and self.trace_thief != 0:
            #print(self.random, self.thief)
            self.calculate_random_match()
        else:
            self.sim_ran = 0
            self.sim_thief = 0
            self.sim_ran_ran = 0
            self.sim_thief_ran = 0
        print()
        print()



    def similarity(self, code1, code2):
        sim_score = 0   # 0 is good, 4 is bad
        for i in range(0, len(code1)):
            if code1[i] != code2[i]:
                sim_score += 1
        #print(code1, code2, sim_score)
        return sim_score


    def calculate_random_match(self):
        # for thief
        print(self.random.color)
        #print("min is 0, max is 4")
        self.sim_ran = 0
        self.sim_thief = 0
        self.sim_ran_ran = 0
        self.sim_thief_ran = 0
        if self.similarity(self.thief.code, self.trace_thief.code) < 1:
            print("we found a DNA match (thief-thief)")
            self.sim_thief = 1
        # for random
        if self.similarity(self.random.code, self.trace_thief.code) < 1:
            print("we found a DNA match (innocent-thief)")
            self.sim_ran = 1

        if self.similarity(self.thief.code, self.random_draw.code) < 1:
            print("we found a DNA match (thief-random)")
            self.sim_thief_ran = 1
        # for random
        if self.similarity(self.random.code, self.random_draw.code) < 1:
            print("we found a DNA match (innocent-random)")
            self.sim_ran_ran = 1


