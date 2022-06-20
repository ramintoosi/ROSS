import matplotlib.pyplot as plt

fig = plt.figure()
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)
ax1.plot([1,1,1,2,3,4,5,6,7])
ax2.plot([1,1,1,1,1,1,1,1,2,2,2,2,3])
plt.show()