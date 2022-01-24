#主入口

from matplotlib.pyplot import show
from neuron import States
import wirelessNode
import neuronNetworks
from configure import config
from logger import logger
import random

def addColor(color, value):
  result = '\033[1;'
  if color == 'r':
    result = result + '31;40m '
  elif color == 'g':
    result = result + '32;40m '
  elif color == 'b':
    result = result + '34;40m '
  elif color == 'w':
    result = result + '37;40m '

  result = result + str(value) + ' \033[0m '
  return result

#设置随机数种子，方便调试 DEBUG
random.seed(54919487)

wn = wirelessNode.wirelessNetwork()
nn = neuronNetworks.neuronNetwork()

wn.setNN(nn)

timeLoop = 0
timeSec = 0
slotPerSec = config.slotPerSec
nodeCount = config.nodeCount

logger.logger.debug('开始测试')


while True:
    timeLoop = 0
    for i in range(slotPerSec):
        wn.timeLapse(timeSec, i)
    timeSec = timeSec + 1
    #每隔它的一秒它就输出一下。
    #首先打印当前的时间
    showOut = '当前时间:' + addColor('g', timeSec)

    nnWorkState = nn.getWorkState()
    oriID = 0
    desID = 0
    showOut = showOut + ' ' + str(nnWorkState[0])
    oriID = nnWorkState[1][0]
    desID = nnWorkState[1][1]

    if nnWorkState[0] == neuronNetworks.WorkState.ON_ADJUST_WEIGHT:
      showOut = showOut + ' 调整权重节点: ' + str(oriID) + ' 当前测试权重: ' + str(desID) + ' 稳定下损失值: ' + str(nn.getCurStableLoss()) + '\n' 
    else:
      showOut = showOut + ' 起始测试ID：' + str(oriID) + ' 终点ID： ' + str(desID) + ' 稳定下损失值: ' + str(nn.getCurStableLoss()) + '\n'


    for i in range(config.nodeCount):
      if i == oriID:
        showOut = showOut + addColor('b', '*')
      elif i == desID:
        showOut = showOut + addColor('w', 'D')
      elif nn.getNodeState(i) == States.CONNECTED:
        showOut = showOut + addColor('g', ' O ')
      else:
        showOut = showOut + addColor('r', ' O ')
    print("\033c")

    print('\r ' + showOut, end='', flush=True)
    #print('字体有色，且有背景色 \033[0m')

