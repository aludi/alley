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
        self.DNA_drop_threshold = 0.01
        self.value = random.randint(0, 10)

        #print(f"DNA of agent {self.color} is {self.code}")


    def set_thief(self):
        self.thief = True
        self.color = "red"
        self.goal = self.model.thief_location
        self.DNA_drop_threshold = 0.1


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
        #print("new", new)


        if random.random() <= 0.750: # agemts prefer a goal on the same side of the barrier
            for goal in new:
                if self.pos[1] == goal[1]:
                    #print(goal)
                    self.goal = goal
        else:
            #print("new", new)
            random.shuffle(new)
            for goal in new:
                if self.pos[1] != goal[1]:
                    #print(goal)
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
        self.position_memory.append(self.pos)
        self.model.grid.move_agent(self, new_position)


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
                self.visual_buffer[self.model.schedule.time].append((n, n.pos))
                #print(self.visual_buffer)

            '''if flag == 1:
                for agent in self.visual_buffer[self.model.schedule.time]:
                    if type(agent) == MoneyAgent:
                        print(f"At time {self.model.schedule.time}, agent {self.color} saw {agent.color} at loc {agent.pos}")'''


    def targeting(self):

        if self.target == 0:
            for (n, npos) in self.visual_buffer[self.model.schedule.time]:
                if n.value > 1:
                    # agent is now target
                    self.target = n
                    self.state = "setting target"
                    #print("setting target")
        else:
            #print(self.target.color)
            if self.target.pos == self.pos:
                #print("approached")
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
                if (self, self.pos) in self.target.visual_buffer[self.model.schedule.time]:
                    print(self.target.visual_buffer[self.model.schedule.time])
                    print('seen by victim')
            else:
                print('not seen by victim')

            if random.random() > 0.5:
                print("stealing successful at t =", self.model.schedule.time)
                self.target.value = -1
                self.model.steal_time = self.model.schedule.time
                self.model.steal_location = self.pos
                self.model.crime_model.set_victim(self.target)
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
                self.model.crime_model.set_reported_time(self.model.schedule.steps)
                self.model.running = False
                self.model.reported = True
                '''self.model.crime_model.select_trace()
                self.model.crime_model.select_eye_witness()
                self.model.running = False'''




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

        if random.random() < self.DNA_drop_threshold: #1/10 probability for an agent to leave DNA at every step
            dna = DNA(self.model.ag_count, self.model, self)
            self.model.grid.place_agent(dna, (self.pos[0], self.pos[1]))
            self.DNA_dropped.append(dna)
