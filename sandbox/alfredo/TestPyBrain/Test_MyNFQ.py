""" This example demonstrates how to use the NFQ and discrete TD-RL 
algorithms (SARSA, Q, Q(lambda)) in a classical fully observable MDP 
maze task. The goal point is the top right free field."""
import warnings;
import numpy as np;
import matplotlib.pyplot as pl;
from pybrain.rl.environments.mazes import Maze, MDPMazeTask;
from pybrain.rl.learners.valuebased import ActionValueTable;
from pybrain.rl.agents import LearningAgent;
from pybrain.rl.learners import Q, QLambda, SARSA; #@UnusedImport
from pybrain.rl.experiments import Experiment;
from pybrain.datasets import SupervisedDataSet;
from pybrain.tools.shortcuts import buildNetwork;
from pybrain.supervised.trainers import BackpropTrainer;
from pybrain.structure import TanhLayer;

def setup_RL():
    # create the maze with walls (1)
    envmatrix = np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1],
                          [1, 0, 0, 1, 0, 0, 0, 0, 1],
                          [1, 0, 0, 1, 0, 0, 1, 0, 1],
                          [1, 0, 0, 1, 0, 0, 1, 0, 1],
                          [1, 0, 0, 1, 0, 1, 1, 0, 1],
                          [1, 0, 0, 0, 0, 0, 1, 0, 1],
                          [1, 1, 1, 1, 1, 1, 1, 0, 1],
                          [1, 0, 0, 0, 0, 0, 0, 0, 1],
                          [1, 1, 1, 1, 1, 1, 1, 1, 1]]);
    env = Maze(envmatrix, (7, 7));
    # create task
    task = MDPMazeTask(env);
    # create value table and initialize with ones
    table = ActionValueTable(81, 4);
    table.initialize(0.);
    # create agent with controller and learner - use SARSA(), Q() or QLambda() here
    # learner = Q()
    learner = SARSA();
    # create agent
    agent = LearningAgent(table, learner);
    # create experiment
    experiment = Experiment(task, agent);
    return experiment, agent, table;

def get_Batch_Interactions(experiment, nIters):
    ds = SupervisedDataSet(2, 1) #<Two Input Dims>, <One Output Dim>
    agent = experiment.agent;
    nGamma = agent.learner.gamma;
    tableQ = agent.module;
    agent.reset();
    for i in range(nIters):  # @UnusedVariable
        experiment.doInteractions(1);
        lastSt, lastAct, lastR = agent.lastobs, agent.lastaction, agent.lastreward;
        currentSt = experiment.task.getObservation() if lastSt in [69,61] else 70;
        nMaxQ = tableQ.getMaxAction(currentSt);
        nQ = lastR + nGamma*tableQ.getValue(currentSt, nMaxQ);
        ds.addSample([lastSt, lastAct], [nQ]) #[Input], [Output]
    return ds;

def update_QTable(table, ds):
    net = buildNetwork(2, 5, 1, hiddenclass=TanhLayer); #Num. Input, Hidden & Output Neurons
    trainer = BackpropTrainer(net, ds);
    trainer.trainUntilConvergence(maxEpochs=1);
    for i in range(table.numRows):
        for j in range(table.numColumns):
            nQ = net.activate([i,j]);
            table.updateValue(i,j,nQ);    
    
def run_RL(experiment, agent, table):
    # prepare plotting
    pl.gray();
    pl.ion();
    nEpisodes = 50
    for i in range(nEpisodes):  # @UnusedVariable
        # interact with the environment (here in batch mode)
        ds = get_Batch_Interactions(experiment, 5000);
        update_QTable(table, ds);
#         experiment.doInteractions(100);
#         agent.learn();
#         agent.reset();
        # and draw the table
        aQTable = table.params.reshape(81,4).max(1).reshape(9,9);
        pl.imshow(aQTable, interpolation='none');
        pl.title('Episode: '+str(i+1)+'/'+str(nEpisodes));
        pl.show();
        pl.pause(0.01);
    pl.ioff();
    pl.show();

if __name__=="__main__":
    warnings.filterwarnings("ignore");
    experiment, agent, table = setup_RL();
    run_RL(experiment, agent, table);
    