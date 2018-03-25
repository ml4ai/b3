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
from pybrain.rl.environments.mazes import Maze, MDPMazeTask 
from pybrain.rl.learners.valuebased import ActionValueTable
from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners import Q, QLambda, SARSA #@UnusedImport
from pybrain.rl.explorers import BoltzmannExplorer #@UnusedImport
from pybrain.rl.experiments import Experiment
from pybrain.rl.experiments import EpisodicExperiment
from pybrain.rl.environments import Task, EpisodicTask
warnings.filterwarnings("ignore")
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
table = ActionValueTable(81, 4)
table.initialize(1.)
# create agent with controller and learner - use SARSA(), Q() or QLambda() here
# learner = Q()
learner = SARSA()
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
for i in range(50):
    # interact with the environment (here in batch mode)
    experiment.doInteractions(100)
    agent.learn()
    agent.reset()
    # and draw the table
    pylab.imshow(table.params.reshape(81,4).max(1).reshape(9,9), 
                 origin='upper', interpolation='none')
    pylab.title('Episode: '+str(i+1)+'/50')
    pylab.show()
    pylab.pause(0.01)
pylab.ioff()
pylab.show()