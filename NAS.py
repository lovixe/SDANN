import imp
import random
from configure import config
from model import Model
from neuron import States
import numpy as np

class BaseAdjust(object):
    def __init__(self, models) -> None:
        self.complete = False
        self.models = models    #模型列表

    def isComplete(self):
        for item in self.models:
            if item.isComplete() == False:
                return False
        return True

    def start(self): pass

class AddedWeight(object):
    def __init__(self, weight, model) -> None:
        self.weight = weight
        self.model = model
        self.model.resetResult()    #开始进行测试了
    
    #计算均方误差
    def rmse(self,value):
        value = np.array(value)
        return np.sqrt(((value) ** 2).mean())

    #获取评估结果,这里是取均值 
    def getResult(self):
        return self.model.getResult()

    #检查是否完成
    def isComplete(self):
        return self.model.isComplete()

#增加的边线
class AddedEdge(object):
    def __init__(self, srcID, desID, models) -> None:
        self.srcID = srcID
        self.desID = desID
        self.models = models
        self.weightTester = []
        for model in models:
            model.addEdge(srcID, desID)
        #开始获取权重，并逐一安排上
        for i in range(len(config.weights)):
            self.models[i].setWeight(srcID, desID, config.weights[i])
            self.weightTester.append(AddedWeight(config.weights[i], self.models[i]))

    def isComplete(self):
        for item in self.weightTester:
            if item.isComplete() == False:
                return False
        #完成了之后，直接恢复原样
        self.doRestore()
        return True

    def getOpResult(self):
        #获取最优的结果，包括结果值，权重.这里假定了所有的任务都已经完成了
        minValue = 1
        minWeight = []
        for item in self.weightTester:
            if item.getResult() < minValue:
                minValue = item.getResult()
                minWeight = item.weight
        return minValue, minWeight

    #恢复models的状态
    def doRestore(self):
        for item in self.models:
            item.delEdge(self.srcID, self.desID)

class AddedNode(object):
    def __init__(self, nodeID, models) -> None:
        self.nodeID = nodeID
        self.models = models     

        #记录自己的最佳结果,默认是1
        self.minValue = 1
        self.srcID = -1
        self.weight = []

        print('当前新增边线，测试终点为 {0}'.format(nodeID))

        #找到自己的所有节点
        if self.models[0].getNodeState(self.nodeID) == States.SCATTERED:
            return 

        #先获取到所有的连接到这个节点的节点,指的是神经网络
        nnConnect = self.models[0].nn.getEdgeToNode(self.nodeID)

        #得到所有连接到这个节点的实质连接，并去掉ID小于当前节点的
        wnConnect = self.models[0].nn.getConnectToNode(self.nodeID)
        if len(wnConnect) == 0:
            return

        #查找还没有连接的比自己ID大的节点,有的话，就作为候选
        for item in wnConnect:
            if (item not in nnConnect) and (item > self.nodeID):
                #开始测试
                tmp = AddedEdge(item, self.nodeID, self.models)
                #开始测试一条边，对边的测试是多线程的
                while tmp.isComplete() == False:
                    pass
                #获取结果 
                minValue, minWeight = tmp.getOpResult()
                if minValue < self.minValue:
                    self.minValue = minValue
                    self.srcID = item
                    self.weight = minWeight

    def getOpResult(self):
        return self.srcID, self.nodeID, self.weight, self.minValue                                                                                                  
    
class AddEdge(BaseAdjust):
    def start(self, lastLoss):
        self.lastLoss = lastLoss
        #开始工作,先设置增加ID
        self.curNode = AddedNode(0, self.models)

        while True:
            opSrcID, opDesID, opWeight, value = self.curNode.getOpResult()
            if value < self.lastLoss:
                print('发现更小损失 {}'.format(value))
                self.lastLoss = value
                #同步修改所有的节点信息
                for item in self.models:
                    item.addEdge(opSrcID, opDesID)
                    item.setWeight(opSrcID, opDesID, opWeight)
                #将下一个终点设置为本节点,并开始进行测试
                self.curNode = AddedNode(opSrcID, self.models)
            #然后继续寻找下一个节点，直到完成
            #现在的结果并不比之前的好
            else:
                #这里有一些判断条件，如果达到了末尾，那么退出，否则随机的选择一个节点
                temp = self.models[0].getConnectToNode(self.curNode.nodeID)
                wnConnect = []
                for item in temp:
                    if item > self.curNode.nodeID:
                        wnConnect.append(item)

                if len(wnConnect) == 0:
                    #本次添加器已经完成了工作, 直接返回就可以了
                    print('本次增加测试已经完成')
                    return

                #没有到头，那就随机的找一个
                randomValue = random.randint(0,len(wnConnect) - 1)

                #logger.logger.debug('延长至节点' + str(wnConnect[randomValue]))
                self.curNode = AddedNode(wnConnect[randomValue], self.models)


class adjustWeight(BaseAdjust):
    def start(self, lossValue):
        self.lossValue = lossValue
        #随机选择一个节点作为调整权重的节点
        self.adjNodeID = random.randint(1, config.nodeCount - 1)

        print('选择{0}作为调整权重节点'.format(self.adjNodeID))

        #无需记录旧有的权重，因为一定在覆盖范围内

        #准备开始调整权重
        self.weights = config.weights
        self.testResults = []
        for i in range(len(self.weights)):
            self.models[i].setSelfWeight(self.adjNodeID, self.weights[i])
            self.models[i].resetResult()

        while True:
            hasDone = True
            for item in self.models:
                if item.isComplete() == False:
                    hasDone = False
            if hasDone == True:
                break
        
        #已经测试完成，现在开始检查各个结果
        minValue = 1
        minIndex = -1
        for i in range(len(self.models)):
            if self.models[i].getResult() < minValue:
                minValue = self.models[i].getResult()
                minIndex = i
        #统一更新所有的模型
        for item in self.models:
            item.setSelfWeight(self.adjNodeID, self.weights[minIndex])
        self.lossValue = minValue

class NAS(object):
    def __init__(self, models) -> None:
        self.lastLost = 1       #最后的损失值
        self.models = models    #模型
        if len(self.models) != len(config.weights):
            raise Exception('模型个数不对')
    
    def doTest(self):
        lastLost = 1
        while True:
            #增加边
            adder = AddEdge(self.models)
            adder.start(lastLost)
            lastLost = adder.lastLoss

            #调整一个节点的权重
            adj = adjustWeight(self.models)
            adj.start(lastLost)
            adj.start(lastLost)
            adj.start(lastLost)
            adj.start(lastLost)
            lastLost = adj.lossValue
            print('最佳损失值为{0}'.format(lastLost))
