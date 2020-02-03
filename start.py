#!/usr/bin/env python
#Start to run the sumulation through SUMO

# @file    start.py
# @author  Morris Qiu
# @date    2020-01-29

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random

# Import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa


def generate_routefile():
    random.seed(42)  # make tests reproducible
    N = 3600  # number of time steps
    # demand per second from different directions
    pEB = 1. / 10
    pWB = 1. / 11
    pSB = 1. / 15
    pNB = 1. / 25
    with open("data/road.rou.xml", "w") as routes:
        print("""<routes>
        <vType id="typeWE" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" \
guiShape="passenger"/>
        <vType id="typeNS" accel="0.8" decel="4.5" sigma="0.5" length="7" minGap="3" maxSpeed="25" guiShape="bus"/>

        <route id="EastBound" edges="W-0W 0W-0 0-0E 0E-E" />
        <route id="WestBound" edges="E-0E 0E-0 0-0W 0W-W" />
        <route id="SouthBound" edges="N-0N 0N-0 0-0S 0S-S" />
        <route id="NorthBound" edges="S-0S 0S-0 0-0N 0N-N" />""", file=routes)
        vehNr = 0
        for i in range(N):
            if random.uniform(0, 1) < pEB:
                print('    <vehicle id="EastBound_%i" type="typeWE" route="EastBound" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pWB:
                print('    <vehicle id="WestBound_%i" type="typeWE" route="WestBound" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pSB:
                print('    <vehicle id="SouthBound_%i" type="typeNS" route="SouthBound" depart="%i" color="1,0,0"/>' % (
                    vehNr, i), file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pNB:
                print('    <vehicle id="NorthBound_%i" type="typeNS" route="NorthBound" depart="%i" color="1,0,0"/>' % (
                    vehNr, i), file=routes)
                vehNr += 1
        print("</routes>", file=routes)

# The program looks like this
#    <tlLogic id="tl0" type="static" programID="0" offset="0">
# the locations of the tls are      NESW
#        <phase duration="31" state="GrGr"/>
#        <phase duration="21"  state="yryr"/>
#        <phase duration="31" state="rGrG"/>
#        <phase duration="21"  state="ryry"/>
#    </tlLogic>


def run():
    """execute the TraCI control loop"""
    step = 0
    # we start with phase 2 where EW has green
    for i in range(20):
#    traci.trafficlight.setPhase("tl0", 2)
#    while traci.lane.getLastStepVehicleNumber("0W-0_0") <200:
#   while traci.simulation.getMinExpectedNumber() > 0:        
        traci.simulationStep()
#    if traci.trafficlight.getPhase("tl0") == 2:
            # we are not already switching
#           if traci.inductionloop.getLastStepVehicleNumber("tl0") > 0:
                # there is a vehicle from the north, switch
#       traci.trafficlight.setPhase("tl0", 3)
#           else:
                # otherwise try to keep green for EW
#               traci.trafficlight.setPhase("tl0", 2)
        eb = traci.lane.getLastStepVehicleNumber("0W-0_0")
        step += 1
        print("Step "+ str(step))
        print('Eastbound vechicles : ', eb)
    traci.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "data/road.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()
