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
            if random.uniform(0, 1) < pEB:
                print('    <vehicle id="EastBound_%i" type="typeWE" \
                      route="EastBound" depart="%i" />' \
                      % (vehNr, i), file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pWB:
                print('    <vehicle id="WestBound_%i" type="typeWE" \
                      route="WestBound" depart="%i" />' \
                      % (vehNr, i), file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pSB:
                print('    <vehicle id="SouthBound_%i" type="typeNS" \
                      route="SouthBound" depart="%i" color="1,0,0"/>' \
                      % (vehNr, i), file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pNB:
                print('    <vehicle id="NorthBound_%i" type="typeNS" \
                      route="NorthBound" depart="%i" color="1,0,0"/>' \
                      % (vehNr, i), file=routes)
                vehNr += 1
        print("</routes>", file=routes)


class Env_TLC:
    """
    Class for Traffic Light Control Environment which is used for retrieving
    State, changing the traffic phases or duration via TRACI API

    """

    def __init__(self, program_sequence, programID, tlsID):

        sumoBinary = checkBinary('sumo-gui')
        generate_routefile()

        self.Simulation_args = [sumoBinary, "-c", "../../data/road.sumocfg",
                                "--tripinfo-output", "tripinfo.xml"]
        self.Restart_args = [sumoBinary, '-c', '../../data/road.sumocfg',
                             '--load-state', 'test_save_state.xml',
                             '--output-prefix', 'TIME']
        traci.start(self.Simulation_args)
        Sim.saveState('test_save_state.xml')

        self.ID = tlsID
        self.programID = programID
        self.program_sequence = program_sequence
        self.CurrentPhase = TL.getPhase(self.ID)
        self.Current_Phase_State = TL.getRedYellowGreenState(self.ID)
        self.lanes = TL.getControlledLanes(self.ID)
        self.links = TL.getControlledLinks(tlsID)
        self.RYG_definition = TL.getCompleteRedYellowGreenDefinition(tlsID)[0]
        self.last_state = {}

        self.IBlaneList = [self.links[i][0][0]for i in range(len(self.links))]
        self.OBlaneList = [self.links[i][0][1]for i in range(len(self.links))]
        self.linkList = [self.links[i][0][2]for i in range(len(self.links))]

    def getStateArray(self, ):
        observation = np.row_stack((
            [np.array(each) for each in self.last_state.values()],
            self.program_sequence,
            state_to_array(self.Current_Phase_State)
        ))
        return observation

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
        self.Current_Phase_State = TL.getRedYellowGreenState(self.ID)
        self.CurrentPhase = TL.getPhase(self.ID)

    def ChangePhase(self, phase_index):
        TL.setPhase(self.ID, phase_index)
        return

    def StepAndCalculate(seconds, OBDetectors=[]):
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

        self.current_phase_duration = TL.getPhaseDuration(self.ID)
        self.RYG_definition.\
            getPhases()[(self.CurrentPhase + 2) % 4].duration = duration

        nbr_Veh_left_OB = self.StepAndCalculate(
            reward_period,
            OBDetectors=list(lane_areas))

        Total_Waiting_Times = [Ln.getWaitingTime(lane) for
                               lane in self.IBlaneList]

        reward = (nbr_Veh_left_OB / duration) - sum(Total_Waiting_Times)
        # reward = (total flow of cars - sigmoid(total_waiting_time)) / action

        self.updateLastState()
        observation_ = self.getStateArray()

        info = {}  # TODO

        return reward, observation_, done, info

    def ResetSimulation(self,):
        traci.close(False)
        traci.start(self.Restart_args)
        Next_Switch = TL.getNextSwitch(self.ID)
        while traci.simulation.getTime() < Next_Switch:
            traci.simulationStep()
        self.updateLastState()
        return self.getStateArray()
