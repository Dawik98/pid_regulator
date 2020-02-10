import pdb #debugger

from threading import Thread, Timer
from time import time, ctime

from pid_controller import PID_controller, LivePIDPlotter
from plotter import Live_Plotter

# run pid each 1sec
wait_time = 1

temp_reg = PID_controller('temp_reg1', log_results=True)
temp_reg.update_parameters(1.0, 1.0, 1.0, 0.0)
temp_reg.update_value(2.0)
temp_reg.update_setpoint(5.0)


def run():
    temp_reg.calculate_u_tot()
    # pdb.set_trace() #breakpoint

    Timer(wait_time, run).start()

run()

plotter = LivePIDPlotter(temp_reg, 1, ["messurment", "setpoint", "u_tot"], plot_interval=0.1)
plotter.run()