import numpy as np
import scipy

# Rt_smoother
def rt_smoother(y, win_length=5):
    win_alpha = 1
    win = scipy.signal.windows.gaussian(win_length,std = win_length/win_alpha)
    win /= np.sum(win)
    conved = scipy.signal.convolve(y, win, mode='same')
    return conved

	
# Matlab Round function
def matlab_round(num):
    res = (int(num > 0) - int(num < 0)) * int(abs(num) + 0.5)
    return res