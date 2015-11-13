import pyqtgraph as pg
from PyQt4 import QtCore, QtGui
import numpy as np
import neblina as neb
import neblinasim as sim
import math
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
import sys
import time

class DataThread(QtCore.QThread):
    """docstring for DataThread"""
    def __init__(self, data, updateSignal, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False
        self.data = data
        self.updateSignal = updateSignal

    def __del__(self):
        self.exiting = True
        self.wait()

    def run(self):
        while (self.exiting == False):
            self.data.update()
            self.updateSignal.emit()
            time.sleep(0.02)

class PlottingData(object):
    """docstring Por PlottingData"""
    def __init__(self, arg):
        self.rollIdx = 0
        self.numSamples = 300
        graphSize = 100
        self.timebase = np.arange(0, graphSize)
        self.accelData = [[],[],[]]
        self.gyroData = [[],[],[]]
        self.imuPackets = sim.createRandomIMUDataPacketList(50.0, self.numSamples)
        for elem in (packet for idx,packet in enumerate(self.imuPackets) if idx < graphSize):
            # For all three axis
            for idx,axisSample in enumerate(elem.data.accel):
                # Gyro and Accel have same num of axis
                self.accelData[idx].append(axisSample)
                self.gyroData[idx].append(axisSample)

    def update(self):
        # Update all three axis for both accel and gyro
        for idx,axis in enumerate(self.accelData):
            self.accelData[idx] = list(np.roll(self.accelData[idx], 1))
            self.accelData[idx][0] = self.imuPackets[self.rollIdx].data.accel[idx]
        for idx,axis in enumerate(self.gyroData):
            self.gyroData[idx] = list(np.roll(self.gyroData[idx], 1))
            self.gyroData[idx][0] = self.imuPackets[self.rollIdx].data.gyro[idx]
        # Wrap around the samples
        self.rollIdx += 1
        self.rollIdx %= (self.numSamples)
        

class PlottingWindow(pg.GraphicsWindow):
    """docstring for PlottingGUI"""
    packetReceivedSignal = QtCore.Signal()
    def __init__(self, plottingData, parent=None):
        super(PlottingWindow, self).__init__(parent)
        self.packetReceivedSignal.connect(self.draw)
        self.data = plottingData
        self.setWindowTitle('Neblina Data Plots')
        self.accelPlot = self.addPlot(title='Accelerometer Data')
        self.accelPlot.addLegend()
        self.nextRow()
        self.gyroPlot = self.addPlot(title='Gyroscope Data')
        self.gyroPlot.addLegend()
        self.nextRow()
        # self.magPlot = self.addPlot(title='Magnetometer Data')
        # self.magPlot.addLegend()
        self.accelXCurve = self.accelPlot.plot(self.data.timebase, self.data.accelData[0], pen='b', name='X')
        self.accelYCurve = self.accelPlot.plot(self.data.timebase, self.data.accelData[1], pen='g', name='Y')
        self.accelZCurve = self.accelPlot.plot(self.data.timebase, self.data.accelData[2], pen='r', name='Z')
        self.gyroXCurve = self.gyroPlot.plot(self.data.timebase, self.data.gyroData[0], pen='b', name='X')
        self.gyroYCurve = self.gyroPlot.plot(self.data.timebase, self.data.gyroData[1], pen='g', name='Y')
        self.gyroZCurve = self.gyroPlot.plot(self.data.timebase, self.data.gyroData[2], pen='r', name='Z')

    def draw(self):
        # print('redraw')
        self.accelXCurve.setData(self.data.accelData[0])
        self.accelYCurve.setData(self.data.accelData[1])
        self.accelZCurve.setData(self.data.accelData[2])
        self.gyroXCurve.setData(self.data.gyroData[0])
        self.gyroYCurve.setData(self.data.gyroData[1])
        self.gyroZCurve.setData(self.data.gyroData[2])

def start():
    # here you can argparse your CLI arguments, so you can choose
    # your interface (readline, ncurses, Qt, web, whatever...?)
    # and setup your application (logfile, port to bind to, look 
    # of the GUI...)

    data = PlottingData(1)
    plottingApplication = QtGui.QApplication(sys.argv) # create application
    plottingWindow = PlottingWindow(data) # Create the instance of the window

    dataWorkerThread = DataThread(data, plottingWindow.packetReceivedSignal)
    # drawThread = DrawingThread(plottingWindow)

    # Show windows
    plottingWindow.show() # Make the instance visible
    plottingWindow.raise_() # Raise instance on top of window stack
    
    # Start the threads
    # drawThread.start()
    dataWorkerThread.start()
    plottingApplication.exec_()

    # timer = pg.QtCore.QTimer()      # timer used to call the updateGraphs function
    # timer.timebaseout.connect(updateGraphs)
    # timer.start(500)                  # timer restarts every 5ms ( freq = 200 Hz)

    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #     QtGui.QApplication.instance().exec_()
    # ser.close()


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    sys.exit(start())
    