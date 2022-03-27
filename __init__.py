#主入口

import copy
from importlib.resources import contents
from neuron import States
import neuronNetworks
from configure import config
from logger import logger
import random
import model
import NAS

#设置随机数种子，方便调试 DEBUG
#random.seed(54919487)
random.randint(1,10)


#创建多线程所用的模型
models = []
models.append(model.Model())
weightCount = len(config.weights)
for i in range(1, len(config.weights), 1):
  models.append(copy.deepcopy(models[0]))

for i in range(4):
  models[i].setModelID(i)


#恢复
recovery = True
if recovery:
  #有效恢复
  file = open(config.recordStructFile, 'r')
  content = file.readlines()
  #查找最后一次的结果
  lastParitition = 0
  for i in range(len(content)):
    if content[i].find('******') != -1:
      lastParitition = i

  #开始进行恢复
  for i in range(lastParitition + 1, len(content), 1):
    contents = content[i].split(':')
    if contents[0] == 'selfWeight':
      nodeID = int(contents[1])
      weight = [float(contents[2]), float(contents[3]), float(contents[4])]

      for item in models:
        item.setSelfWeight(nodeID, weight)
    elif contents[0] == 'edge':
      srcID = int(contents[1])
      desID = int(contents[2])
      weight = [float(contents[3]), float(contents[4]), float(contents[5])]
      for item in models:
        item.addEdge(srcID, desID)
        item.setWeight(srcID, desID, weight)

#准备将控制权交给NAS
nas = NAS.NAS(models)

if __name__ == '__main__':
  nas.doTest()
