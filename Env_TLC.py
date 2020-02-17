# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 13:40:29 2020

@author: morris qiu
"""

import os
import sys
import numpy as np

# Import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


from sumolib import checkBinary
import traci
import traci.constants as tc


class Env_TLC:
    """
    Class for Traffic Light Control Environment which is used for retrieving State,
    changing the traffic phases or duration via TRACI API

    """

    def __init__(self, programID, tlsID):
        self.id = tlsID
        self.programID = programID

    def traffic_volume(self, ):
        links = traci.trafficlight.getControlledLinks(tlsID)
        IBlaneList = [links[i][0][0]for i in range(len(links))]
        OBlaneList = [links[i][0][1]for i in range(len(links))]
        linkList = [links[i][0][2]for i in range(len(links))]

        traci.lane.getLastStepHaltingNumber(laneID)
        traci.lane.getLastStepOccupancy(laneID)
        traci.lane.getLastStepVehicleNumber(laneID)
        traci.lane.getWaitingTime(laneID)

        IBVolume = [traci.lane.getLastStepVehicleNumber(
            laneID) for laneID in IBlaneList]
        OBVolume = [traci.lane.getLastStepVehicleNumber(
            laneID) for laneID in OBlaneList]

        IBWaitingTime = [traci.lane.getWaitingTime(
            laneID) for laneID in IBlaneList]
        IBOccupancy = [traci.lane.getLastStepOccupancy(
            laneID) for laneID in IBlaneList]

        observation = np.row_stack(
            (IBVolume, OBVolume, IBWaitingTime, IBOccupancy))
