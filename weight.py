import random
#Quantity of Information:  QI

class neuronWeight(object):
    def __init__(self, wSource = -1, wDes = -1, wTime = -1) -> None:
        if wSource == -1:
            self.wSource = random.random()
        if wDes == -1:
            self.wDes = random.random()
        if wTime == -1:
            self.wTime = random.random()
        self.wLinkQuality = 1           #这个权重初始值就是1，它的影响比较大，而且是整体的影响，所以不打算进行变动调整

    def getWeight(self):
        result = []
        result.append(self.wSource)
        result.append(self.wDes)
        result.append(self.wTime)
        return result