import mesa
import random
import numpy as np
import math
import copy


class DNA(mesa.Agent):
    def __init__(self, unique_id, model, owner):
        # Pass the parameters to the parent class.
        super().__init__(unique_id, model)
        self.model.ag_count += 1
        self.owner = owner
        self.time_dropped = self.model.schedule.time
        self.code = owner.code

    def step(self):
        pass

class MoneyAgent(mesa.Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model, color):
        # Pass the parameters to the parent class.
        super().__init__(unique_id, model)
        self.model.ag_count += 1
        # Create the agent's attribute and set the initial values.
        self.wealth = 1
        self.heading = random.choice(["n", "e", "s", "w", "ne", "nw", "se", "sw"])
        self.color = color
        self.possible_DNA = ["A", "C"]
        self.code = random.choices(self.possible_DNA, k=4)
        self.goal = random.choice(self.model.goal_locations)
        self.goal_counter = 0
        self.thief = 0
        self.target = 0
        self.state = "walking to goal"
        self.visual_buffer = {0:[]}
        self.position_memory = []
        self.DNA_dropped = []
        self.value = random.randint(0, 10)
        print(f"DNA of agent {self.color} is {self.code}")


    def set_thief(self):
        self.thief = True
        self.color = "red"
        self.goal = self.model.thief_location


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

    def calculate_preferred_goal(self):
        new = copy.deepcopy(self.model.goal_locations)
        new.remove(self.pos)
        print("new", new)


        if random.random() <= 0.750: # agemts prefer a goal on the same side of the barrier
            for goal in new:
                if self.pos[1] == goal[1]:
                    print(goal)
                    self.goal = goal
        else:
            print("new", new)
            random.shuffle(new)
            for goal in new:
                if self.pos[1] != goal[1]:
                    print(goal)
                    self.goal = goal


    def move(self, r):
        current_goal = self.goal
        if self.pos == self.goal:
            "reached goal"
            if self.thief != True:
                self.goal_counter += 1
                self.calculate_preferred_goal() #random.choice(self.model.goal_locations)

        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=True, radius=r
        )
        min_dist = min(self.get_distance(current_goal, pos) for pos in possible_steps)
        final_candidates = [
            pos for pos in possible_steps if self.get_distance(current_goal, pos) == min_dist
        ]
        new_position = self.random.choice(final_candidates)
        #print("best", self.pos, new_position, new_position in self.model.accessible_grid_coordinates)
        #print("dif", self.pos[0] - new_position[0], self.pos[1] - new_position[1])


        if new_position not in self.model.accessible_grid_coordinates:
            v0 = new_position[0] - self.pos[0]
            v1 = new_position[1] - self.pos[1]
            #print(self.color, v0, v1)
            new_positions = [(self.pos[0]+v0, self.pos[1]), (self.pos[0], self.pos[1]+v1),
                             (self.pos[0]+v1, self.pos[1]), (self.pos[0], self.pos[1]+v0),
                             (self.pos[0]-v1, self.pos[1]), (self.pos[0], self.pos[1]-v0)]
            for p in new_positions:
                new_position = p
                if new_position in self.model.accessible_grid_coordinates and \
                        new_position not in self.position_memory[-3:]:
                    #print("new position", new_position, self.pos)
                    break

        self.update_heading(self.pos, new_position)
        self.model.grid.move_agent(self, new_position)
        self.position_memory.append(self.pos)


    def halfway_point_calc(self):
        if self.goal != 0:
            p = self.pos
            g = self.goal
            d0 = int((abs(p[0] - g[0])/2))
            d1 = int((abs(p[1] - g[1])/2))
            if p[1] != g[1]:
                return (int(self.model.grid.width/2), int(self.model.grid.height/2))
            else:
                return (d0, d1)


    def update_heading(self, newP, oldP):
        (ax, ay) = oldP
        (bx, by) = newP
        if ax > bx:
            if ay == by:
                self.heading == "e"
            elif ay > by:
                self.heading = "ne"
            else:
                self.heading = "se"
        elif ax == bx:
            if ay == by:
                self.heading == "n"
            elif ay > by:
                self.heading = "n"
            else:
                self.heading = "s"
        else: # "ax < bx"
            if ay == by:
                self.heading == "w"
            elif ay > by:
                self.heading = "nw"
            else:
                self.heading = "sw"




    def vision(self):
        x = self.model.grid.get_neighbors(self.pos, True, radius=10)
        self.visual_buffer[self.model.schedule.time] = []
        flag = 0
        for n in x:
            if type(n) is not MoneyAgent:
                continue
            if self.heading in ["n", "ne", "nw"]:
                if n.pos[0] >= self.pos[0] and n.pos[1] >= self.pos[1]:
                    vision = 1
                else:
                    vision = 0
            elif self.heading == "e":
                if (n.pos[0] >= self.pos[0] and n.pos[1] <= self.pos[1] + (self.pos[1]/2)) or (n.pos[0] >= self.pos[0] and n.pos[1] >= self.pos[1] - (self.pos[1] / 2)):
                    vision = 1
                else:
                    vision = 0
            elif self.heading in ["s", "sw", "se"]:
                if n.pos[0] <= self.pos[0] and n.pos[1] <= self.pos[1]:
                    vision = 1
                else:
                    vision = 0
            elif self.heading == "w":
                if (n.pos[0] <= self.pos[0] and n.pos[1] <= self.pos[1] + (self.pos[1]/2)) or (n.pos[0] <= self.pos[0] and n.pos[1] >= self.pos[1] - (self.pos[1] / 2)):
                    vision = 1
                else:
                    vision = 0
            else:
                pass

            if vision == 1:
                (x0, y0) = self.pos
                (x1, y1) = n.pos
                dx = x0 - x1
                dy = y0 - y1
                D = 2 * dy - dx
                y = y0
                # print(x0, x1)
                for x in range(x0, x1):
                    # print(x, y)
                    if (x, y) not in self.model.accessible_grid_coordinates:
                        vision = 0
                    if D > 0:
                        y = y + 1
                        D = D - 2 * dx
                    if D == D + 2 * dy:
                        break

            if vision == 1:
                '''if n.color == "red":
                    print(self.color, self.heading, "sees ", n.color, " at ", self.model.schedule.time)
                    flag = 1'''
                self.visual_buffer[self.model.schedule.time].append(n)

            '''if flag == 1:
                for agent in self.visual_buffer[self.model.schedule.time]:
                    if type(agent) == MoneyAgent:
                        print(f"At time {self.model.schedule.time}, agent {self.color} saw {agent.color} at loc {agent.pos}")'''


    def targeting(self):

        if self.target == 0:
            for n in self.visual_buffer[self.model.schedule.time]:
                if n.value > 1:
                    # agent is now target
                    self.target = n
                    self.state = "setting target"
                    print("setting target")
        else:
            print(self.target.color)
            if self.target.pos == self.pos:
                print("approached")
                self.state = "stealing"
                self.stealing()
            else:
                self.state = "approaching target"
                self.goal = self.target.pos



    def check_location(self):
        loc = 0
        if 5 < self.pos[0] < 10 and 3 < self.pos[1] < 16:
            # agent is safe in alleyway
            loc = 1
        if loc == 0:
            self.target = 0
            self.goal = self.model.thief_location

    def stealing(self):
        print("stealing")
        if self.target != 0:
            if self.model.schedule.time in self.target.visual_buffer.keys():
                if self in self.target.visual_buffer[self.model.schedule.time]:
                    print(self.target.visual_buffer[self.model.schedule.time])
                    print('seen by victim')
            else:
                print('not seen by victim')

            if random.random() > 0.5:
                print("stealing successful")
                self.target.value = -1
                self.model.crime_model.set_victim_and_random(self.target)
            else:
                print("stealing unsuccessful")

            self.target = 0
            self.goal = random.choice(self.model.goal_locations)

    def monitor(self):
        # once every ~ten steps agent checks if they've been stolen from
        # then quit simulation
        if random.random() < 0.1:
            if self.value == -1:
                print("realise stolen from")
                self.model.crime_model.victim = self
                self.model.crime_model.select_trace()
                self.model.crime_model.select_eye_witness()
                self.model.running = False




    def step(self):
        # The agent's step will go here.
        # For demonstration purposes we will print the agent's unique_id
        self.monitor()
        self.visual_buffer[self.model.schedule.time] = []
        self.vision()
        if self.thief == True:
            self.check_location()
            self.targeting()
            if self.waypoints != []:
                self.move(2)
        else:
            self.move(1)

        if random.random() < 0.1: #1/10 probability for an agent to leave DNA at every step
            dna = DNA(self.model.ag_count, self.model, self)
            self.model.grid.place_agent(dna, (self.pos[0], self.pos[1]))
            self.DNA_dropped.append(dna)




class MoneyModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, N, width, height):
        self.ag_count = 0
        self.num_agents = N
        self.grid = mesa.space.MultiGrid(width, height, False)

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
        if 400 < self.schedule.steps:
            self.crime_model.select_trace()
            self.crime_model.select_eye_witness()
            self.running = False

class Experiment():
    def __init__(self, run):
        prob_correct_match = 0
        prob_math_innocent = 0

        prob_random_trace_match_thief = 0
        prob_random_trace_match_arbit = 0

        prior_random = []
        prior_thief = []
        random_draw_from_thief = 0

        for i in range(0, run):
            model = MoneyModel(N=10, width=20, height=20)
            for j in range(200):
                model.step()
            model.crime_model.select_trace()
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

        print("====================================================================")
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
        '''odds = p/(1-p)
        odds*(1-p) = p
        odds - p*odds = p
        odds = p + p*odds
        odds = p(1+odds)
        p = odds/(1+odds)'''
        print(f"posteriorPROB_trace(random) left by thief == {odds/(1+odds)}")
        print(f"posteriorPROB_trace(random) left by innocent == {1 - (odds/(1+odds))}")
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
        print(self.random.color)
        # victim
        self.victim = 0

    def set_victim_and_random(self, agent):
        self.victim = agent
        while self.random == self.thief or self.random == self.victim:
            self.random = random.choice(self.model.agent_list)

    def select_eye_witness(self):

        # todo - define a victim
        print("suspect (thief) color ", self.thief.color)

        print("suspect (innocent) color ", self.random.color)

        print("victim color ", self.victim.color)
        for agent in self.model.agent_list:
            print(agent.visual_buffer)
            for key in agent.visual_buffer.keys():
                val = agent.visual_buffer[key]
                if self.thief in val or self.random in val:
                    print(f"at time {key}, agent {agent.color} saw:")
                    for item in val:
                        if type(item) == MoneyAgent:
                            print(f"\t {item.color} at location {item.pos}")


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
        self.trace_random = random.choice(collect_DNA_random)
        self.trace_thief = random.choice(collect_DNA_thief_subset)
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
        self.calculate_random_match()
        print()
        print()



    def similarity(self, code1, code2):
        sim_score = 0   # 0 is good, 4 is bad
        for i in range(0, len(code1)):
            if code1[i] != code2[i]:
                sim_score += 1
        print(code1, code2, sim_score)
        return sim_score


    def calculate_random_match(self):
        # for thief
        print(self.random.color)
        print("min is 0, max is 4")
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


