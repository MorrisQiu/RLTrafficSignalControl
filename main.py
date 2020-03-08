import gym
# import torch as T
import os
from datetime import datetime as dt
import argparse
import envs  # noqa: w0611
from RL_ModelImplementations import Agent
import numpy as np


def PrepareConstants():

    global DATA_PATH, ROUTE_FILE, CONFIG_FILE, STATE_FILE, LOG_FILE, EPS_MIN
    global MESSAGE_FILE, ERROR_FILE, RENDER_SIM, NBR_GAMES, OBSERVATIONS_SIZE
    global NBR_ACTIONS, BATCH_SIZE, EPSILON, GAMMA, LEARNING_RATE, EPS_DECAY
    global TRAIN, ON, DURATION_MODEL_PATH

    TRAIN = False
    # ON = None
    DATA_PATH = './data/'
    ROUTE_FILE = 'road.rou.xml'
    CONFIG_FILE = 'road.sumocfg'
    STATE_FILE = 'saved_state.xml'
    LOG_FILE = 'logs.xml'
    MESSAGE_FILE = 'messages.xml'
    ERROR_FILE = 'errors.xml'
    RENDER_SIM = False
    NBR_GAMES = 72
    OBSERVATIONS_SIZE = 35 * 8
    NBR_ACTIONS = 8
    BATCH_SIZE = 64
    EPSILON = 1.0
    GAMMA = 0.99
    LEARNING_RATE = 0.0003
    EPS_DECAY = 0.999996
    EPS_MIN = 0.01

    parser_descr = 'Simulation environement for training and using Deep QLearning  NeurNets to control traffic lights behaviour inside of SUMo'  # noqa
    r_desc = 'Use SUMo provided GUI (sumo-gui) to render the simulated environement'  # noqa
    d_desc = 'Path of the SUMo config and various XML files. Also the path where the output data is dumped.'  # noqa
    D_desc = 'Load the Duration Agent pyTorch parameters from the supplied file path'  # noqa
    P_desc = 'Load the Program Agent pyTorch parameters from the supplied file path'  # noqa
    t_desc = 'Launches the training routine. If ommitted the inference routine is launched instead.'  # noqa
    o_desc = 'Can be either "DURATION" or "PROGRAM". If ommitted will train both of them at the same time.'  # noqa

    parser = argparse.ArgumentParser(description=parser_descr)
    parser.add_argument('-r', '--render_sim', action='store_true', help=r_desc)  # noqa
    parser.add_argument('-d', '--data_path', type=str, default='./data/', help=d_desc)  # noqa
    parser.add_argument('-P', '--program_model_path', type=str, help=P_desc)  # noqa
    parser.add_argument('-D', '--duration_model_path', type=str, help=D_desc)  # noqa
    parser.add_argument('-t', '--train', action='store_true', help=t_desc)  # noqa
    parser.add_argument('-o', '--on', choices=['duration', 'program'], help=o_desc)  # noqa

    args = parser.parse_args()

    for each in args.__dict__:
        globals()[each.upper()] = args.__dict__[each]


PrepareConstants()


def TrainOn(environement):
    """ 'SumoDuration-vo' Trains only on the Duration Agent. The program used
    is a simple ['GGrrGGrr', 'yyrryyrr', 'rrGGrrGG', 'rryyrryy'] sequence."""

    env = gym.make(environement)
    brain = Agent(
        gamma=GAMMA,
        epsilon=EPSILON,
        batch_size=BATCH_SIZE,
        nbr_actions=NBR_ACTIONS,
        input_dims=[OBSERVATIONS_SIZE],
        lr=LEARNING_RATE)
    scores = []
    eps_history = []
    score = 0
    for i in range(NBR_GAMES):
        done = False
        observation = env.reset()
        score = 0
        while not done:
            action = brain.choose_action(observation.flatten())
            observation_, reward, done, info = env.step(action)
            score += reward
            brain.store_transition(
                observation.flatten(),
                action, reward,
                observation_.flatten(), done)
            observation = observation_
            brain.learn()
        scores.append(score)
        if i % 10 == 0 and i > 0:
            avg_score = np.mean(scores[max(0, i-10):(i+1)])
            filename = str(round(dt.today().timestamp())) +\
                '_{environement}_model_{str(round(score))}.pickle'
            checkpoint_path = os.path.join(DATA_PATH, filename)
            brain.CheckPoint(
                episode=i,
                score=avg_score,
                filepath=checkpoint_path
            )

            print('episode', i, ' score', score,
                  'average score %.3f' % avg_score,
                  'epsilon %.3f' % brain.epsilon)
        else:
            print('episode', i, ' score', score)
        eps_history.append(brain.epsilon)


def TrainOnBoth():

    print('TrainOnBoth() is under construction')


def InferenceLoop():
    print(' The inference loop is under Construction.')
    print('Use "python main.py -t to train')

    # DurationBrain = ''
    # ProgramBrain = ''


if __name__ == '__main__':
    if TRAIN:
        if ON is None:
            TRAIN_ON_DURATION = True
            TrainOnBoth()
        elif ON.upper() == 'PROGRAM':
            TrainOn('SumoProgram-v0')
            TRAIN_ON_DURATION = False
        elif ON.upper() == 'DURATION':
            TrainOn('SumoDuration-v0')
    else:
        InferenceLoop()
