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
    def __init__(self, run, suspect):
        self.headings = ["run", "agentID", "suspect", "victim", "thief", "DNAatCS", "locCS", "statement"]
        self.total_states = []
        self.r = []
        num_agents = 10
        for i in range(0, run):
            model = MoneyModel(N=num_agents, width=20, height=20)
            model.crime_model.set_run(i)
            model.crime_model.set_suspect(suspect)
            for j in range(500):
                model.step()
                if model.reported == True:
                    break
            states, r = model.crime_model.calculate_probabilities()
            self.total_states.append(states)
            self.r.append(r)


    def print_table(self):
        for row in self.total_states:
            for r in row:
                print(r[0], r)




class CrimeModel():
    def __init__(self, model):
        self.model = model
        ### set suspects: thief, and random ###
        # thief
        self.thief = self.model.agent_list[0]
        # random suspect
        self.suspect = self.thief
        self.victim = 0
        self.total_witness_inn = 0
        self.total_witness_guilt = 0
        self.reported_time = 0

    def set_suspect(self, agent_type):
        # default is thief
        print("in set suspect")
        if agent_type == "innocent":
            while self.suspect == self.thief or self.suspect == self.victim:
                self.suspect = random.choice(self.model.agent_list)
        if agent_type == "thief":
            self.suspect = self.thief
        print(self.suspect.thief)

    def set_run(self, run):
        self.run = run

    def set_victim(self, agent):
        self.victim = agent

    def set_reported_time(self, t):
        self.reported_time = t

    def who_is_suspect(self, agent):
        if agent == self.suspect:
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

    def seen_at_crime_scene(self, agent):
        l = []
        for other_agent in self.model.agent_list:
            if other_agent == self.thief:
                x = 1
            else:
                x = 0
            if other_agent == self.suspect:
                y= 1
            else:
                y = 0
            close, alibi = self.check_distance_memory(agent, other_agent)
            l.append([agent.unique_id, other_agent.unique_id, x, y, close, alibi])
        return l

    def check_distance_memory(self, agent, other):
        close = 0
        alibi = 0
        locs = self.check_memory_near_victim(agent, other)
        for (v_pos, o_pos) in locs:
            dist = self.get_distance(v_pos, o_pos)
            if dist < 2:
                close = 1
            if dist > 5:
                alibi = 1
        return close, alibi


    def check_memory_near_victim(self, agent, other_agent):
        locs = []
        for key in agent.visual_buffer.keys():
            if key in range(max(0, self.reported_time - 10), self.reported_time):
                victim_pos = (-1, -1)
                other_agent_pos = (-10, -10)

                val = agent.visual_buffer[key]
                if val != []:
                    if self.victim in list(zip(*val))[0]:
                        for item in val:
                            if item[0] == self.victim:
                                victim_pos = item[1]
                            if item[0] == other_agent:
                                other_agent_pos = item[1]
                    if victim_pos != (-1, -1) and other_agent_pos != (-10, -10):
                        locs.append((victim_pos, other_agent_pos))
        return locs



    def calculate_probabilities(self):
        l = []
        r = []
        self.DNA_evidence = self.calculate_trace()
        for agent in self.model.agent_list:
            id = agent.unique_id
            sus = self.who_is_suspect(agent)
            vic = self.who_is_victim(agent)
            thi = self.who_is_thief(agent)
            dna = self.DNA_at_CS(agent)
            loc = self.agent_at_crime_scene(agent)
            sta = self.agent_loc_statement(agent)
            ret = self.seen_at_crime_scene(agent)
            state = [self.run, id, sus, vic, thi, dna, loc, sta]
            for row in ret:
                r.append(row)
            l.append(state)
        return l, r




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
        memory_tuples = self.position_witness(agent)
        for (pos_suspect, pos_victim, time) in memory_tuples:
            if pos_suspect != (-3, -3) and pos_victim != (-1, -1):
                if self.get_distance(pos_suspect, pos_victim) < 3:
                    return 1
        return 0

    def eyeWitnessAlibi(self, agent):
        memory_tuples = self.position_witness(agent)
        for (pos_suspect, pos_victim, time) in memory_tuples:
            if pos_suspect != (-3, -3) and pos_victim != (-1, -1):
                print("distance", time, pos_suspect, pos_victim, self.get_distance(pos_suspect, pos_victim))
                if self.get_distance(pos_suspect, pos_victim) > 5:
                    print("position of thief FAR AWAY position of victim at ", time, "according to ", agent.color)
                    return 1
        return 0

    def eyeWitnessBase(self, agent):
        count = 0
        memory_tuples = self.anyone_with_victim(agent)
        for (pos_suspect, pos_victim, time) in memory_tuples:
            if pos_suspect != (-3, -3) and pos_victim != (-1, -1):
                if self.get_distance(pos_suspect, pos_victim) < 3:
                    count += 1
        return count

    def eyeWitnessAlibiBase(self, agent):
        count = 0
        memory_tuples = self.anyone_with_victim(agent)
        for (pos_suspect, pos_victim, time) in memory_tuples:
            if pos_suspect != (-3, -3) and pos_victim != (-1, -1):
                print("distance", time, pos_suspect, pos_victim, self.get_distance(pos_suspect, pos_victim))
                if self.get_distance(pos_suspect, pos_victim) > 5:
                    print("position of thief FAR AWAY position of victim at ", time, "according to ", agent.color)
                    count += 1
        return count


    def position_witness(self, agent):
        pos_suspect = (-3, -3)
        pos_victim = (-1, -1)
        memory_tuples = []
        for key in range(max(0, self.reported_time - 10), self.reported_time):  # final recall
            pos_suspect = (-3, -3)
            pos_victim = (-1, -1)
            if key in agent.visual_buffer.keys():
                val = agent.visual_buffer[key]
                if val != []:
                    if (self.suspect in list(zip(*val))[0]):
                        print(f"at time {key}, agent {agent.color, agent.unique_id} saw: ({self.thief.color, self.victim.color})")
                        flag = 0
                        for item in val:
                            if type(item[0]) == MoneyAgent:
                                print(f"\t {item[0].color} at location {item[1]}")
                                if self.suspect == item[0]:
                                    pos_suspect = item[1]
                                    flag = 1
                                if self.victim == item[0]:
                                    pos_victim = item[1]
                                    flag = 1
                        if flag == 1:
                            pos_tuple = (pos_suspect, pos_victim, key)
                            memory_tuples.append(pos_tuple)

        return memory_tuples

    def anyone_with_victim(self, agent):
        pos_anyone = (-3, -3)
        pos_victim = (-1, -1)
        memory_tuples = []
        for key in range(max(0, self.reported_time - 10), self.reported_time):  # final recall
            pos_anyone = (-3, -3)
            pos_victim = (-1, -1)
            if key in agent.visual_buffer.keys():
                val = agent.visual_buffer[key]
                other_agents = []
                if val != []:
                    if (self.victim in list(zip(*val))[0]):
                        for item in val:
                            if type(item[0]) == MoneyAgent:
                                if item[0] != self.thief:
                                    other_agents.append(item[1])
                            if self.victim == item[0]:
                                pos_victim = item[1]
                for agent_pos in other_agents:
                    mem_tuple = (agent_pos, pos_victim, key)
                    memory_tuples.append(mem_tuple)

        return memory_tuples


    def agent_at_crime_scene(self, agent):
        steal_location = self.model.steal_location
        agent_position_steal = agent.position_memory[self.model.steal_time]
        if steal_location == agent_position_steal:
            return 1
        else:
            return 0

    def agent_loc_statement(self, agent):
        if self.agent_at_crime_scene(agent) == 1:
            return 1
        else:
            return 0
        '''
        
        p = random.random()
        if self.agent_at_crime_scene(agent) == 1:
            if agent.thief == True:
                if p <= 0.2:
                    return 1
                else:
                    return 0
            else:
                if p <= 0.7:
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
                    return 1    #agent lies'''



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


