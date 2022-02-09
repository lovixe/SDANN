from asyncore import dispatcher_with_send
from concurrent.futures import thread
from neuron import States
import wirelessNode
import neuronNetworks
from configure import config
import threading

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

    def isComplete(self):
        #只有当线程停止之后，才可以获取数据
        if self.complete == False:
            return False
        return self.nn.isComplete() #这里基本是True

    #调用这个函数时，线程会重新跑起来
    def resetResult(self):
        self.nn.resetResult()
        self.complete = False   

    def getResult(self):
        return self.nn.getResult()

    def startTest(self):
        if self.isComplete() == True:
            return False

        self.nn.resetResult()
        t = threading.Thread(target=self.doTest)
        t.start()
        return True

    def doTest(self):
        while True:
            #一直保持运行，当已完成的时候，不做什么动作
            if self.complete == True:
                pass
            else:
            #当未完成时，开始工作，直到完成测试。完成测试后complete会被修改为True
                timeSec = 0
                slotPerSec = config.slotPerSec
                while self.nn.isComplete() == False:
                    for i in range(slotPerSec):
                        self.wn.timeLapse(timeSec, i)
                    timeSec = timeSec + 1
                self.complete = True
        