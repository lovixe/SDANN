from asyncore import dispatcher_with_send
from concurrent.futures import thread
import imp
import multiprocessing
from queue import Queue
from neuron import States
import wirelessNode
import neuronNetworks
from configure import config
from multiprocessing import Process
from multiprocessing import Value
import numpy as np

class Model(object):
    def __init__(self):
        self.wn = wirelessNode.wirelessNetwork()
        self.nn = neuronNetworks.neuronNetwork()
        self.wn.setNN(self.nn)
        self.complete = True

    def setWeight(self, srcID, desID, weight):
        self.nn.setConnectWeight(srcID, desID, weight)

    def setSelfWeight(self, nodeID, weight):
        self.nn.setNodeSelfWeight(nodeID, weight)

    def addEdge(self, srcID, desID):
        self.nn.addConnect(srcID, desID)
    
    def delEdge(self, srcID, desID):
        self.nn.delConnect(srcID, desID)

    def getNodeState(self, nodeID):
        return self.nn.getNodeState(nodeID)

    def getConnectToNode(self, nodeID):
        return self.nn.getConnectToNode(nodeID)

    def isComplete(self):
        if self.runFlag.value == 0:
            return False
        else:
            return True

    #调用这个函数时，线程会重新跑起来
    def resetResult(self):
        self.startTest()

    def getResult(self):
        return self.result.value

    def setModelID(self, id):
        self.id = id

    def startTest(self):

        self.runFlag = Value('b', False)
        self.result = Value('f', 1)

        self.t = Process(target=self.doTest, args=(self.nn, self.wn, self.runFlag, self.result))
        self.t.start()
        return True

    def doTest(self, nn, wn, runFlag, result):
        #当未完成时，开始工作，直到完成测试。完成测试后complete会被修改为True
        timeSec = 0
        slotPerSec = config.slotPerSec
        nn.resetResult()
        while nn.isComplete() == False:
            for i in range(slotPerSec):
                wn.timeLapse(timeSec, i)
            timeSec = timeSec + 1
        runResult = nn.getResult()
        value = np.array(runResult) 
        result.value = np.sqrt(((value) ** 2).mean())
        runFlag.value = 1
        