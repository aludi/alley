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
        self.steal_location = 0

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

        personal_loc_guilt = []
        personal_away_guilt= []
        personal_loc_random= []
        personal_away_random= []
        personal_loc_base= []
        personal_away_base= []

        thief_present_crime_scene = []
        thief_away_crime_scene = []
        other_present_crime_scene = []
        other_away_crime_scene = []

        num_agents = 10

        for i in range(0, run):
            model = MoneyModel(N=num_agents, width=20, height=20)
            for j in range(500):
                model.step()
                if model.reported == True:
                    break
            model.crime_model.calculate_probabilities()
            exit()
            model.crime_model.select_trace()
            model.crime_model.select_eye_witness()
            model.crime_model.calculate_alibi()
            model.crime_model.personal_testimony()

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

            p_crime_scene_thief = model.crime_model.thief_present_crime_scene / (
                        model.crime_model.thief_present_crime_scene + model.crime_model.thief_away_crime_scene)
            p_crime_scene_other = model.crime_model.other_present_crime_scene / (
                        model.crime_model.other_present_crime_scene + model.crime_model.other_away_crime_scene)

            p_away_thief = model.crime_model.thief_away_crime_scene / (
                    model.crime_model.thief_present_crime_scene + model.crime_model.thief_away_crime_scene)
            p_away_other = model.crime_model.other_away_crime_scene / (
                    model.crime_model.other_present_crime_scene + model.crime_model.other_away_crime_scene)

            # probabilities for how many times the agent is away or not
            print(p_crime_scene_thief, p_crime_scene_other)
            print(p_away_thief, p_away_other)
            thief_present_crime_scene.append(p_crime_scene_thief)
            thief_away_crime_scene.append(p_away_thief)
            other_present_crime_scene.append(p_crime_scene_other)
            other_away_crime_scene.append(p_away_other)

            try:
                personal_loc_guilt.append(model.crime_model.trueLoc_report_thief / p_crime_scene_thief)
            except ZeroDivisionError:
                personal_loc_guilt.append(0)

            try:
                personal_away_guilt.append(model.crime_model.trueAway_report_thief/p_away_thief)
            except ZeroDivisionError:
                personal_away_guilt.append(0)

            try:
                personal_loc_base.append(model.crime_model.trueLoc_report_innocent / p_crime_scene_other)
                personal_loc_random.append(model.crime_model.trueLoc_report_target/p_crime_scene_other)
            except ZeroDivisionError:
                personal_loc_base.append(0)
                personal_loc_random.append(0)
            try:
                personal_away_random.append(model.crime_model.trueAway_report_target/p_away_other)
                personal_away_base.append(model.crime_model.trueAway_report_innocent/p_away_other)
            except ZeroDivisionError:
                personal_away_random.append(0)
                personal_away_base.append(0)

            #print(model.crime_model.thief_present_crime_scene)
            #print(model.crime_model.thief_away_crime_scene)



            ''''p_stat_given_cs_thief = model.crime_model.trueLoc_report_thief/p_crime_scene_thief
            p_stat_given_cs_other = model.crime_model.trueLoc_report_innocent/p_crime_scene_other

            p_stat_given_away_thief = model.crime_model.trueAway_report_thief / p_away_thief
            p_stat_given_away_other = model.crime_model.trueAway_report_innocentr / p_away_other

            print(p_stat_given_cs_thief, p_stat_given_cs_other)
            print(p_stat_given_away_thief, p_stat_given_away_other)'''

            #thief_present_crime_scene.append(thief_present_crime_scene)
            #self.thief_away_crime_scene = 0
            #self.other_present_crime_scene = 0
            #self.other_away_crime_scene = 0


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

        self.thief_LR = ["thief"]
        self.other_LR = ["arbit"]

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

        self.thief_LR.append(prob_correct_match/prob_math_innocent)
        self.other_LR.append(prob_random_trace_match_thief/prob_random_trace_match_arbit)

        print("======================    WITNESSES     ============================")
        #print(witness_guilt)
        #print(witness_in)
        #print(witness_base_rate)
        av_guilt = sum(witness_guilt)/len(witness_guilt)
        av_in = sum(witness_in)/len(witness_in)
        av_base = sum(witness_base_rate)/len(witness_base_rate)

        #print(f"average number of witness guilt {av_guilt}")
        #print(f"average number of witness inn {av_in}")
        #print(f"average number of witness base rate {av_base}")
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

        self.thief_LR.append(av_guilt/av_base)
        self.other_LR.append(av_in/av_base)


        print("======================      ALIBI       ============================")
        #print(alibi_guilt)
        #print(alibi_in)
        #print(alibi_base_rate)
        av_guilt = sum(alibi_guilt) / len(alibi_guilt)
        av_in = sum(alibi_in) / len(alibi_in)
        av_base = sum(alibi_base_rate) / len(alibi_base_rate)
        #print(av_guilt)
        #print(av_in)
        #print(av_base)

        #print(f"average number of witness guilt {av_guilt}")
        #print(f"average number of witness inn {av_in}")
        #print(f"average number of witness base rate {av_base}")
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


        self.thief_LR.append(av_guilt/av_base)
        self.other_LR.append(av_in/av_base)



        print("======================     PERSONAL     ============================")

        av_loc_guilt = sum(personal_loc_guilt)/len(personal_loc_guilt)
        av_away_guilt = sum(personal_away_guilt)/len(personal_away_guilt)

        av_loc_random = sum(personal_loc_random)/len(personal_loc_random)
        av_away_random = sum(personal_away_random)/len(personal_away_random)

        av_loc_base = sum(personal_loc_base)/len(personal_loc_base)
        av_away_base = sum(personal_away_base)/len(personal_away_base)

        Prior_thief_cs = sum(thief_present_crime_scene)/len(thief_present_crime_scene)
        Prior_thief_away = sum(thief_away_crime_scene)/len(thief_away_crime_scene)
        Prior_other_cs = sum(other_present_crime_scene)/len(other_present_crime_scene)
        Prior_other_away = sum(other_away_crime_scene)/len(other_away_crime_scene)
        print(Prior_thief_cs, Prior_thief_away)
        print(Prior_other_cs, Prior_other_away)

        print(f"LR_personal(thief) == {av_loc_guilt / av_away_guilt}")
        print(f"posteriorOdds_personal(thief) == {(Prior_thief_cs / (Prior_thief_away)) * (av_loc_guilt / av_away_guilt)}")
        odds2 = (Prior_thief_cs / (Prior_thief_away)) * (av_loc_guilt / av_away_guilt)
        print(f"posteriorPROB_personal(thief) at cs == {odds2 / (1 + odds2)}")
        print(f"posteriorPROB_personal(thief) at niet cs == {1 - (odds2 / (1 + odds2))}")

        print("====================================================================")

        print(f"LR_personal(innocent) == {av_loc_random / av_away_random}")
        print(f"posteriorOdds_personal(innocent) == {(Prior_other_cs / (Prior_other_away)) * (av_loc_random / av_away_random)}")
        odds2 = (Prior_other_cs / (Prior_other_away)) * (av_loc_random /av_away_random)
        print(f"posteriorPROB_personal(innocent) at cs == {odds2 / (1 + odds2)}")
        print(f"posteriorPROB_personal(innocent) at niet cs == {1 - (odds2 / (1 + odds2))}")


        self.thief_LR.append(av_guilt/av_base)
        self.other_LR.append(av_in/av_base)

        print("====================================================================")
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
        self.suspect = self.thief
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

    def who_is_suspect(self, agent):
        if agent == self.random or agent == self.thief:
            return 1
        else:
            return 0
    def who_is_victim(self, agent):
        if agent == self.victim:
            return 1
        else:
            return 0

    def who_is_thief(self, agent):
        if agent == self.thief:
            return 1
        else:
            return 0


    def calculate_probabilities(self):
        headings = ["agentID", "suspect", "victim", "thief", "DNAatCS", "locCS", "statement", "seenSuspectCS", "seenSuspectAlibi", ]
        l = [headings]
        self.DNA_evidence = self.calculate_trace()
        for agent in self.model.agent_list:
            id = agent.unique_id
            sus = self.who_is_suspect(agent)
            vic = self.who_is_victim(agent)
            thi = self.who_is_victim(agent)
            dna = self.DNA_at_CS(agent)
            loc = self.agent_at_crime_scene(agent)
            sta = self.agent_loc_statement(agent)
            scs = self.eyeWitness(agent)  # the agent saw the victim and the thief at the same position in the given time range
            sal = self.eyeWitnessAlibi(agent)
            state = [id, sus, vic, thi, dna, loc, sta, scs, sal]
            l.append(state)
        print(l)


    def calculate_trace(self):
        collect_DNA_other = []
        collect_DNA_thief = []
        for i in range(5, 10):
            for j in range(3, 16):
                for agent in self.model.grid[i][j]:
                    if type(agent) == DNA:
                        if agent.owner.thief == True:
                            collect_DNA_thief.append(agent)
                        else:
                            collect_DNA_other.append(agent)
        return [collect_DNA_thief, collect_DNA_other]

    def DNA_at_CS(self, agent):
        evidence_thief = self.DNA_evidence[0]
        evidence_other = self.DNA_evidence[1]
        total_evidence = evidence_other + evidence_thief
        if total_evidence == []:
            return 0

        for trace in total_evidence:
            if trace.owner == agent:
                return 1
        return 0

    def eyeWitness(self, agent):
        pos_suspect, pos_victim = self.position_witness(agent)
        if pos_suspect == pos_victim:
            return 1
        else:
            return 0

    def eyeWitnessAlibi(self, agent):
        pos_suspect, pos_victim = self.position_witness(agent)
        if pos_suspect != (-3, -3) and pos_victim != (-1, -1):
            if self.get_distance(pos_suspect, pos_victim) > 2:
                #print("position of thief FAR AWAY position of victim at ", key, "according to ", agent.color)
                return 1

        return 0


    def position_witness(self, agent):
        for key in range(max(0, self.reported_time - 10), self.reported_time):  # final recall
            pos_suspect = (-3, -3)
            pos_victim = (-1, -1)
            if key in agent.visual_buffer.keys():
                val = agent.visual_buffer[key]
                if val != []:
                    if (self.suspect in list(zip(*val))[0]):
                        print(f"at time {key}, agent {agent.color} saw:")
                        for item in val:
                            if type(item[0]) == MoneyAgent:
                                print(f"\t {item[0].color} at location {item[1]}")
                                if self.suspect == item[0]:
                                    pos_suspect = item[1]
                                if self.victim == item[0]:
                                    pos_victim = item[1]
            return pos_suspect, pos_victim


    def agent_at_crime_scene(self, agent):
        steal_location = self.model.steal_location
        agent_position_steal = agent.position_memory[self.model.steal_time]
        if steal_location == agent_position_steal:
            return 1
        else:
            return 0

    def agent_loc_statement(self, agent):
        p = random.random()
        if self.agent_at_crime_scene(agent) == 1:
            if agent.thief == True:
                if p <= 0.2:
                    return 1
                else:
                    return 0
            else:
                if p <= 0.8:
                    return 1
                else:
                    return 0
        else:   # agent was not at crime scene
            if agent.thief == True:
                if p <= 0.99:
                    return 0    # agent tells you that they were not at crime scene (true)
                else:
                    return 1    #agent lies
            else:
                if p <= 1:
                    return 0
                else:
                    return 1    #agent lies



    def personal_testimony(self):
        steal_location = self.model.steal_location
        self.trueLoc_report_thief = 0
        self.trueLoc_report_innocent = 0
        self.trueAway_report_thief = 0
        self.trueAway_report_innocent = 0
        self.trueLoc_report_target = 0
        self.trueAway_report_target = 0

        self.thief_present_crime_scene = 0
        self.thief_away_crime_scene = 0
        self.other_present_crime_scene = 0
        self.other_away_crime_scene = 0
        for agent in self.model.agent_list:
            # ask agents: "where were you at the time of the murder
            # agents might lie
            agent_position_steal = agent.position_memory[self.model.steal_time]
            p = random.random()

            if steal_location == agent_position_steal: # agent was at steal location
                if agent.thief == True:
                    self.thief_present_crime_scene +=1

                    if p <= 0.2:
                        self.trueLoc_report_thief += 1
                else:
                    self.other_present_crime_scene += 1
                    if p <= 0.8:
                        self.trueLoc_report_innocent += 1
                        if agent == self.random:
                            self.trueLoc_report_target += 1

            else:
                if agent.thief == True:
                    self.thief_away_crime_scene += 1
                    if p <= 0.99:
                        self.trueAway_report_thief += 1
                else:
                    self.other_away_crime_scene += 1
                    if p <= 1:
                        self.trueAway_report_innocent += 1
                        if agent == self.random:
                            self.trueAway_report_target += 1

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


