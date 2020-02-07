from pprint import pprint as pp
import numpy as np
import itertools
import random

# tls = traci.trafficlight
# tl_list = tls.getIDList()
# logic = tls.getCompleteRedYellowGreenDefinition('tl0')[1]
# logic.phases


class ConflictMatrix:

    def __init__(self, matrix=None):

        if matrix is None:
            print("conflict matrix has to be included")
        else:
            self.matrix = np.array(matrix)

    def test_conflict(self, phase_state):
        return has_conflict(phase_state, self)


cm1 = [
    [0, 0, 1, 1, 0, 1, 1, 1],
    [0, 0, 1, 1, 1, 1, 1, 1],
    [1, 1, 0, 0, 1, 1, 0, 1],
    [1, 1, 0, 0, 1, 1, 1, 1],
    [0, 1, 1, 1, 0, 0, 1, 1],
    [1, 1, 1, 1, 0, 0, 1, 1],
    [1, 1, 0, 1, 1, 1, 0, 0],
    [1, 1, 1, 1, 1, 1, 0, 0]]

conf_1 = ConflictMatrix(cm1)
phase_state = 'rygGrygG'

light_values = {
    'r': 0,
    'y': 1,
    'g': 2,
    'G': 3
}


def state_to_array(state='rrrrrrrr'):

    array = [light_values[light] for light in [each for each in state]]
    return array


def array_to_state(array=[0, 0, 0, 0, 0, 0, 0, 0]):

    lights = []
    values = []
    for value, light in enumerate(light_values):
        lights.append(light)
        values.append(value)

    state = [lights[index] for index in [values.index(each) for each in array]]
    return ''.join(state)


def PhaseMask(phase_state):

    state_array = state_to_array(phase_state)
    tlight_dimension = len(state_array)
    mask = np.kron(state_array, state_array).reshape((tlight_dimension,
                                                      tlight_dimension))
    return mask


def has_conflict(phase_state, conf_matx=conf_1):

    hadamard = np.multiply(PhaseMask(phase_state), conf_matx.matrix)

    # print(hadamard)

    return not np.all(hadamard == 0)


def get_action_space(elements, N):
    result = []
    for permutation in itertools.product(elements, repeat=N):
        result.append(array_to_state(list(permutation)))
    print(f'Number of possible permutations: {len(result)}')
    return result


full_action_space = get_action_space([0, 1, 2, 3], 8)

action_space = [state for state
                in full_action_space if
                not has_conflict(state, conf_1)]

print(f'Permutations without conflict: {len(action_space)}')
