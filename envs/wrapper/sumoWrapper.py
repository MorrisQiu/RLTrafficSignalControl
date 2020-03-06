# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 13:40:29 2020

@authors: morris qiu, Sehail Fillali
"""

import os
import subprocess  # noqa
import sys
import random
import numpy as np
from main import (
    RENDER_SIM, DATA_PATH, CONFIG_FILE, ROUTE_FILE, STATE_FILE, LOG_FILE,
    MESSAGE_FILE, ERROR_FILE
)

from helper import state_to_array


# Import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import sumolib  # noqa: E402
from sumolib import checkBinary  # noqa: E402
import traci  # noqa: E402, F401
from traci import trafficlight as TL  # noqa: E402
from traci import lane as Ln  # noqa: E402
from traci import simulation as Sim  # noqa: E402, F401
from traci import lanearea as La  # noqa: E402, F401
from traci import constants as C  # noqa: E402, F401

sumoBinary = checkBinary('sumo-gui') if RENDER_SIM else checkBinary('sumo')
config_path = os.path.join(DATA_PATH, CONFIG_FILE)
route_path = os.path.join(DATA_PATH, ROUTE_FILE)
state_path = os.path.join(DATA_PATH, STATE_FILE)
log_path = os.path.join(DATA_PATH, LOG_FILE)
import pudb; pudb.set_trace()  # XXX BREAKPOINT
message_path = os.path.join(DATA_PATH, MESSAGE_FILE)
error_path = os.path.join(DATA_PATH, ERROR_FILE)


def generate_routefile(route_file):
    random.seed(42)  # make tests reproducible
    N = 3600  # number of time steps
    # demand per second from different directions
    pEB = 1. / 10
    pWB = 1. / 11
    pSB = 1. / 15
    pNB = 1. / 25

    with open(route_file, "w") as routes:
        print("""<routes>
        <vType id="typeWE" accel="0.8" decel="4.5" sigma="0.5" length="5" \
              minGap="2.5" maxSpeed="16.67" guiShape="passenger"/>
        <vType id="typeNS" accel="0.8" decel="4.5" sigma="0.5" length="7" \
              minGap="3" maxSpeed="25" guiShape="bus"/>

        <route id="EastBound" edges="W-0W 0W-0 0-0E 0E-E" />
        <route id="WestBound" edges="E-0E 0E-0 0-0W 0W-W" />
        <route id="SouthBound" edges="N-0N 0N-0 0-0S 0S-S" />
        <route id="NorthBound" edges="S-0S 0S-0 0-0N 0N-N" />""", file=routes)
        vehNr = 0
        for i in range(N):
            red_color = 'color="1,0,0"'
            est_string = f'    <vehicle id="EastBound_{vehNr}" type="typeWE" route="EastBound" depart="{i}" />'  # noqa: E501
            wst_string = f'    <vehicle id="WestBound_{vehNr}" type="typeWE" route="WestBound" depart="{i}" />'  # noqa: E501
            sth_string = f'    <vehicle id="SouthBound_{vehNr}" type="typeNS" route="SouthBound" depart="{i}" {red_color}/>'  # noqa: E501
            nth_string = f'    <vehicle id="NorthBound_{vehNr}" type="typeNS" route="NorthBound" depart="{i}" {red_color}/>'  # noqa: E501
            if random.uniform(0, 1) < pEB:
                print(est_string, file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pWB:
                print(wst_string, file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pSB:
                print(sth_string, file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pNB:
                print(nth_string, file=routes)
                vehNr += 1
        print("</routes>", file=routes)


class contiOBSListener(traci.StepListener):

    def __init__(self, array, Update, Append):

        self.full_OBS_array = array
        self.UpdateLastState = Update
        self.AppendStateToOBSArray = Append

    def step(self, t=0):
        self.UpdateLastState()
        self.AppendStateToOBSArray()
        print(f'contiOBSListner called at {traci.simulation.getTime()} ms.', end='\r')  # noqa

        return True


class Env_TLC:
    """ Class for Traffic Light Control Environment which is used for
    retrieving State, changing the traffic phases or duration via TRACI API"""

    def __init__(self, program_sequence, programID, tlsID, restart=False):
        generate_routefile(route_path)

        self.start_args = [sumoBinary,
                           '-c', config_path,
                           '-l', log_path,
                           '--message-log', message_path,
                           '--error-log', error_path,
                           '--no-step-log', 'true',
                           # '--duration-log.disable', 'true',
                           '-W', 'true',
                           '-S', 'true', '-Q', 'true'
                           ]

        if restart:
            traci.start(self.start_args + ['--load-state', state_path])
        else:
            traci.start(self.start_args)
            Sim.saveState(state_path)

        self.ID = tlsID
        self.programID = programID
        self.program_sequence = program_sequence
        self.lanes = TL.getControlledLanes(self.ID)
        self.links = TL.getControlledLinks(self.ID)
        self.IBlaneList = [self.links[i][0][0]for i in range(len(self.links))]
        self.OBlaneList = [self.links[i][0][1]for i in range(len(self.links))]
        self.linkList = [self.links[i][0][2]for i in range(len(self.links))]

        self.current_phase_index = TL.getPhase(self.ID)
        self.Current_Phase_State = TL.getRedYellowGreenState(self.ID)
        self.RYG_definition = TL.getCompleteRedYellowGreenDefinition(self.ID)
        self.last_state = {}
        self.UpdateLastState()
        self.full_OBS_array = np.array(None, dtype=np.float32)
        listner = contiOBSListener(
            self.full_OBS_array,
            self.UpdateLastState,
            self.AppendStateToOBSArray
        )
        traci.addStepListener(listner)

    def AppendStateToOBSArray(self, state=None):

        if state is None:
            state = self.last_state
        state = np.array([each for each in state.values()], dtype=np.float32)
        state = state.reshape((1, 10, 8))

        self.full_OBS_array = state if self.full_OBS_array.shape is () \
            else np.row_stack((
                self.full_OBS_array,
                state
            ))

    def getStateArray(self, obs=None):
        """ Function that creates the observation state as an np.array from
        three componenents: Traffic_obs, Current Program sequence and Current
        Phase."""

        if obs is None:
            obs = {None: None}
            print('No value passed to getStateArray')
        traffic = np.array([each for each in obs.values()])\
            if type(obs) == dict else obs
        program = self.program_sequence
        phase = state_to_array(self.Current_Phase_State)
        phase = state_to_array(self.next_phase_state)
        return np.row_stack((traffic, program, phase))

    def UpdateLastState(self, ):

        self.last_state['IBOccupancy'] = [Ln.getLastStepOccupancy(
            laneID) for laneID in self.IBlaneList]
        self.last_state['IBVolume'] = [Ln.getLastStepVehicleNumber(
            laneID) for laneID in self.IBlaneList]
        self.last_state['IBMeanSpeed'] = [Ln.getLastStepMeanSpeed(
            laneID) for laneID in self.IBlaneList]
        self.last_state['IBQueuSize'] = [Ln.getLastStepHaltingNumber(
            laneID) for laneID in self.IBlaneList]
        self.last_state['IBWaitingTime'] = [Ln.getWaitingTime(
            laneID) for laneID in self.IBlaneList]

        self.last_state['OBOccupancy'] = [Ln.getLastStepOccupancy(
            laneID) for laneID in self.OBlaneList]
        self.last_state['OBVolume'] = [Ln.getLastStepVehicleNumber(
            laneID) for laneID in self.OBlaneList]
        self.last_state['OBMeanSpeed'] = [Ln.getLastStepMeanSpeed(
            laneID) for laneID in self.IBlaneList]
        self.last_state['OBQueuSize'] = [Ln.getLastStepHaltingNumber(
            laneID) for laneID in self.OBlaneList]
        self.last_state['OBWaitingTime'] = [Ln.getWaitingTime(
            laneID) for laneID in self.OBlaneList]

        self.current_phase_index = TL.getPhase(self.ID)
        self.Current_Phase_State = TL.getRedYellowGreenState(self.ID)
        self.RYG_definition = TL.getCompleteRedYellowGreenDefinition(self.ID)

    def StepAndCalculate(self, lane_areas=[]):
        """ Plays the simulation for the whole chosen duration of the next
        light phase and keeps track of the new observations for the next
        decision making point. """

        while 'y' in self.Current_Phase_State:
            traci.simulationStep()

        start_time_index = int(Sim.getTime())
        Starting_VehIDs = []
        Total_VehIDs = []
        Current_VehIDs = []
        # Get list of Starting Vehicles in OBDetector Areas
        for each in [list(La.getLastStepVehicleIDs(lane_area))
                     for lane_area in lane_areas]:
            for ID in each:
                Starting_VehIDs.append(ID)
        # Get list of Total Vehicles in OBDetector Areas
        # for _ in range(seconds):
        Next_Switch = TL.getNextSwitch(self.ID)
        while traci.simulation.getTime() < Next_Switch:
            for each in [list(La.getLastStepVehicleIDs(lane_area))
                         for lane_area in lane_areas]:
                for ID in each:
                    if ID not in Total_VehIDs:
                        Total_VehIDs.append(ID)
            traci.simulationStep()

        # Get list of remaining Vehicles in OBDetector Areas
        for each in [list(La.getLastStepVehicleIDs(lane_area))
                     for lane_area in lane_areas]:
            for ID in each:
                Current_VehIDs.append(ID)

        vehicles_that_left = (
            len(Total_VehIDs) - len(Current_VehIDs) - len(Starting_VehIDs)
        )
        current_time_index = int(Sim.getTime())

        return start_time_index, current_time_index, vehicles_that_left

    def SimulateDuration(self, duration):
        """ Change the duration of the next phase, calculate the reward and
        observation_ (call StepAndCalculate) and check whether the simulation
        horizon has been reached."""

        reward = 0
        detectors = La.getIDList()
        self.next_phase_state = self.RYG_definition[0].getPhases()[
            (self.current_phase_index + 2) % 4].state

        self.RYG_definition[0].getPhases()[
            (self.current_phase_index + 2) % 4].duration = duration
        TL.setCompleteRedYellowGreenDefinition(
            self.ID,
            self.RYG_definition[0]
        )
        traci.simulationStep()
        # self.UpdateLastState()

        start_time_index, current_time_index, nbr_Veh_left_OB = \
            self.StepAndCalculate(lane_areas=detectors)

        # done = current_time_index >= 3600
        done = Sim.getMinExpectedNumber() == 0

        Total_Waiting_Times = [Ln.getWaitingTime(lane) for
                               lane in self.IBlaneList]

        reward = (nbr_Veh_left_OB - sum(Total_Waiting_Times)) / duration

        obs = self.full_OBS_array[start_time_index:current_time_index+1]
        obs = obs.mean(axis=0)
        observation_ = self.getStateArray(obs=obs)

        info = {}  # TODO

        return reward, observation_, done, info

    def ResetSimulation(self, ):
        """ Close and restart the simulation and bring the time index to the
        step at which the next decision should be made. """

        try:
            traci.close(False)
        except Exception as e:
            print(f'e: {e}')

        self.__init__(
            program_sequence=self.program_sequence,
            programID=self.programID,
            tlsID=self.ID,
            restart=False
        )

        self.next_phase_state = self.RYG_definition[0].getPhases()[
            (self.current_phase_index + 2) % 4].state
        start_time_index = int(Sim.getTime())
        Next_Switch = TL.getNextSwitch(self.ID)
        while traci.simulation.getTime() < Next_Switch:
            traci.simulationStep()

        current_time_index = int(Sim.getTime())
        obs = self.full_OBS_array[start_time_index:current_time_index+1]
        obs = obs.mean(axis=0)
        return self.getStateArray(obs=obs)

    def BuildNetwork(self,):
        """ Generate the routes as per the initial conditions passed in
        traffic_conditions, and loads them to the connected SUMo simulation"""
        pass

    def ChangePhase(self, phase_index):
        TL.setPhase(self.ID, phase_index)
        return

    def SumoStart(self,):
        """ Starts the simluartion using the appropriate binary (sumo or
        sumo-gui) if not already started."""

        pass
