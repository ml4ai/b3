#!/usr/bin/env python
__author__ = 'Thomas Rueckstiess, ruecksti@in.tum.de'
""" This example demonstrates how to use the discrete Temporal Difference
Reinforcement Learning algorithms (SARSA, Q, Q(lambda)) in a classical
fully observable MDP maze task. The goal point is the top right free
field. """
from scipy import *
import sys, time
import pylab
import warnings
import numpy as np;
from pybrain.rl.environments.mazes import Maze, MDPMazeTask 
from pybrain.rl.learners.valuebased import ActionValueTable
from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners import NFQ, ActionValueNetwork, Q, QLambda, SARSA #@UnusedImport
from pybrain.rl.explorers import BoltzmannExplorer #@UnusedImport
from pybrain.rl.experiments import Experiment
from pybrain.rl.experiments import EpisodicExperiment
from pybrain.rl.environments import Task, EpisodicTask
warnings.filterwarnings("ignore")

def get_QTable(table):
    nStates = 81;
    aQTable = np.zeros((nStates,1));
    for i in range(nStates):
        aQTable[i] = table.activate([i]);
    return aQTable.reshape(9,9);

# create the maze with walls (1)
envmatrix = array([[1, 1, 1, 1, 1, 1, 1, 1, 1],
                   [1, 0, 0, 1, 0, 0, 0, 0, 1],
                   [1, 0, 0, 1, 0, 0, 1, 0, 1],
                   [1, 0, 0, 1, 0, 0, 1, 0, 1],
                   [1, 0, 0, 1, 0, 1, 1, 0, 1],
                   [1, 0, 0, 0, 0, 0, 1, 0, 1],
                   [1, 1, 1, 1, 1, 1, 1, 0, 1],
                   [1, 0, 0, 0, 0, 0, 0, 0, 1],
                   [1, 1, 1, 1, 1, 1, 1, 1, 1]])
env = Maze(envmatrix, (7, 7))
# create task
task = MDPMazeTask(env)
# create value table and initialize with ones
# table = ActionValueTable(81, 4)
# table.initialize(0.)
table = ActionValueNetwork(1, 4)
# create agent with controller and learner - use SARSA(), Q() or QLambda() here
# learner = Q()
# learner = SARSA()
learner = NFQ()
# standard exploration is e-greedy, but a different type can be chosen as well
# learner.explorer = BoltzmannExplorer()
# create agent
agent = LearningAgent(table, learner)
# create experiment
# experiment = Experiment(task, agent)
experiment = EpisodicExperiment(task, agent)
# prepare plotting
pylab.gray()
pylab.ion()
nEpisodes = 50
for i in range(nEpisodes):
    # interact with the environment (here in batch mode)
    experiment.doInteractions(1000)
    agent.learn()
    agent.reset()
    # and draw the table
    pylab.imshow(get_QTable(table), interpolation='none')
    pylab.title('Episode: '+str(i+1)+'/'+str(nEpisodes))
    pylab.show()
    pylab.pause(0.01)
pylab.ioff()
pylab.show()
            