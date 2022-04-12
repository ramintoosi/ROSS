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

    else:
        # 1-d data
        for k in range(center.shape[1]):
            out[k][:] = np.abs(center[k] - data)

    return out


def stepfcm(data, U, cluster_n, expo):
    mf = np.power(U, expo)
    center = (mf @ data) / (np.array([np.sum(mf, axis=1)]).T @ np.ones((1, data.shape[1])))
    dist = distfcm(center, data)
    obj_fcn = np.sum(np.sum(np.power(dist, 2) * mf, axis=0))
    tmp = np.power(dist, (-2 / (expo - 1)))
    U_new = tmp / (np.ones([cluster_n, 1]) @ np.array([np.sum(tmp, axis=0)]))

    return U_new, center, obj_fcn


def FCM(data, cluster_n, options=[2, 100, 1e-5, 1]):
    """
    FCM Data set clustering using fuzzy c-means clustering
    inputs:
        data
        cluster_n : number of clusters in the data set
        OPTIONS[0] : exponent for the matrix U (default: 2.0)
        OPTIONS[1]: maximum number of iterations (default: 100)
        OPTIONS[2]: minimum amount of improvement (default: 1e-5)
        OPTIONS[3]: info display during iteration (default: 1)
    """
    data_n = data.shape[0]
    in_n = data.shape[1]

    expo = options[0]  # Exponent for U
    max_iter = options[1]  # Max. iteration
    min_impro = options[2]  # Min. improvement
    display = options[3]  # Display info or not

    obj_fcn = np.zeros((max_iter, 1))  # Array for objective function

    # Initial fuzzy partition:
    U = initfcm(cluster_n, data_n)

    # Main Loop:
    for i in range(max_iter):
        U, center, obj_fcn[i] = stepfcm(data, U, cluster_n, expo)
        if display:
            print('Iteration count = {cnt}, obj_fcn = {obj}\n'.format(cnt=i, obj=obj_fcn[i]))

        # check termination condition:
        if i > 1:
            if abs(obj_fcn[i] - obj_fcn[i - 1]) < min_impro:
                break

    iter_n = i  # Actual number of iterations
    # if iter_n + 1 != max_iter:
    #   obj_fcn[iter_n+1:max_iter] = []

    return center, U, obj_fcn

