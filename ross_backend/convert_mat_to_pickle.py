import pickle
import scipy.io as sio

# # read .mat file and spark values
# data = sio.loadmat("/home/zahra/Documents/avir_projects/ROSS_v1/Dataset/DATA.mat")
# print(".mat file keys are : \n", data.keys())
# spike = data['Spike']
# print("spike value is : -----------", spike)
# print("spike type is : -----------", spike.dtype)
# print("spike size is : -----------", spike.size)
# print("spike shape is : -----------", spike.shape)
#
#
# # save spark values as pickle file and load
# path = "./data_set/Raw_Data/test.pkl"
# with open(path, 'wb') as f:
#     pickle.dump(spike, f)
# print("\n----------------- data saved as pickle in path : ", path, "-----------")
# with open(path, 'rb') as f:
#     x = pickle.load(f)
#     print("saved pickle data shape is : -----------", x.shape)
#     print(x)


# --------------------------------------------------------------------------
# import os
# filename = "/run/user/1000/doc/9d846db6/DATA.mat"
# print(os.path.split(filename)[-1][:-4])
# data_path = "./data_set/Raw_Data"
# print(os.path.join(data_path, os.path.split(filename)[-1][:-4]+'.pkl'))

import pickle
with open("/home/zahra/Documents/avir_projects/ROSS_v1/ross_data/Sort_Result/0217b523-194f-49d4-aca6-a11c91dce562.pkl", 'rb') as f:
    x = pickle.load(f)
    print("saved pickle data is : -----------", x.data)


# with open("/home/zahra/Documents/avir_projects/ROSS_v1/ross_backend/data_set/Detection_Result/cc607bdb-a454-489c-87f9-4559469d3780.pkl", 'rb') as f:
#     y = pickle.load(f)
#     print("next saved pickle data is : -----------", y)