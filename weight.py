import random
import configure
#Quantity of Information:  QI

class neuronWeight(object):
    def __init__(self, weight = None) -> None:
        if weight == None:
            weightColCount = configure.getWeightColCount()
            self.weight = []
            for i in range(weightColCount):
                self.weight.append(random.random())
        else:
            self.weight = weight

    def getWeight(self):
        return self.weight

    def setWeight(self, weight):
        #默认是按照顺序来
        self.weight = weight