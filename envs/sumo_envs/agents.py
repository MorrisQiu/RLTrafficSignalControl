"""
Created on Sat 15 Feb 2020 14:12:49 UTC

Custom Environement for building TrafficLight RL Agents using SUMO

#@Author: Sehail Fillali
"""

from main import (
    DURATION_MODEL_PATH, GAMMA, EPSILON, BATCH_SIZE, NBR_ACTIONS,
    OBSERVATIONS_SIZE, LEARNING_RATE
)
from RL_ModelImplementations import Agent
from envs.wrapper.sumoWrapper import Env_TLC, state_to_array
from pprint import pprint as pp
import torch as T
import numpy as np
import gym


def PrepareConstants():
    global DURATION_ACTIONS, PROGRAM_ACTIONS
    # Possible durations to be chosen from
    DURATION_ACTIONS = [7, 15, 25, 35, 50, 70, 90, 120]

    # Full program for the traffic light: {'r': 0, 'y': 1, 'g' : 2, 'G': 3}
    # one phase:['abcdefgh'] each letter is one lane (right on red lanes are
    # ignored)
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

    PROGRAM_ACTIONS = [program_0,
                       program_1,
                       program_2,
                       program_3,
                       program_4,
                       program_5]


PrepareConstants()


class sumoDurationEnv(gym.Env):
    """ Environement for training on the perfect Duration of the next traffic
    light phase which maximizes performance (as determined by the reward
    metric)
    """

    def __init__(self,
                 # agent_type='JAgent',
                 # nbr_actions=8,
                 *args, **kargs):

        super(sumoDurationEnv, self).__init__()

        # Action space
        # a descrete set of actions to be passed to the traci module for
        # execution

        self.action_space = [7, 15, 25, 35, 50, 70, 90, 120]

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
        self.TfcLgt_sim = Env_TLC(
            program_sequence=self.current_tlProgram,
            programID='0',
            tlsID=tlID)

        # self.TfcLgt_sim.ContinuousResetSimulation()

        OBS_indexForKey = {
            'IBOccupancy': 1,
            'IBVolume': 2,
            'IBMeanSpeed': 3,
            'IBQueuSize': 4,
            'IBWaitingTime': 5,
            'OBOccupancy': 6,
            'OBVolume': 7,
            'OBMeanSpeed': 8,
            'OBQueuSize': 9,
            'OBWaitingTime': 10,
        }

        # Full OBS input tensor
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

        pp('Duration Environement instatiated')

    def step(self, action):
        ''' Use the selected action to complete a step in environement,
        while carefully using the corresponding RL scope (horizon necessary for
                calculating the reward) '''

        reward, observation_, done, info = \
            self.TfcLgt_sim.SimulateDuration(self.action_space[action])

        return observation_, reward, done, info

    def reset(self):
        '''
        Reset the simulation after the episode is finished. The whole
        simulation is reset to it's starting condition.
        '''

        return self.TfcLgt_sim.ResetSimulation()

    def render(self, mode='human', close=False):

        # TODO OPTIONAL: Use sumo-gui to display the simulation for a
        # particular window of time
        pass


class sumoProgramEnv(gym.Env):
    """ Environement for training on the perfect TrfcLgt Program (sequence of
    light configurations for each lane) which maximizes perfomance (as
    determined by the reward metric)"""

    def __init__(self,
                 # agent_type='JAgent',
                 nbr_actions=8,
                 *args, **kargs):

        super(sumoProgramEnv, self).__init__()

        if DURATION_MODEL_PATH is None:
            print("Please make sure to use the -D option and specify a model path!")  # noqa
        else:
            try:
                params = T.load(DURATION_MODEL_PATH)
                print(f'Duration model loaded: epsod {params["episode"]}, score {params["score"]}')  # noqa
            except Exception as e:
                print(f'error loading duration model: {e}')
            duration_brain = Agent(
                gamma=GAMMA,
                epsilon=EPSILON,
                batch_size=BATCH_SIZE,
                nbr_actions=NBR_ACTIONS,
                input_dims=[OBSERVATIONS_SIZE],
                lr=LEARNING_RATE)
            self.duration_brain.load_state_dict(params['state'])
            self.duration_brain.eval()

        # Example for discrete action space
        self.programs = PROGRAM_ACTIONS
        self.action_space = [np.array([state_to_array(state) for state in
                                       program]) for program in self.programs]

        self.duration_env = gym.make('SumoDuration-v0')
        self.TfcLgt_sim = self.duration_env.TfcLgt_sim

        # FIXME: Right now it's same as the Duration Agent
        pp('Program Environement instatiated')

    def step(self, action):

        # TODO Use the selected action to complete a step in environement,
        # while carefully using the corresponding RL scope (horizon necessary
        # for calculating the reward)

        reward, observation_, done, info = \
            self.TfcLgt_sim.SimulateDuration(self.action_space[action])
        return observation_, reward, done, info

    def reset(self):

        # TODO Reset the environement to an initial state
        pass

    def render(self, mode='human', close=False):

        # TODO OPTIONAL: Use sumo-gui to display the simulation for a
        # particular window of time
        pass
