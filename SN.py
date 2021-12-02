#神经网络出口，神经元可以建立与出口的连接。出口有自己的运行逻辑以区别与普通的神经元节点。
import packet
from configure import config
import copy


class sinkNode(object):
    def __init__(self) -> None:
        self.id = 0     # 默认SN就是ID为0的节点
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

    def recvPacket(self, packet):
        #SN节点的数据包，已经完成了传输，不再进行时间流逝
        self.recvs.append(copy.deepcopy(packet))

    #不断的调用这个函数，SN需要自己在何时的时候计算损失值
    #更新了一轮，则返回损失值，否则返回None
    def timeLapse(self, timeOffset):
        self.timeOffset = timeOffset
        if timeOffset == 0:
            self.timeSec = self.timeSec + 1
            if self.timeSec == self.dataCreateCycle and timeOffset == self.slotPerSec - 1:
                #已经到了最新的一节了，计算上一次的情况
                lost = self.calcLost()
                self.lastLossValue = lost

                self.lastLoopRecvs.clear()
                for item in self.recvs:
                    self.lastLoopRecvs.append(item)

                #清理现有的记录
                self.recvs.clear()
                return lost
            else:
                return None
        else:
            return None

    #计算损失度函数
    def calcLost(self):
        recvCount = 0
        lost = []
        #清理重复的数据包
        recvedTime = []     #记录数据包接受时间
        aggLoss = []        #记录数据包聚合损失情况
        #遍历接受到的数据包
        for item in self.recvs:
            #item 是一个数据包
            for node in item.packets:
                #记录数据包的接受时间
                recvedTime.append(node.timestamp)
                recvCount = recvCount + 1
            aggLoss.append(item.aggGoal)

        #计算损失值
        #先计算时间上的损失值。使用的是均方差损失函数。
        # 接受的时间越长，其损失越大
        #lossTime = 1/(2 * nodeCount) \sum_i^n recvedTime[i]^2
        lossTime = 0
        for item in recvedTime:
            lossTime = lossTime + item * item
        for i in range(self.nodeCount - recvCount):
            lossTime = lossTime + self.cycleWidth * self.cycleWidth
        lossTime = lossTime / (2 * self.nodeCount)
        #归于[0,1]
        lossTime = lossTime / (pow(self.cycleWidth, 2) / 2)

        #后计算信息量的损失值。使用的同样是均方差损失函数
        #损失值有上限，设置为最大的单个节点的数据包一直到最大时间才到SN
        lossQI= 0
        maxLossQI = (config.maxQIInFrm - 1) * self.cycleWidth
        for item in aggLoss:
            if item > maxLossQI:
                tmp = maxLossQI
            else:
                tmp = item
            lossQI = lossQI + pow(tmp, 2)

        #统计丢失的节点,按最大值处理
        for i in range(self.nodeCount - recvCount):
            lossQI = lossQI + pow(maxLossQI, 2)

        # 要除以的个数是接受到的个数以及丢失的个数
        lossQI = lossQI / (2 * self.nodeCount)
        #归于[0,1]
        lossQI = lossQI / (pow(maxLossQI, 2) / 2)

        #得到损失值向量
        lost.append(lossTime)
        lost.append(lossQI)
        return lost

    def getLastStates(self):
        return self.lastLoopRecvs

            
            