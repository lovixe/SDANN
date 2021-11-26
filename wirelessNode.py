#这个文件是描述无线节点的

import configure

class node(object):
    def __init__(self, nodeID, linkGroup) -> None:
        self.nodeID = nodeID
        self.linkGroup = linkGroup
        self.dataGeneralCycle = configure.getDataGeneralCycle()     #多少秒产生数据
        self.slotPerSecond = configure.getSlotPerSec()              #每秒多少个时间槽

        self.packets = []       #节点当前的数据包，一般是一个，多的认为直接通过地理路由方法送到了SN，这里只关注未被聚合的信息

    #时间流逝
    def timeLapse(self, timeOffset):
        pass


class wirelessNetwork(object):
    def __init__(self) -> None:
        #开始建立网络
        self.nodes = []
        self.nodeCount = configure.getNodeCount()
        self.linkGroup = []
        self.generateLink()

        #产生节点,注意的是节点0是SN。这里就不区分对待了，节点自己区分吧
        for i in range(self.nodeCount):
            self.nodes.append(node(i, self.linkGroup))

    def setNN(self, neuronNetwork):
        self.neuronNetwork = neuronNetwork

    #产生连接
    def generateLink(self):
        #先产生所需的节点连接空间
        #需要注意的是节点的连接是双向的,这里就简单粗暴的相等了
        connectRange = configure.getConnectRange()
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
        
