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

plots = 4
curvesPerPlot = 3
plotsize = 200
plotsTitle = ["Accelerometer Data","Gyroscope Data","Magnetometer Data","Euler Angles Data"]
curvesName = ["Accel X","Accel Y","Accel Z","Gyro X","Gyro Y","Gyro Z","Mag X","Mag Y","Mag Z","Angles X","Angles Y","Angles Z"]
colors = ["r","g","b"]

plotList = []
curvesList = []
dataSeries = []
bufferData = []

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
        # print(self.gyroData[0])
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
        self.gyroPlot = self.addPlot(title='Gyroscope Data')
        self.gyroPlot.addLegend()
        self.nextRow()
        self.magPlot = self.addPlot(title='Magnetometer Data')
        self.magPlot.addLegend()
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


    # eulerPlot = win.addPlot(title='Euler Angles')

    # while ii < plots:
    #     plotList.append(win.addPlot(title=plotsTitle[ii]))
    #     if ii%2 == 1:
    #         win.nextRow()
    #     plotList[ii].addLegend()
    #     ii +=1



    # ii = 0
    # while jj < curvesPerPlot*plots:
    #     dataSeries.append(np.zeros(plotsize))
    #     curvesList.append(plotList[ii].plot(dataSeries[jj],pen=colors[kk], name=curvesName[jj]))
    #     jj +=1
    #     kk +=1
    #     if jj % curvesPerPlot == 0:
    #         ii +=1
    #     if kk % 3 == 0:
    #         kk = 0
    #     #print "hello"
    # ii = 0
    # jj = 0
    # kk = 0

    # timer = pg.QtCore.QTimer()      # timer used to call the updateGraphs function
    # timer.timebaseout.connect(updateGraphs)
    # timer.start(500)                  # timer restarts every 5ms ( freq = 200 Hz)

    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #     QtGui.QApplication.instance().exec_()
    # ser.close()

timebasestamp = 0
def updateGraphs():      # Function to update new set of data
    global data, accelPlot, timebase, timebasestamp

    gyro = [100, 200, -400]
    accel = [-50, 74, -10]
    timebasestamp += 20000
    eulerAngleData = neb.NebResponsePacket.\
    createEulerAngleResponsePacket(timebasestamp, 20.0, 0.0, -20.0)
    IMUData = neb.NebResponsePacket.\
    createIMUResponsePacket(timebasestamp,accel, gyro)
    data = np.roll(data, 1)
    curve.setData(data)
    print(data)
    # while jj < curvesPerPlot*2:
    #     dataSeries[jj][0] = bufferData[jj]
    #     dataSeries[jj] = np.roll(dataSeries[jj], -1)
    #     curvesList[jj].setData(dataSeries[jj])
    #     jj += 1
    # jj = 0



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    sys.exit(start())
    