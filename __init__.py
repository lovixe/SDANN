#主入口

import wirelessNode
import neuronNetworks
from configure import config
from logger import logger
import random
import pygame, sys
from pygame.locals import *

#時間类，负责不断的产生时间
class timeDrive(object):
    def __init__(self):
        self.timeLoop = 0

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

# 初始化pygame
pygame.init()
 
# 设置窗口的大小，单位为像素
screen = pygame.display.set_mode((500, 400))
 
# 设置窗口标题
pygame.display.set_caption('Hello World')
 
# 程序主循环
while True:
 
  # 获取事件
  for event in pygame.event.get():
    # 判断事件是否为退出事件
    if event.type == QUIT:
      # 退出pygame
      pygame.quit()
      # 退出系统
      sys.exit()
 
  # 绘制屏幕内容
  pygame.display.update()

while True:
    timeLoop = 0
    for i in range(slotPerSec):
        wn.timeLapse(timeSec, i)
    timeSec = timeSec + 1

