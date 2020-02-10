import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

from threading import Thread, Timer


class Live_Plotter(object):

    def __init__(self, time_sec, u_tot, value, setpoint):

        style.use('fivethirtyeight')

        self.time_sec = time_sec
        self.u_tot = u_tot
        self.value = value
        self.setpoint = setpoint


        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(1,2,1)
        self.ax2 = self.fig.add_subplot(1,2,2)

        self.ani = animation.FuncAnimation(self.fig, self.animate, 1000)

        plt.show()

    def animate(self, i):
        self.ax1.clear()
        self.ax1.set_ylim([0,100])
        self.ax1.set_xlim([0,60])

        self.ax2.clear()
        self.ax2.set_ylim([-10,20])
        self.ax2.set_xlim([0,60])

        self.ax1.plot(self.time_sec, self.u_tot)
        self.ax2.plot(self.time_sec, self.setpoint)
        self.ax2.plot(self.time_sec, self.value)

