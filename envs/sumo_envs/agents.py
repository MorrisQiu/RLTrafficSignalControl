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
import sumoWrapper
from sumoWrapper import Env_TLC
from sumoWrapper import SimulateDuration
from sumoWrapper import ResetSimulation


class sumoDurationEnv(gym.Env):
    """ Custom Environement following gym specs"""

    def __init__(self,
                 # agent_type='JAgent',
                 # nbr_actions=8,
                 *args, **kargs):

        super(sumoDurationEnv, self).__init__()

        # Action space
        # a descrete set of actions to be passed to the traci module for
        # execution

        self.action_field = spaces.Discrete(8)
        self.action_space = [7, 15, 25, 35, 50, 70, 90, 120]

        # Example action
        # pp( f'action {i}: {actions[self.action_field.sample()]}')

        # Observational space
        # Full program for the traffic light: {'r': 0, 'y': 1, 'g' : 2, 'G': 3}
        program = ['rrGGrrGG', 'GGrrGGrr'] * 12
        self.current_tlProgram = np.array([state_to_array(state)
                                           for state in program])

        # Observational state constituents for a junction of 8 lanes (right on
        # red is not taken into account in the Traffic Light logic)
        # [a, b, c, d, e, f, g, h]:
        tlID = 'tl0'
        # tlID = TL.getIDList()[0]
        self.TcLt_simulation = Env_TLC(
            program_sequence=self.current_tlProgram,
            programID='0',
            tlsID=tlID)

        self.TcLt_simulation.ResetSimulation()

        # 'IBOccupancy' (1 x 8)
        # 'IBVolume' (1 x 8)
        # 'IBMeanSpeed' (1 x 8)
        # 'IBQueuSize' (1 x 8)
        # 'IBWaitingTime' (1 x 8)
        # 'OBOccupancy' (1 x 8)
        # 'OBVolume' (1 x 8)
        # 'OBMeanSpeed' (1 x 8)
        # 'OBQueuSize' (1 x 8)
        # 'OBWaitingTime (1 x 8)
        # 'FullProgramRYGCycle (24 x 8)
        # 'NextPhaseRYG (1 x 8)

        pp('Program Environement instatiated')

    def step(self, action):
        # TODO Use the selected action to complete a step in environement,
        # while carefully using the corresponding RL scope (horizon necessary
        # for calculating the reward)

        reward, observation_, done, info = \
            self.TcLt_simulation.SimulateDuration(action)

        return observation_, reward, done, info


    def reset(self):

        observation = self.TcLt_simulation.ResetSimulation()\
            + self.current_tlProgram \
            + state_to_array(self.TcLt_simulation.Current_Phase_State)
        return observation


class sumoProgramEnv(gym.Env):
    """ Custom Environement following gym specs"""

    def __init__(self,
                 # agent_type='JAgent',
                 nbr_actions=8,
                 *args, **kargs):

        super(sumoProgramEnv, self).__init__()

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

