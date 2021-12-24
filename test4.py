
import os
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
import random
from itertools import count
from matplotlib import style

style.use('fivethirtyeight')

fig = plt.figure()
# ax1 = fig.add_subplot(1,1,1)
x_vals = []
y_vals = []
index = count()

def animate(i):
        
    x_vals.append(next(index))
    y_vals.append(random.randint(0,5))
    
    plt.cla()
    plt.plot(x_vals, y_vals)

ani = animation.FuncAnimation(plt.gcf(), animate, interval=1000)
plt.tight_layout()
plt.show()