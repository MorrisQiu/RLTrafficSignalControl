import gym
import envs  # noqa: w0611
from RL_ModelImplementations import Agent
import numpy as np

NBR_GAMES = 30
OBSERVATIONS_SIZE = 35 * 8
NBR_ACTIONS = 8
BATCH_SIZE = 64
EPSILON = 1.0
GAMMA = 0.99
LEARNING_RATE = 0.0003
EPS_DECAY = 0.996
EPS_MIN = 0.01

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
