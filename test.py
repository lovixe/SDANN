import numpy as np

def rmse(predictions):
    return np.sqrt(((predictions) ** 2).mean())


a = [[1,1],[1,1],[1,1]]
print(rmse(np.array(a)))