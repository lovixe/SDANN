#神经网络出口，神经元可以建立与出口的连接。出口有自己的运行逻辑以区别与普通的神经元节点。
from neuron import States
import packet
from configure import config
import copy
import neuron
from logger import logger


class sinkNode(neuron.neuronNode):
    def __init__(self, id) -> None:
        self.id = 0     # 默认SN就是ID为0的节点
        self.nodeID = 0
        self.nodeCount = config.nodeCount - 1     #除了SN之外的节点数量
        self.maxInforInSingleFrm = config.maxQIInFrm
        self.cycleWidth = config.maxLiveTime
        self.recvs = []                 #存储本轮内收到的数据包
        self.dataCreateCycle = config.dataGeneralCycle
        self.slotPerSec = config.slotPerSec

        self.lastLoopRecvs = []         #上一轮收到的数据包
        self.lastLossValue = 1

        self.timeOffset = 0
        self.timeSec = 0
        self.edges = []
        self.state = States.CONNECTED

    def recvPacket(self, packet):
        #SN节点的数据包，已经完成了传输，不再进行时间流逝
        self.recvs.append(copy.deepcopy(packet))

    #不断的调用这个函数，SN需要自己在何时的时候计算损失值
    #更新了一轮，则返回损失值，否则返回None
    def timeLapse(self, timeOffset):
        self.timeOffset = timeOffset
        if timeOffset == self.slotPerSec - 1:
            self.timeSec = self.timeSec + 1
            if self.timeSec % self.dataCreateCycle == 0:
                #已经到了最新的一节了，计算上一次的情况
                lost = self.calcLost()
                self.lastLossValue = lost

                self.lastLoopRecvs.clear()
                for item in self.recvs:
                    self.lastLoopRecvs.append(item)
                    recvListID = ''
                    for xxx in item.packets:
                        recvListID = recvListID + str(xxx.nodeID) + ','
                    #logger.logger.info('SN 接收到的数据包列表 ' + recvListID)

                #清理现有的记录
                self.recvs.clear()
                return lost
            else:
                return None
        else:
            return None
        
        
    #计算得分
    def calcPacketAggGoal(self, packet):
        #这里是计算一个数据包的聚合得分的
        timestamps = []
        for item in packet.packets:
            timestamps.append(item.aggTimestamp)
        timestamps.sort()
        #获得本数据包的时间长度
        t = packet.timestamp
        goal = 0
        #遍历记录的节点信息
        for i in range(len(timestamps)):
            if t == 0:
                goal = goal + pow(10, i) * 9    #直接给最大值
            else:
                if timestamps[i] != 0:
                    goal = goal + pow(10, i) * int(9 - (timestamps[i] - 1) / t)
                else:
                    goal = goal + pow(10, i) * int(9 - timestamps[i] / t)
        #返回得分
        return goal
        
    #计算聚合损失的函数
    def calcAggLoss(self):
        recvCount = 0
        #获得最大值
        maxGoal = pow(10, self.maxInforInSingleFrm) - 1
        #遍历每一个数据包，得到每个数据包的聚合损失
        loss = 0
        for packet in self.recvs:
            loss = loss + maxGoal - self.calcPacketAggGoal(packet)
            recvCount = recvCount + len(packet.packets)
            
        #增加上丢失的节点
        loss = loss + maxGoal * (self.nodeCount - recvCount)     
        #计算均方根差
        loss = loss / (2 * self.nodeCount)
        #归一
        loss = loss / (maxGoal / 2)
        return loss
    
    #计算时间损失的函数
    def calcTimeLoss(self):
        recvCount = 0
        recvedTime = []     #记录数据包接受时间
        #遍历接受到的数据包
        for item in self.recvs:
            #item 是一个数据包
            for node in item.packets:
                #记录数据包的接受时间
                recvedTime.append(node.timestamp)
                recvCount = recvCount + 1
        #计算时间上的损失值使用的是均方差损失函数。
        #接受的时间越长，其损失越大
        #lossTime = 1/(2 * nodeCount) \sum_i^n recvedTime[i]^2
        lossTime = 0
        #计算收到的数据包的时间损失
        for item in recvedTime:
            lossTime = lossTime + item * item
        #计算未收到的数据包的时间损失
        for i in range(self.nodeCount - recvCount):
            lossTime = lossTime + self.cycleWidth * self.cycleWidth
        #综合计算
        lossTime = lossTime / (2 * self.nodeCount)
        #归于[0,1]
        lossTime = lossTime / (pow(self.cycleWidth, 2) / 2)
        return lossTime

    #计算损失度函数
    def calcLost(self):
        lost = []

        lossTime = self.calcTimeLoss()
        lossQI = self.calcAggLoss()

        #得到损失值向量
        lost.append(lossTime)
        lost.append(lossQI)
        return lost

    def getLastStates(self):
        return self.lastLoopRecvs

            
            