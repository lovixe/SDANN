#这个文件是描述无线节点的

from configure import config
from abc import abstractclassmethod, ABCMeta
import random
from packet import packet
from packet import nodePacket

class node(object):
    def __init__(self, nodeID, linkGroup) -> None:
        self.nodeID = nodeID
        self.linkGroup = linkGroup
        self.dataGeneralCycle = config.dataGeneralCycle     #多少秒产生数据
        self.slotPerSecond = config.slotPerSec              #每秒多少个时间槽

        self.packets = []       #节点当前的数据包，一般是一个，多的认为直接通过地理路由方法送到了SN，这里只关注未被聚合的信息

        #设置数据产生时间
        self.createDataTimeSec = random.randint(0, self.dataGeneralCycle - 1)
        self.createDataTimeSlot = random.randint(0, self.slotPerSecond - 1)

    #产生数据
    def createData(self):
        #因为只有不全的packet，所以需要合并
        if len(self.packets) == 0:
            #产生一个新的packet
            newPacket = packet()
            self.packets.append(newPacket)
        
        #packets里面有数据包的存在，那么将自己的数据存放进去,注意，packets里面只会有一个
        #先产生一个自己的数据吧
        newData = nodePacket(self.nodeID)
        self.packets[0].aggregation()

    #时间流逝
    def timeLapse(self, timeSec, timeOffset):
        pass


    #设置NN
    def setNeuronNetwork(self, nn):
        self.neuronNetwork = nn

    #接收到其他节点的信息
    def recvData(self, packet):
        pass

class IWN(meteaclass=ABCMeta):
    @abstractclassmethod
    def setDataToNode(self, desID, packet): pass

    @abstractclassmethod
    def neuronNetworkTimeLapse(self, nodeID, timeOffset, inputVector=None): pass


class wirelessNetwork(IWN):
    def __init__(self) -> None:
        #开始建立网络
        self.nodes = []
        self.nodeCount = config.nodeCount
        self.linkGroup = []
        self.generateLink()

        #产生节点,注意的是节点0是SN。这里就不区分对待了，节点自己区分吧
        for i in range(self.nodeCount):
            self.nodes.append(node(i, self.linkGroup))

    def setNN(self, neuronNetwork):
        self.neuronNetwork = neuronNetwork
        self.neuronNetwork.setLinkGroup(self.linkGroup)

    #实现一下接口
    def setDataToNode(self, desID, packet):
        self.nodes[desID].recvData(packet)

    def neuronNetworkTimeLapse(self, nodeID, timeOffset, inputVector=None):
        self.neuronNetwork.timeLapse(nodeID, timeOffset, inputVector)

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
                for j in range(i - 3, self.nodeCount - connectRange, 1):
                    connects.append(j)
            self.linkGroup.append(connects)

    #接受时间流逝
    def timeLapse(self, timeSec, timeOffset):
        for i in range(len(self.nodes)):
            self.nodes[i].timeLapse(timeSec, timeOffset)
        
