#主入口

import copy
from matplotlib.pyplot import show
from neuron import States
import neuronNetworks
from configure import config
from logger import logger
import random
import model
import NAS

# def addColor(color, value):
#   result = '\033[1;'
#   if color == 'r':
#     result = result + '31;40m '
#   elif color == 'g':
#     result = result + '32;40m '
#   elif color == 'b':
#     result = result + '34;40m '
#   elif color == 'w':
#     result = result + '37;40m '

#   result = result + str(value) + ' \033[0m '
#   return result

#设置随机数种子，方便调试 DEBUG
random.seed(54919487)

# wn = wirelessNode.wirelessNetwork()
# nn = neuronNetworks.neuronNetwork()

# wn.setNN(nn)

# timeLoop = 0
# timeSec = 0
# slotPerSec = config.slotPerSec
# nodeCount = config.nodeCount

print('开始测试')

#创建多线程所用的模型
models = []
models.append(model.Model())
weightCount = len(config.weights)
for i in range(1, len(config.weights), 1):
  models.append(copy.deepcopy(models[0]))

for item in models:
  if item.startTest() == False:
    raise Exception('Wrong Thread')

#准备将控制权交给NAS
nas = NAS.NAS(models)
nas.doTest()
