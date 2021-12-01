#主入口

import wirelessNode
import neuronNetworks
from configure import config

#時間类，负责不断的产生时间
class timeDrive(object):
    def __init__(self):
        self.timeLoop = 0



wn = wirelessNode.wirelessNetwork()
nn = neuronNetworks.neuronNetwork()

wn.setNN(nn)

timeLoop = 0
timeSec = 0
slotPerSec = config.slotPerSec
nodeCount = config.nodeCount

while True:
    timeLoop = 0
    for i in range(slotPerSec):
        wn.timeLapse(timeSec, i)
    timeSec = timeSec + 1