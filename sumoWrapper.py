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
# import traci
from traci import trafficlight as TL
from traci import lane as Ln


class Env_TLC:
    """
    Class for Traffic Light Control Environment which is used for retrieving
    State, changing the traffic phases or duration via TRACI API

    """

    def __init__(self, programID, tlsID):
        self.ID = tlsID
        self.programID = programID
        self.lanes = TL.getControlledLanes(self.ID)
        self.links = TL.getControlledLinks(tlsID)
        self.RYG_definition = TL.getCompleteRedYellowGreenDefinition(tlsID)
        self.last_state = {}

        self.IBlaneList = [self.links[i][0][0]for i in range(len(self.links))]
        self.OBlaneList = [self.links[i][0][1]for i in range(len(self.links))]
        self.linkList = [self.links[i][0][2]for i in range(len(self.links))]

    def getStateArray(state):
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
