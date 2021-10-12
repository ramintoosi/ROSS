import numpy as np


def initfcm(cluster_n, data_n):
    U = np.random.rand(cluster_n, data_n)
    col_sum = np.sum(U, axis=0)
    U = U / np.tile(col_sum, (cluster_n, 1))
    
    return U

	
def distfcm(center, data):
    out = np.zeros(center.shape[0], data.shape[0])

    # fill the output matrix
    if center.shape[1] > 1:
        for k in range(center.shape[0]):
            out[k][:] = np.sum(np.power(data - (np.ones(data.shape[0], 1) @ center[k][:]), 2), axis=1).T
    
    else: #1-d data
        for k in range(center.shape[1]):
            out[k][:] = np.abs(center[k] - data)
            
    return out
	

