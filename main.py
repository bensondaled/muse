"""
muse-io --device Muse-550F --osc osc.udp://127.0.0.1:5000 --osc-timestamp 
"""
##

import argparse
import numpy as np
import matplotlib.pyplot as pl
import threading
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server

ADDRESS = '127.0.0.1'
PORT = 5000

class Muse():
    def __init__(self):

        # ui
        fig,axs = pl.subplots(2,1)
        buffer_size = 200
        ax_acc, ax_eeg = axs
        ax_acc.set_ylim([-2000,2000])
        ax_acc.set_xlim([0, buffer_size])
        ax_eeg.set_ylim([0, 1700])
        ax_eeg.set_xlim([0, buffer_size])
        self.data_acc = np.zeros([buffer_size, 3])
        self.data_eeg = np.zeros([buffer_size, 4])
        self.data_acc[:] = np.nan
        self.data_eeg[:] = np.nan
        self.lines_acc = ax_acc.plot(self.data_acc)
        self.lines_eeg = ax_eeg.plot(self.data_eeg)
        self.is_updating = True
        fig.canvas.mpl_connect('close_event', self.stop_updating)

        parser = argparse.ArgumentParser()
        parser.add_argument("--ip", default=ADDRESS)
        parser.add_argument("--port", type=int, default=PORT)
        self.args = parser.parse_args()

        self.dispatcher = Dispatcher()
        self.dispatcher.map("/debug", print)
        self.dispatcher.map("/muse/eeg", self.eeg_handler)
        self.dispatcher.map("/muse/acc", self.acc_handler)
        
        threading.Thread(target=self.begin_server).start()
        self.disp()

    def begin_server(self):
        server = osc_server.ThreadingOSCUDPServer((self.args.ip, self.args.port), self.dispatcher)
        server.serve_forever()

    def stop_updating(self, *args):
        self.is_updating = False

    def eeg_handler(self, src, ch1, ch2, ch3, ch4, secs, usecs):
        self.data_eeg = np.roll(self.data_eeg, -1, axis=0)
        self.data_eeg[-1,:] = [ch1,ch2,ch3,ch4]

    def acc_handler(self, src, x, y, z, secs, usecs):
        self.data_acc = np.roll(self.data_acc, -1, axis=0)
        self.data_acc[-1,:] = [x,y,z]

    def disp(self):
        while True:
            pl.pause(0.001)
            if not self.is_updating:
                return
            for d,l in zip(self.data_acc.T, self.lines_acc):
                l.set_ydata(d)
            for d,l in zip(self.data_eeg.T, self.lines_eeg):
                l.set_ydata(d)
            pl.draw()

if __name__ == '__main__':
    m = Muse()


##
