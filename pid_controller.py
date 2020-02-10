
import pdb #debugger

from time import time, ctime

class PID_controller:


    def __init__(self, reg_name, log_results=False):

        self.name = reg_name
        self.log_results = log_results

        self.Kp = 0.0 #proportional gain
        self.Ti = 0.0 #integral gain
        self.Td = 0.0 #derivative gain
        self.Nd = 0.0 #derivative filter value
        self.Ts = 0.0 #samplings time

        self.setpoint = 0
        self.error = 0

        self.u_p = 0
        self.u_i = 0
        self.u_d = 0
        self.u_tot = 0

        # feedback value:
        self.value = 0
        self.value_prev = 0

        self.time_now = time()
        self.time_prev = 0

    def get_reg_name(self):
        return self.name

    # Write a log with results from the regulator
    def writer(self, data):
         file = open(self.name+'_log.txt', 'a')

         for i in data:
             file.write(str(i))
             file.write('|')
         file.write('\n')

         file.close()


    def update_parameters(self, Kp, Ti, Td, Nd):
        self.Kp = Kp #proportional gain
        self.Ti = Ti #integral gain
        self.Td = Td #derivative gain
        self.Nd = Nd #derivative filter value
    
    def update_value(self, value):
        self.value_prev = self.value
        self.value = round(value,2)
        self.calculate_u_tot()

    def update_setpoint(self, setpoint):
        self.setpoint = round(setpoint,2)
        self.calculate_u_tot()

    def get_sample_time(self):
        self.time_prev = self.time_now
        self.time_now = time()

        self.Ts = self.time_now - self.time_prev

    # proportional part
    def proportional(self):
        u_p = self.Kp * self.error
        u_p = round(u_p,2)
        self.u_p = u_p

    # intagral part
    def integral(self):
        try:
            u_i = self.Kp * self.Ts / self.Ti * self.error + self.u_i
            u_i = round(u_i,2)

            # anti windup:
            if u_i > 100.0:
                self.u_i = 100.0
            elif u_i < 0.0:
                self.u_i = 0.0

        except ZeroDivisionError:
            self.u_i = 0.00


    # derivative part
    def derivative(self):
        try:
            beta = self.Td / (self.Td + self.Ts * self.Nd)
            u_d = beta*self.u_d - (self.Kp * self.Td / self.Ts) * (1-beta) * (self.value-self.value_prev)
            self.u_d = u_d
            u_d = round(u_d,2)
        except ZeroDivisionError:
            self.u_d = 0.00
            
    # calculate error
    def get_error(self):
        error = self.setpoint - self.value
        error = round(error,2)
        self.error = error

    def calculate_u_tot(self):
        self.get_sample_time()
        self.get_error()

        #calculate proportional, integral and derivative "pådrag"
        self.proportional()
        self.integral()
        self.derivative()

        self.u_tot = self.u_p + self.u_i + self.u_d
        self.u_tot = round(self.u_tot, 2)

        # anti windup:
        # if self.u_tot > 100.0:
        #     self.u_tot = 100.0
        # elif self.u_tot < 0.0:
        #     self.u_tot = 0.0

        results = [ctime(), self.value, self.setpoint, self.u_tot, self.u_p, self.u_i, self.u_d, self.Kp, self.Ti, self.Td, self.Nd]

        # log results if the optiion is on - default = FALSE
        if self.log_results:
            self.writer(results)

        return results
        


import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style, dates
import numpy as np

class LivePIDPlotter:
    def __init__(self, regulator, xrange, vars_to_plot=[], plot_interval = 1):
        self.regulator = regulator
        self.plot_interval = plot_interval
        self.xrange = xrange / 1440 # convert to time in matplotlib format
        self.vars_to_plot = vars_to_plot

        #dictionary with variables that can be ploted
        self.index = {"messurment" : [], "setpoint" : [], "u_tot" : [], "u_p" : [], "u_i" : [], "u_d" : [], "Kp" : [], "Ti" : [], "Td" : [], "N" : []}
        self.xtime = []

        #create empty plots
        self.fig = plt.figure()
        if ("u_tot" or "u_p" or "u_i" or "u_d") in self.vars_to_plot:
            self.ax1 = self.fig.add_subplot(2,1,1)
            self.ax2 = self.fig.add_subplot(2,1,2)
            self.ax1.grid()
            self.ax2.grid()
        else:
            self.ax1 = self.fig.add_subplot(1,1,1)

        # create graph for each variable
        self.lines = []

        for d in self.vars_to_plot:
            if d == ("u_tot" or "u_p" or "u_i" or "u_d"):
                line, = self.ax2.plot_date([], [], 'o-')
                self.lines.append(line)
            else:
                line, = self.ax1.plot_date([], [], 'o-')
                self.lines.append(line)

        # change graph style
        style.use('fivethirtyeight')


    def get_data(self):
        data = np.genfromtxt(self.regulator.name+'_log.txt', delimiter='|', usecols=range(1,11))
        self.xtime = np.genfromtxt(self.regulator.name+'_log.txt', delimiter='|', dtype='str', usecols=0)
        self.xtime = dates.datestr2num(self.xtime) #convert to matplotlib date format
        j = 0
        for i in self.index:
            self.index[i] = data[:, j]
            j += 1

    def plotter(self, o): #xrange in min
        self.get_data()

        self.fig.autofmt_xdate()

        if ("u_tot" or "u_p" or "u_i" or "u_d") in self.vars_to_plot:
            self.ax1.xaxis.set_major_formatter(dates.DateFormatter('%d.%m %H:%M'))
            self.ax1.set_xlim([self.xtime[-1]-self.xrange, self.xtime[-1]])
            self.ax1.set_ylim([-10,50])

            self.ax2.xaxis.set_major_formatter(dates.DateFormatter('%d.%m %H:%M'))
            self.ax2.set_xlim([self.xtime[-1]-self.xrange, self.xtime[-1]])
            self.ax2.set_ylim([0,100])
        else:
            self.ax1.xaxis.set_major_formatter(dates.DateFormatter('%d.%m %H:%M'))
            self.ax1.set_xlim([self.xtime[-1]-self.xrange, self.xtime[-1]])
            self.ax1.set_ylim([-10,50])



        x = self.xtime
        y = []

        for i,d in enumerate(self.vars_to_plot):
            y = self.index[d]
            self.lines[i].set_data(x,y)

        return self.lines

    def run(self):
        ani = animation.FuncAnimation(self.fig, self.plotter, interval = self.plot_interval*1000)
        plt.show()




        







