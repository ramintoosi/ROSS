import numpy as np


def initfcm(cluster_n, data_n):
    U = np.random.rand(cluster_n, data_n)
    col_sum = np.sum(U, axis=0)
    U = U / np.tile(col_sum, (cluster_n, 1))
    
    return U

	
def distfcm(center, data):
    out = np.zeros((center.shape[0], data.shape[0]))

    # fill the output matrix
    if center.shape[1] > 1:
        for k in range(center.shape[0]):
            diff = np.ones((data.shape[0], 1)) @ np.array([center[k][:]])
            sub = data - diff
            squared = np.power(sub, 2)
            out[k][:] = np.sqrt(np.sum(squared, axis=1).T)
            #out[k][:] = np.sqrt(np.sum(np.power(data - (np.ones((data.shape[0], 1)) @ np.array([center[k][:]]), 2), axis=1)).T)
    
    else:
        #1-d data
        for k in range(center.shape[1]):
            out[k][:] = np.abs(center[k] - data)
            
    return out


def stepfcm(data, U, cluster_n, expo):
    mf = np.power(U, expo)
    center = (mf @ data) / (np.array([np.sum(mf, axis=1)]).T @ np.ones((1, data.shape[1])))
    dist = distfcm(center, data)
    obj_fcn = np.sum(np.sum(np.power(dist, 2) * mf, axis=0))
    tmp = np.power(dist, (-2/(expo-1)))
    U_new = tmp / (np.ones([cluster_n, 1]) @ np.array([np.sum(tmp, axis=0)]))
    
    return U_new, center, obj_fcn	

