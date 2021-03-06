#这个文件是描述无线节点的

from configure import config
from abc import abstractclassmethod, ABCMeta
import random
from packet import packet
from packet import nodePacket
from neuron import States
import copy
from logger import logger

class node(object):
    def __init__(self, nodeID, linkGroup, iwn) -> None:
        self.nodeID = nodeID
        self.linkGroup = linkGroup
        self.dataGeneralCycle = config.dataGeneralCycle     #多少秒产生数据
        self.slotPerSecond = config.slotPerSec              #每秒多少个时间槽

        self.packet = None       #节点当前的数据包，一般是一个，多的认为直接通过地理路由方法送到了SN，这里只关注未被聚合的信息

        self.iwn = iwn

        #设置数据产生时间
        self.createDataTimeSec = random.randint(0, self.dataGeneralCycle - 1)
        self.createDataTimeSlot = random.randint(0, self.slotPerSecond - 1)

    #检查满了的数据包
    def checkFull(self):
        if self.packet.getRemainSpace() == 0:
            #直接发送给SN，认为传输完成了
            self.neuronNetwork.overTransmit(self.packet)
            self.packet = None
            return True
        else:
            return False

    #产生数据
    def createData(self):
        #因为只有不全的packet，所以需要合并
        if self.nodeID == 0:
            return

        if self.packet == None:
            #产生一个新的packet
            self.packet = packet()
        
        #packets里面有数据包的存在，那么将自己的数据存放进去
        #先产生一个自己的数据吧
        newData = nodePacket(self.nodeID)
        self.packet.addQI(newData)

        #检查是否满了
        if self.packet.getRemainSpace() == 0:
            self.neuronNetwork.overTransmit(self.packet)
            self.packet = None

    #在散点时，将数据包发送给最近的非散点
    def sendDataToConnected(self):
        for item in self.linkGroup[self.nodeID]:
            if self.iwn.getNodeState(item) == States.CONNECTED:
                #logger.logger.info('散点发送数据包: ' + str(self.nodeID) + ' -> ' + str(item))
                self.iwn.sendDataToNode(item, self.packet)
                self.packet = None
                return
        #如果附近真的没有，那么直接清空缓存吧
        self.packet = None

    #获取周边节点信息，生成输入值
    def getInputVector(self, timeOffset):
        #生成一个字典
        result = {'timeOffset': timeOffset}
        if self.packet == None:
            result[str(self.nodeID)] = 0
        else:
            result[str(self.nodeID)] = self.packet.getRemainSpace()

        for item in self.linkGroup[self.nodeID]:
            result[str(item)] = self.iwn.getNodeQI(item)
        return result

    #时间流逝
    def timeLapse(self, timeSec, timeOffset):
        #检查是否需要产生数据
        if (timeSec % self.dataGeneralCycle) == self.createDataTimeSec and timeOffset == self.createDataTimeSlot:
            self.createData()
        
        #做出决策，如果是散点，那么传输数据就完事了。如果不是散点，那么需要整理数据并给神经网络做出决策
        if self.iwn.getNodeState(self.nodeID) == States.SCATTERED:
            #散点
            if self.packet != None:
                #查找最近的非散点，把数据给他
                self.sendDataToConnected()
        else:
            #对自己的数据包内的时间戳进行变动
            if self.packet != None:
                self.packet.timeLapse()
                #因为系统是从前向后扫描，数据是从后向前传递，所以不会出现一个数据包在一个时间槽内被增加了两次的情况
                #本节点是神经网络的连接节点，需要做出神经网络决策的
                result = self.neuronNetwork.timeLapse(self.nodeID, timeOffset, self.getInputVector(timeOffset))
                if result != None and result != self.nodeID:
                    #需要转发数据，如果是自己，那么忽略就可以

                    listNode = ''
                    for item in self.packet.packets:
                        listNode = listNode + str(item.nodeID) + ','
                    #logger.logger.info('发送数据包: ' + str(self.nodeID) + ' -> ' + str(result) + '. 包括 ' + listNode)
                    self.iwn.sendDataToNode(result, self.packet)
                    self.packet = None
            
            if self.nodeID == 0:
                self.neuronNetwork.timeLapse(self.nodeID, timeOffset)
    #设置NN
    def setNeuronNetwork(self, nn):
        self.neuronNetwork = nn

    #接收到其他节点的信息
    def recvData(self, packet):
        #这是很重要的一部分，完成之后，就可以进行测试了.
        #如果是SN节点，那么直接给SN节点就可以了
        if self.nodeID == 0:
            self.neuronNetwork.overTransmit(packet)
        else:
            tmp = copy.deepcopy(packet)
            if self.packet == None:
                #本身没有数据，那么直接用就可以
                self.packet = tmp
            else:
                #进行合并
                if self.packet.getRemainSpace() > len(tmp.packets):
                    #并没有填满，那么直接聚合就可以
                    self.packet = copy.deepcopy(self.packet.aggregation(tmp))
                    #完成聚合了，那么这个tmp就没有什么用途了
                    if self.packet.getRemainSpace() == 0:
                        self.neuronNetwork.overTransmit(self.packet)
                        self.packet = None
                else:
                    #一个数据包不够，那么只能先填满一个，然后将另一个作为自己的数据包
                    tmp, self.packet = self.packet.aggregationFull(tmp)
                    self.neuronNetwork.overTransmit(tmp)
                    

    #获取信息量
    def getQI(self):
        if self.nodeID == 0:
            return config.maxQIInFrm
        else:
            if self.packet == None:
                return 0
            else:
                return len(self.packet.packets)

class IWN():
    
    def sendDataToNode(self, desID, packet): 
        pass

    def getNodeState(self, desID): 
        pass

    def getNodeQI(self, desID): 
        pass


class wirelessNetwork(IWN):
    def __init__(self) -> None:
        super().__init__()
        #开始建立网络
        self.nodes = []
        self.nodeCount = config.nodeCount
        self.linkGroup = []
        self.generateLink()

        #产生节点,注意的是节点0是SN。这里就不区分对待了，节点自己区分吧
        for i in range(self.nodeCount):
            self.nodes.append(node(i, self.linkGroup, self))

    def setNN(self, neuronNetwork):
        self.neuronNetwork = neuronNetwork
        self.neuronNetwork.setLinkGroup(self.linkGroup)
        #设置NN
        for item in self.nodes:
            item.setNeuronNetwork(neuronNetwork)

    #实现一下接口
    def sendDataToNode(self, desID, packet):
        self.nodes[desID].recvData(packet)

    #获取节点状态
    def getNodeState(self, desID):
        return self.neuronNetwork.getNodeState(desID)

    #获取节点信息量
    def getNodeQI(self, desID):
        return self.nodes[desID].getQI()

    #产生连接
    def generateLink(self):
        #先产生所需的节点连接空间
        #需要注意的是节点的连接是双向的,这里就简单粗暴的相等了
        connectRange = config.connectRange
        for i in range(self.nodeCount):
            connects = []
            if i < connectRange or i >= self.nodeCount - connectRange:
                if i < connectRange:
                    #开端添加的
                    for j in range(0, i + 3):
                        connects.append(j)
                else:
                    for j in range(i - 3, self.nodeCount):
                        connects.append(j)
            else:
                for j in range(i - 3, self.nodeCount, 1):
                    if j <= i + 3 and j != i:
                        connects.append(j)
            self.linkGroup.append(connects)

    #接受时间流逝
    def timeLapse(self, timeSec, timeOffset):
        for i in range(len(self.nodes)):
            self.nodes[i].timeLapse(timeSec, timeOffset)
        
