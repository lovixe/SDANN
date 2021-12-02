from configure import config
import copy

#单一节点数据包
class nodePacket(object):
    def __init__(self, nodeID) -> None:
        self.nodeID = nodeID
        self.timestamp = 0      #当累加到一定程度后会被删除
        self.maxLiveTime = config.maxLiveTime  #节点的最大存活时间

    def checkObsolete(self):
        if self.timestamp >= self.maxLiveTime:
            return True
        else:
            return False
    #无效了返回True， 有效返回False
    def timeLapse(self):
        self.timestamp = self.timestamp + 1
        return self.checkObsolete()

#数据包类，可以包括多个不同的数据包
class packet(object):
    def __init__(self) -> None:
        self.packets = []
        self.maxNodeCapacity = config.maxQIInFrm  #最多可以包括多少个节点的信息
        self.aggLoss = 0                        #当其中的节点数据包因为超时后也不会允许再次聚合
        self.recvTimeOffset = 0             #接受时间戳

    #时间流逝, 当返回False，表示这个数据包已经超时了。当返回True时，表明这个数据包正常
    def timeLapse(self):
        packetLens = len(self.packets)
        for i in range(packetLens - 1, 0, -1):
            if self.packets[i].timeLapse() == True:
                del self.packets[i]
        #计算得分,按照时间进行积分
        self.aggLoss = (self.maxNodeCapacity - len(self.packets)) * 1
        return True

    def getRemainSpace(self):
        return self.maxNodeCapacity - len(self.packets)

    #聚合, 输入参数为等待聚合的数据包们
    def aggregation(self, waitAggPackets):
        count = 0
        for item in waitAggPackets:
            if len(self.packets) < self.maxNodeCapacity:
                tmp = copy.deepcopy(item)
                self.packets.append(tmp)
                count = count + 1
            else:
                break
        return count

    def addQI(self, node):
        if self.getRemainSpace() > 0:
            tmp = copy.deepcopy(node)
            self.packets.append(tmp)
            return True
        else:
            return False