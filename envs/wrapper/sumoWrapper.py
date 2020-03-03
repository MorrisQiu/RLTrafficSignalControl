# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 13:40:29 2020

@author: morris qiu
"""

import os
import sys
import random
import numpy as np

from helper import state_to_array


# Import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

# import traci.constants as tc
from sumolib import checkBinary  # noqa: E402
import traci  # noqa: E402, F401
from traci import trafficlight as TL  # noqa: E402
from traci import lane as Ln  # noqa: E402
from traci import simulation as Sim  # noqa: E402, F401
from traci import lanearea as La  # noqa: E402, F401
from traci import constants as C  # noqa: E402, F401


def generate_routefile():
    random.seed(42)  # make tests reproducible
    N = 3600  # number of time steps
    # demand per second from different directions
    pEB = 1. / 10
    pWB = 1. / 11
    pSB = 1. / 15
    pNB = 1. / 25

    with open("../../data/road.rou.xml", "w") as routes:
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
            est_string = f'    <vehicle id="EastBound_{vehNr}" type="typeWE" route="EastBound" depart="{i}" />' #  noqa: E501
            wst_string = f'    <vehicle id="WestBound_{vehNr}" type="typeWE" route="WestBound" depart="{i}" />' #  noqa: E501
            sth_string = f'    <vehicle id="SouthBound_{vehNr}" type="typeNS" route="SouthBound" depart="{i}" {red_color}/>' #  noqa: E501
            nth_string = f'    <vehicle id="NorthBound_{vehNr}" type="typeNS" route="NorthBound" depart="{i}" {red_color}/>' #  noqa: E501
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


class Env_TLC:
    """
    Class for Traffic Light Control Environment which is used for retrieving
    State, changing the traffic phases or duration via TRACI API

    """

    def __init__(self, program_sequence, programID, tlsID, restart=False):

        sumoBinary = checkBinary('sumo')
        # sumoBinary = checkBinary('sumo-gui')
        generate_routefile()

        self.start_args = [sumoBinary,
                           "-c", "../../data/road.sumocfg",
                           '-l', '../../data/log.xml',
                           '--message-log', '../../messages.xml',
                           '--error-log', '../../errors.xml'
                           ]
        self.Restart_args = [sumoBinary,
                             '-c', '../../data/road.sumocfg',
                             '--load-state', 'test_save_state.xml',
                             '-l', '../../data/log.xml',
                             '--message-log', '../../messages.xml',
                             '--error-log', '../../errors.xml'
                             ]
        """
    -l, --log FILE                       Writes all messages to FILE (implies
    --message-log FILE                   Writes all non-error messages to FILE
    --error-log FILE                     Writes all warnings and errors to FILE
        """

        if restart:
            traci.start(self.Restart_args)
        else:
            traci.start(self.start_args)

        Sim.saveState('test_save_state.xml')

        self.ID = tlsID
        self.programID = programID
        self.program_sequence = program_sequence
        self.CurrentPhase = TL.getPhase(self.ID)
        self.Current_Phase_State = TL.getRedYellowGreenState(self.ID)
        self.lanes = TL.getControlledLanes(self.ID)
        self.links = TL.getControlledLinks(tlsID)
        self.RYG_definition = TL.getCompleteRedYellowGreenDefinition(tlsID)
        self.IBlaneList = [self.links[i][0][0]for i in range(len(self.links))]
        self.OBlaneList = [self.links[i][0][1]for i in range(len(self.links))]
        self.linkList = [self.links[i][0][2]for i in range(len(self.links))]
        self.last_state = {}
        self.UpdateLastState()
        self.continuous_observations = {}
        for each in self.last_state.keys():
            self.continuous_observations[each] = []

    def getStateArray(self, obs_dict=None):
        """ Function that creates the observation state as an np.array from
        three componenents: Traffic_obs, Current Program sequence and Current
        Phase."""

        if obs_dict is None:
            obs_dict = {None: None}
            print('No value passed to getStateArray')
        traffic = np.array([each for each in obs_dict.values()])
        program = self.program_sequence
        current_phase = state_to_array(self.Current_Phase_State)
        return np.row_stack((traffic, program, current_phase))

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
        self.Current_Phase_State = TL.getRedYellowGreenState(self.ID)
        self.CurrentPhase = TL.getPhase(self.ID)

    def ChangePhase(self, phase_index):
        TL.setPhase(self.ID, phase_index)
        return

    def ResetContinuousOBS(self, ):
        """
        Purge the continuous observations to start tracking new values.
        """

        for each in self.continuous_observations.keys():
            self.continuous_observations[each] = []
        return

    def UpdateContinuousOBS(self, ):
        """
        Append the observations from the current simulation step into the array
        """

        self.UpdateLastState()
        for each in self.continuous_observations.keys():
            self.continuous_observations[each].append(
                np.array(self.last_state[each])
            )
        return

    def StepAndCalculate(self, lane_areas=[]):
        """ Plays the simulation for the whole chosen duration of the next
        light phase and keeps track of the new observations for the next
        decision making point. """

        traci.simulationStep()
        Starting_VehIDs = []
        Total_VehIDs = []
        Current_VehIDs = []
        self.ResetContinuousOBS()
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
            self.UpdateContinuousOBS()
            traci.simulationStep()

        # Get list of remaining Vehicles in OBDetector Areas
        for each in [list(La.getLastStepVehicleIDs(lane_area))
                     for lane_area in lane_areas]:
            for ID in each:
                Current_VehIDs.append(ID)

        vehicles_that_left = (
            len(Total_VehIDs) - len(Current_VehIDs) - len(Starting_VehIDs)
        )

        return vehicles_that_left

    def SimulateDuration(self, duration):
        """ Change the duration of the next phase, calculate the reward and
        observation_ (call StepAndCalculate) and check whether the simulation
        horizon has been reached."""

        # current_time = traci.getTime()
        reward = -300
        # reward_measurement_period = 120
        detectors = La.getIDList()

        # self.current_phase_duration = TL.getPhaseDuration(self.ID)
        self.RYG_definition[0].getPhases()[
            (self.CurrentPhase + 2) % 4].duration = duration
        TL.setCompleteRedYellowGreenDefinition(
            self.ID,
            self.RYG_definition[0]
        )

        nbr_Veh_left_OB = self.StepAndCalculate(lane_areas=detectors)

        sim_time_index = traci.simulation.getTime()
        done = sim_time_index >= 3600

        Total_Waiting_Times = [Ln.getWaitingTime(lane) for
                               lane in self.IBlaneList]

        reward = (nbr_Veh_left_OB - sum(Total_Waiting_Times)) / duration

        for each in self.continuous_observations.keys():
            self.continuous_observations[each] = np.array(
                self.continuous_observations[each]).mean(axis=0)
        observation_ = self.getStateArray(
            obs_dict=self.continuous_observations)

        info = {}  # TODO

        return reward, observation_, done, info

    def ResetSimulation(self,):
        """ Close and restart the simulation and bring the time index to the
        step at which the next decision should be made. """

        traci.close(False)
        self.__init__(
            program_sequence=self.program_sequence,
            programID=self.programID,
            tlsID=self.ID,
            restart=True
        )
        Next_Switch = TL.getNextSwitch(self.ID)
        while traci.simulation.getTime() < Next_Switch:
            self.UpdateContinuousOBS()
            traci.simulationStep()

        for each in self.continuous_observations.keys():
            self.continuous_observations[each] = np.array(
                self.continuous_observations[each]).mean(axis=0)
        return self.getStateArray(
            obs_dict=self.continuous_observations)

    def BuildNetwork(self,):
        """ Generate the routes as per the initial conditions passed in
        traffic_conditions, and loads them to the connected SUMo simulation"""
        pass

    def SumoStart(self,):
        """ Starts the simluartion using the appropriate binary (sumo or
        sumo-gui) if not already started."""

        pass

    def cummulateObservations(self, ):
        """ Appends each step's observations to the current cummulative
        observations."""

        for each in self.last_state.keys():
            self.continuous_observations[each].append(
                np.array(self.last_state[each]))

        return

    def getContinuousObservations(self, ):
        """ Brings the time index to the decision making point while keeping
        track of the observation space values."""

        self.continuous_observations = {}
        # initialize reward observations
        for each in self.last_state.keys():
            self.continuous_observations[each] = []
        Next_Switch = TL.getNextSwitch(self.ID)
        while traci.simulation.getTime() < Next_Switch:
            traci.simulationStep()
            self.cummulateObservations()
            # self.UpdateLastState()
            # for each in self.last_state.keys():
            #     continuous_observations[each].append(
            #         np.array(self.last_state[each]))

        for each in self.continuous_observations.keys():
            self.continuous_observations[each] = np.array(
                self.continuous_observations[each]).mean(axis=0)
        return self.getStateArray(obs_dict=self.continuous_observations)

    def ContinuousResetSimulation(self,):
        """ Returns getContinuousObservations() result """

        return self.getContinuousObservations()
