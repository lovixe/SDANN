import configparser

#读取权重配置
def getWeightConfig():
    cf = configparser.ConfigParser()
    cf.read('configure.ini')
    weightCount = cf.get('weight', 'weightCount')
    weights = []
    for i in range(weightCount):
        weightItem = cf.get('weight', 'weight' + str(i))
        weightStrSplit = weightItem.split(',')
        weightNew = []
        for item in weightStrSplit:
            weightNew.append(int(item))
        weights.append(weightNew)
    return weights

#读取测试次数
def getTestCountConfig():
    cf = configparser.ConfigParser()
    cf.read('configure.ini')
    testCount = cf.get('test', 'testCount')
    return int(testCount)

#读取节点个数
def getNodeCount():
    cf = configparser.ConfigParser()
    cf.read('configure.ini')
    result = cf.get('node', 'nodeCount')
    return int(result)

#读取单帧最大QI
def getMaxQIInFrm():
    cf = configparser.ConfigParser()
    cf.read('configuire.ini')
    result = cf.get('system', 'maxQIInFrm')
    return int(result)

#数据产生周期
def getDataGeneralCycle():
    cf = configparser.ConfigParser()
    cf.read('configuire.ini')
    result = cf.get('system', 'dataGeneralCycle')
    return int(result)

#每秒分为多少个段
def getSlotPerSec():
    cf = configparser.ConfigParser()
    cf.read('configuire.ini')
    result = cf.get('system', 'slotPerSecond')
    return int(result)