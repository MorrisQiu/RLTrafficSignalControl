# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 13:40:29 2020

@author: morris qiu
"""

import os
import sys
import numpy as np
# from sumolib import checkBinary


# Import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

# import traci.constants as tc
import traci  # noqa: E402, F401
from traci import trafficlight as TL  # noqa: E402
from traci import lane as Ln  # noqa: E402
from traci import simulation as Sim  # noqa: E402, F401
from traci import lanearea as La  # noqa: E402, F401

Sim.saveState('test_save_state.xml')


class Env_TLC:
    """
    Class for Traffic Light Control Environment which is used for retrieving
    State, changing the traffic phases or duration via TRACI API

    """

    def __init__(self, programID, tlsID):
        self.ID = tlsID
        self.light_logic = TL.getCompleteRedYellowGreenDefinition(self.ID)[0]
        self.programID = programID
        self.CurrentPhase = TL.getPhase(self.ID)
        self.lanes = TL.getControlledLanes(self.ID)
        self.links = TL.getControlledLinks(tlsID)
        self.RYG_definition = TL.getCompleteRedYellowGreenDefinition(tlsID)
        self.last_state = {}

        self.IBlaneList = [self.links[i][0][0]for i in range(len(self.links))]
        self.OBlaneList = [self.links[i][0][1]for i in range(len(self.links))]
        self.linkList = [self.links[i][0][2]for i in range(len(self.links))]

    def getStateArray(self, ):
        return np.row_stack([np.array(each)
                             for each in self.last_state.values()])

    def updateLastState(self, ):

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

    def ChangePhase(self, phase_index):
        TL.setPhase(self.ID, phase_index)
        return

    def StepAndCalculate(seconds, OBDetectors):
        Starting_VehIDs = []
        Total_VehIDs = []
        Current_VehIDs = []

        # Query for Starting Vehicles in OBDetector Areas
        for each in [list(La.getLastStepVehicleIDs(lane_area))
                     for lane_area in OBDetectors]:
                for ID in each:
                    Starting_VehIDs.append(ID)

        # Query for Total Vehicles in OBDetector Areas
        for _ in range(seconds):
            for each in [list(La.getLastStepVehicleIDs(lane_area))
                         for lane_area in OBDetectors]:
                for ID in each:
                    if ID not in Total_VehIDs:
                        Total_VehIDs.append(ID)
            traci.simulationStep()

        # Query for remaining Vehicles in OBDetector Areas
        for each in [list(La.getLastStepVehicleIDs(lane_area))
                     for lane_area in OBDetectors]:
                for ID in each:
                    Current_VehIDs.append(ID)
        return len(Total_VehIDs) - len(Current_VehIDs) - len(Starting_VehIDs)

    def SimulateDuration(self, duration):
        # current_time = traci.getTime()
        reward = -300
        done = 1
        reward_period = 120
        lane_areas = La.getIDList()

        self.current_phase_duration = TL.getPhaseDuration()
        self.light_logic.\
            getPhases()[(self.CurrentPhase + 2) % 4].duration = duration

        nbr_Veh_left_OB = self.StepAndCalculate(
            reward_period,
            OBDetectors=lane_areas)

        Total_Waiting_Times = [Ln.getWaitingTime(lane) for
                               lane in self.IBlaneList]

        reward = (nbr_Veh_left_OB / duration) - sum(Total_Waiting_Times)
        # reward = (total flow of cars - sigmoid(total_waiting_time)) / action

        self.updateLastState()
        observation_ = self.getStateArray()

        info = {}  # TODO

        return reward, observation_, done, info
