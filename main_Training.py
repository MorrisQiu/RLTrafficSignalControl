import gym
import argparse
import envs  # noqa: w0611
from RL_ModelImplementations import Agent
import numpy as np


def PrepareConstants():

    global DATA_PATH, ROUTE_FILE, CONFIG_FILE, STATE_FILE, LOG_FILE, EPS_MIN
    global MESSAGE_FILE, ERROR_FILE, RENDER_SIM, NBR_GAMES, OBSERVATIONS_SIZE
    global NBR_ACTIONS, BATCH_SIZE, EPSILON, GAMMA, LEARNING_RATE, EPS_DECAY

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
    model_path_descr = 'load the pyTorch parameters from the supplied file path'  # noqa

    parser = argparse.ArgumentParser(description=parser_descr)
    parser.add_argument('-r', '--render_sim', help=render_descr,
                        action='store_true')
    parser.add_argument('-d', '--data_path', help=data_path_descr, type=str,
                        default='./data/')
    parser.add_argument('-m', '--model_path', help=model_path_descr, type=str)

    args = parser.parse_args()

    for each in args.__dict__:
        globals()[each.upper()] = args.__dict__[each]


PrepareConstants()

if __name__ == '__main__':
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
            print('episode', i, ' score', score,
                  'average score %.3f' % avg_score,
                  'epsilon %.3f' % brain.epsilon)
        else:
            print("\033[F")
            print("\033[F")
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
