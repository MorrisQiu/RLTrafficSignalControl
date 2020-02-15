"""
Created on Sat 15 Feb 2020 14:12:49 UTC

Custom Environement for building TrafficLight RL Agents using SUMO

#@Author: Sehail Fillali
"""

import os
import sys
import numpy as np
import gym
from gym import spaces
from main_DQNTutorial import NBR_ACTIONS
from Env_TLC import Env_TLC

# Import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


class sumoEnv(gym.Env):
    """ Custom Environement following gym specs"""

    def __init__(self,
                 agent_type='JAgent',
                 nbr_actions=NBR_ACTIONS,
                 *args, **kargs):

        super(sumoEnv, self).__init__()

        # TODO Define the Action space
        # a descrete set of actions to be passed to the traci module for
        # execution

        # Example for discrete action space
        self.action_space = spaces.discrete(NBR_ACTIONS)

        # TODO Define the Observational space
        # This is supposed to be an instatiation of a sumo simulation, along
        # with the handle of a valid traci active connection

        traffic_light = Env_TLC(programID, tlsID)
        print(traffic_light)

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
