import gym
from datetime import datetime as dt
import argparse
import envs  # noqa: w0611
from RL_ModelImplementations import Agent
import numpy as np


def PrepareConstants():

    global DATA_PATH, ROUTE_FILE, CONFIG_FILE, STATE_FILE, LOG_FILE, EPS_MIN
    global MESSAGE_FILE, ERROR_FILE, RENDER_SIM, NBR_GAMES, OBSERVATIONS_SIZE
    global NBR_ACTIONS, BATCH_SIZE, EPSILON, GAMMA, LEARNING_RATE, EPS_DECAY
    global TRAIN, ON

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
    EPS_DECAY = 0.996
    EPS_MIN = 0.01

    parser_descr = 'Simulation environement for training and using Deep QLearning  NeurNets to control traffic lights behaviour inside of SUMo'  # noqa
    render_descr = ' Use SUMo provided GUI (sumo-gui) to render the simulated environement'  # noqa
    data_path_descr = 'Path of the SUMo config and various XML files. Also the path where the output data is dumped.'  # noqa
    duration_model_path_descr = 'Load the Duration Agent pyTorch parameters from the supplied file path'  # noqa
    program_model_path_descr = 'Load the Program Agent pyTorch parameters from the supplied file path'  # noqa
    train_descr = 'Launches the training routine. If ommitted the inference routine is launched instead.'  # noqa
    on_descr = 'Can be either "DURATION" or "PROGRAM". If ommitted will train both of them at the same time.'  # noqa

    parser = argparse.ArgumentParser(description=parser_descr)
    parser.add_argument('-r', '--render_sim', action='store_true', help=render_descr)  # noqa
    parser.add_argument('-d', '--data_path', type=str, default='./data/', help=data_path_descr)  # noqa
    parser.add_argument('-P', '--program_model_path', type=str, help=program_model_path_descr)  # noqa
    parser.add_argument('-D', '--duration_model_path', type=str, help=duration_model_path_descr)  # noqa
    parser.add_argument('-t', '--train', action='store_true', help=train_descr)  # noqa
    parser.add_argument('-o', '--on', choices=['duration', 'program'], help=on_descr)  # noqa

    args = parser.parse_args()

    for each in args.__dict__:
        globals()[each.upper()] = args.__dict__[each]


PrepareConstants()


def TrainOnDuration():
    """ Trains only on the Duration Agent. The program used is a simple\
        ['GGrrGGrr', 'yyrryyrr', 'rrGGrrGG', 'rryyrryy'] sequence."""

    env = gym.make('SumoDuration-v0')
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
        if i % 10 == 0 and i > 0:
            avg_score = np.mean(scores[max(0, i-10):(i+1)])
            brain.CheckPoint(
                i,
                str(round(dt.today().timestamp())) + '_duration_model.pickle'
                    )
            print('episode', i, ' score', score,
                  'average score %.3f' % avg_score,
                  'epsilon %.3f' % brain.epsilon)
        else:
            print('episode', i, ' score', score)
        eps_history.append(brain.epsilon)
        done = False
        observation = env.reset()
        score = 0
        while not done:
            action = brain.choose_action(observation.flatten())
            observation_, reward, done, info = env.step(action)
            score += reward
            brain.store_transition(observation.flatten(), action, reward,
                                   observation_.flatten(), done)
            observation = observation_
            brain.learn()
        scores.append(score)


def TrainOnProgram():
    print('TrainOnProgram() is under construction')


def TrainOnBoth():
    print('TrainOnBoth() is under construction')


def InferenceLoop():
    print(' The inference loop is under Construction.')
    print('Use "python main_Training.py -t to train')


if __name__ == '__main__':
    if TRAIN:
        if ON is None:
            TRAIN_ON_DURATION = True
            TrainOnBoth()
        elif ON.upper() == 'PROGRAM':
            TrainOnProgram()
            TRAIN_ON_DURATION = False
        elif ON.upper() == 'DURATION':
            TrainOnDuration()
    else:
        InferenceLoop()
