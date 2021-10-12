import fcm_utils *

def fcm(data, cluster_n, options=[2, 100, 1e-5, 1]):
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
    
    expo = options[0] # Exponent for U
    max_iter = options[1] # Max. iteration
    min_impro = options[2] # Min. improvement
    display = options[3] # Display info or not
    
    obj_fcn = np.zeros((max_iter, 1)) # Array for objective function
    
    # Initial fuzzy partition:
    U = initfcm(cluster_n, data_n)
    
    # Main Loop:
    for i in range(max_iter):
        U, center, obj_fcn[i] = stepfcm(data, U, cluster_n, expo)
        if display:
            print('Iteration count = {cnt}, obj_fcn = {obj}\n'.format(cnt=i, obj=obj_fcn[i]))
        
        # check termination condition:
        if i > 1:
            if abs(obj_fcn[i] - obj_fcn[i-1]) < min_impro:
                break
    
    iter_n = i # Actual number of iterations
    if iter_n + 1 != max_iter:
        obj_fcn[iter_n+1:max_iter] = []
    
    return center, U, obj_fcn