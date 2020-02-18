"""
Created on Sat 15 Feb 2020 14:12:49 UTC

Custom Environement for building TrafficLight RL Agents using SUMO

#@Author: Sehail Fillali
"""

from pprint import pprint as pp
import os
import sys
import numpy as np
import gym
from gym import spaces
from helper import state_to_array
from sumoWrapper import Env_TLC
from sumoWrapper import getReward

# Import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


class durationEnv(gym.Env):
    """ Custom Environement following gym specs"""

    def __init__(self,
                 # agent_type='JAgent',
                 nbr_actions=8,
                 *args, **kargs):

        super(durationEnv, self).__init__()

        # Action space
        # a descrete set of actions to be passed to the traci module for
        # execution

        self.action_field = spaces.Discrete(8)
        self.action_space = [7, 15, 25, 35, 50, 70, 90, 120]

        # Example action
        # pp( f'action {i}: {actions[self.action_field.sample()]}')

        # Observational space
        # This is supposed to be an instatiation of a sumo simulation, along
        # with the handle of a valid traci active connection

        # Observational state constituents for a junction of 8 lanes (right on
        # red is not taken into account in the Traffic Light logic)
        # [a, b, c, d, e, f, g, h]:
        tlID = TL.getIDList()[0]
        self.trfcLgt_simulation = Env_TLC(programID='0', tlsID=tlID)
        self.observation_space = np.zeros(35,8)
        print(self.observation_space)

        # 'IBOccupancy',
        # 'IBVolume',
        # 'IBMeanSpeed',
        # 'IBQueuSize',
        # 'IBWaitingTime',
        # 'OBOccupancy',
        # 'OBVolume',
        # 'OBMeanSpeed',
        # 'OBQueuSize',
        # 'OBWaitingTime'
        # 'CurrentPhase'

        # Full program for the traffic light: {'r': 0, 'y': 1, 'g' : 2, 'G': 3}
        program = ['rrGGrrGG', 'GGrrGGrr'] * 12
        self.current_tlProgram = np.array([state_to_array(state)
                                           for state in program])
        observation = np.vstack((self.edge_occupancy,
                                 self.OB_lane_occupancy,
                                 self.queue_sizes,
                                 self.mean_speed,
                                 self.current_tlProgram))
        pp('Program Environement instatiated')

    def step(self, action):

        # TODO Use the selected action to complete a step in environement,
        # while carefully using the corresponding RL scope (horizon necessary
        # for calculating the reward)

        # the step uses the traci handle to excecute the action

        reward, observation = simulate_action(action, time_horizon)
        '''
        def getReward(action):
            update duration for program index n + 1

            for i in range(self.action_space[action]):
                trc.simulation.step()
                aggregate outbound flow of cars and total waiting time
                for reward calculation

            reward = (total flow of cars - sigmoid(total_waiting_time)) / action

            self.trfcLgt_simulation.updateLastState()
            observation = self.trfcLgt_simulation.getStateArray()
            return reward, observation

        done = trc.currentTimeIndex == time_horizon
        info = 1  # TODO
        '''

        # return observation_, reward, done, info
        pass

    def reset(self):

        # TODO Reset the environement to an initial state
        pass

    def render(self, mode='human', close=False):

        # TODO OPTIONAL: Use sumo-gui to display the simulation for a
        # particular window of time
        pass


class programEnv(gym.Env):
    """ Custom Environement following gym specs"""

    def __init__(self,
                 # agent_type='JAgent',
                 nbr_actions=8,
                 *args, **kargs):

        super(programEnv, self).__init__()

        # Action Space
        # a descrete set of actions to be passed to the traci module for
        # execution

        # Example for discrete action space
        self.action_field = spaces.Discrete(6)

        # Full program for the traffic light: {'r': 0, 'y': 1, 'g' : 2, 'G': 3}
        # one phase:['abcdefgh']
        program_0 = ['rrggrrgg',
                     'ggrrggrr'] * 12

        program_1 = ['grrrgrrr',
                     'rgrrrgrr',
                     'rrgrrrgr',
                     'rrrgrrrg'] * 6

        program_2 = ['grrrgrrr',
                     'ggrrggrr',
                     'rgrrrgrr',
                     'rrgrrrgr',
                     'rrggrrgg',
                     'rrrgrrrg'] * 4

        program_3 = ['grrrgrrr',
                     'ggrrggrr',
                     'rrgrrrgr',
                     'rrggrrgg'] * 6

        program_4 = ['ggrrggrr',
                     'rgrrrgrr',
                     'rrgrrrgr',
                     'rrggrrgg'] * 6

        program_5 = ['grrrrrrr',
                     'rgrrrrrr',
                     'rrgrrrrr',
                     'rrrgrrrr',
                     'rrrrgrrr',
                     'rrrrrgrr',
                     'rrrrrrgr',
                     'rrrrrrrg'] * 3

        self.programs = [program_0,
                         program_1,
                         program_2,
                         program_3,
                         program_4,
                         program_5]

        self.action_space = [np.array([state_to_array(state)
                                       for state in program])
                             for program in self.programs]
        # Example action
        # pp( f'action {i}: {self.action_space[self.action_field.sample()]}')

        # TODO Define the Observational space
        # This is supposed to be an instatiation of a sumo simulation, along
        # with the handle of a valid traci active connection
        pp('Program Environement instatiated')

    def step(self, action):

        # TODO Use the selected action to complete a step in environement,
        # while carefully using the corresponding RL scope (horizon necessary
        # for calculating the reward)

        # the step uses the traci handle to excecute the action
        pass

    def reset(self):

        # TODO Reset the environement to an initial state
        pass

    def render(self, mode='human', close=False):

        # TODO OPTIONAL: Use sumo-gui to display the simulation for a
        # particular window of time
        pass


test_DurationEnv = durationEnv()
test_ProgramEnv = programEnv()
