from configure import config

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
    
    def timeLapse(self):
        self.timestamp = self.timestamp + 1
        return self.checkObsolete()

#数据包类，可以包括多个不同的数据包
class packet(object):
    def __init__(self) -> None:
        self.packets = []
        self.maxNodeCapacity = config.maxQIInFrm  #最多可以包括多少个节点的信息
        self.aggGoal = 0                        #当其中的节点数据包因为超时后也不会允许再次聚合
        self.hadAgg = 0                         #曾经聚合的数据包个数  
        self.timestamp =  0                     #记录时间戳,这是数据包的时间戳，每个节点也有自己的时间戳的。  
        self.maxLiveTime = config.maxLiveTime

    #时间流逝, 当返回False，表示这个数据包已经超时了。当返回True时，表明这个数据包正常
    def timeLapse(self):
        self.timestamp = self.timestamp + 1     
        if self.timestamp >= self.maxLiveTime:
            return False
        packetLens = len(self.packets)
        for i in range(packetLens - 1, 0, -1):
            if self.packets[i].timeLapse() == True:
                del self.packets[i]
        return True

    def getRemainSpace(self):
        return self.maxNodeCapacity - self.hadAgg

    #聚合, 输入参数为等待聚合的数据包们
    def aggregation(self, waitAggPackets):
        count = 0
        for item in waitAggPackets:
            if self.hadAgg < self.maxNodeCapacity:
                self.packets.append(item)
                self.hadAgg = self.hadAgg + 1
                count = count + 1
            else:
                break
        #计算聚合得分
        self.aggGoal = self.aggGoal + (self.maxLiveTime - self.timestamp) * count
        return count