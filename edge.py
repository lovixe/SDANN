from weight import neuronWeight

#边线, 边线是有方向的。两个节点之间如果要相互发送，那么会有两个边线存在与这两个节点之间。
class edge(object):
    def __init__(self, fromID, toID) -> None:
        self.fromID = fromID
        self.toID = toID  

        #配套权重, 初始化时使用随机生成的
        self.linkWeight = neuronWeight()    # 该边线配套权重

    #计算该链路通路结果, 传递的信息是当前节点的信息量
    def calc(self, sourceQI, desQI,timeOffset):
        #按照权重计算结果
        result = sourceQI * self.linkWeight.wSource + desQI * self.linkWeight.wDes + timeOffset * self.linkWeight.wTime + self.linkQuality * self.linkWeight.wLinkQuality
        #乘以放大系数，然后作为最终结果返回
        return result

    #配置权重，不配置就用默认的
    def setWeight(self, weight):
        self.linkWeight = weight

    def getWeight(self):
        return self.linkWeight.getWeight()