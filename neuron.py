#这个文件是神经元的类
import random
from edge import edge

from enum import Enum

class States(Enum):
    SCATTERED = 1
    CONNECTED = 2

#神经网络节点类： 注意，不是无线节点类，虽然它们之间有关系，但将其抽象为两个不同的类，因为它们处于不同的层级
class neuronNode(object):
    def __init__(self, id) -> None:
        self.nodeID = id
        self.edges = []         #与其他节点的连接记录, 里面的内容是连接的节点
        self.state = States.SCATTERED   #初始化时都是散点状态

    #增加一条边
    def addEdge(self, des, weight = None):
        newEdge = edge(self.nodeID, des)
        if weight != None:
            newEdge.setWeight(weight)
        #添加并修改状态
        self.edges.append(newEdge)
        self.state = States.CONNECTED

    #删除一条边
    def delEdge(self, desID):
        for item in self.edges:
            if item.toID == desID:
                #删除这条边
                self.edges.remove(item)
                #如果节点已经没有任何的边了，那么就修改成散点
                if len(self.edges) == 0:
                    self.state = States.SCATTERED
                return True
        return False

    #是否连接到某个节点
    def connectToSomeNode(self, nodeID):
        for item in self.edges:
            if item.toID == nodeID:
                return True
        return False

    #修改某一条边的权重
    def setEdgeWeight(self, srcID, desID, weight):
        if srcID != self.nodeID:
            return False
        
        for item in self.edges:
            if item.toID == desID:
                item.setWeight(weight)
                return True
        print("Cannot find the edge!\n")
        return False    #未找到
    
    #获取某一条边的权重
    def getEdgeWeight(self, srcID, desID):
        if srcID != self.nodeID:
            return None
        
        for item in self.edges:
            if item.toID == desID:
                return item.getWeight()
        return None

    #获取所有的边
    def getEdges(self):
        return self.edges

    #获取所有连接到的节点
    def getEdgesFromThis(self):
        result = []
        for item in self.edges:
            result.append(item.toID)
        return result

    #提取对应的输入数据
    def getInputVector(self, inputVector):
        pass

    #每过一段时间时，就会触发。参数为当前的时间偏移,以及当前节点感知到的其他节点的信息量
    def timeLapse(self, inputVector):
        if self.state == States.SCATTERED:
            #散点不需要有什么动作
            return

        #这里就是计算是否需要做出决断的了,做法是将计算各自的权重然后取最高的动作。
        max = 0.0
        connectID = None

        #TO-DO 提取出对应的数据，应为对应不同的节点是不一样的

        for item in self.edges:
            result = item.calc(inputVector)
            if result > max:
                max = result
                connectID = item.toID
        
        #这里的激活函数的中间计算过程，只有一个1，其他都是0. 为0不用处理，为1就是需要处理的
        #计算的最后一步交由上层的仿真部分进行处理
        return connectID