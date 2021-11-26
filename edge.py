from weight import neuronWeight
import numpy as np

#边线, 边线是有方向的。两个节点之间如果要相互发送，那么会有两个边线存在与这两个节点之间。
class edge(object):
    def __init__(self, fromID, toID) -> None:
        self.fromID = fromID
        self.toID = toID  

        #配套权重, 初始化时使用随机生成的
        self.linkWeight = neuronWeight()    # 该边线配套权重

    #计算该链路通路结果, 传递的信息是当前节点的信息量
    def calc(self, inputVector):
        #按照权重计算结果
        return np.sum(np.multiply(inputVector, self.linkWeight.getWeight()))

    #配置权重，不配置就用默认的
    def setWeight(self, weight):
        self.linkWeight = weight

    def getWeight(self):
        return self.linkWeight.getWeight()