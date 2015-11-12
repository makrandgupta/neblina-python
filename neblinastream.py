import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import neblina as neb
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

timebase = [0,1,2,3,4,5,6,7,8]
data = [1,3,22,5,8,4,16,4,7]
curve = None

class PlottingData(object):
    """docstring Por PlottingData"""
    def __init__(self, arg):
        self.arg = arg

    def setup(self):
        pass

class PlottingWindow(pg.GraphicsWindow):
    """docstring for PlottingGUI"""
    def __init__(self, plottingData, parent=None):
        super(PlottingWindow, self).__init__(parent)
        self.plottingData = plottingData
        self.setWindowTitle('Neblina Data Plots')

    def main_loop(self):
        # wait for the UI to cease
        pass
        # return self.app.exec_()

def start():
    # here you can argparse your CLI arguments, so you can choose
    # your interface (readline, ncurses, Qt, web, whatever...?)
    # and setup your application (logfile, port to bind to, look 
    # of the GUI...)

    data = PlottingData(1)
    data.setup()

    plottingApplication = QtGui.QApplication(sys.argv) # create application
    plottingWindow = PlottingWindow(data) # Create the instance of the window

    # win.setWindowTitle('Neblina Data Plots')
    # accelPlot = win.addPlot(title='Accelerometer Data')
    # accelPlot.addLegend()
    # gyroPlot = win.addPlot(title='Gyroscope Data')
    # gyroPlot.addLegend()
    # win.nextRow()
    # magPlot = win.addPlot(title='Magnetometer Data')
    # magPlot.addLegend()
    # curve = accelPlot.plot(timebase, data, pen='b', name='X')
    # accelPlot.plot(timebase, [9,8,7,6,5,4,3,2,1], pen='g', name='Y')
    # accelPlot.plot(timebase, [9,8,7,6,5,4,3,2,1], pen='r', name='Z')
    # gyroPlot.plot(timebase, [9,8,7,6,5,4,3,2,1], pen='b', name='X')
    # gyroPlot.plot(timebase, [9,8,7,6,5,4,3,2,1], pen='g', name='Y')
    # gyroPlot.plot(timebase, [9,8,7,6,5,4,3,2,1], pen='r', name='Z')

    plottingWindow.show() # Make the instance visible
    plottingWindow.raise_() # Raise instance on top of window stack
    plottingApplication.exec_()

    # PlottingGUI(data).main_loop()


    # global curve, timebase
    # ii = 0
    # jj = 0
    # kk = 0
    # win = pg.GraphicsWindow()
    # win.setWindowTitle('Neblina Data Plots')

    # accelPlot = win.addPlot(title='Accelerometer Data')
    # accelPlot.addLegend()

    # gyroPlot = win.addPlot(title='Gyroscope Data')
    # gyroPlot.addLegend()
    # win.nextRow()
    # magPlot = win.addPlot(title='Magnetometer Data')
    # magPlot.addLegend()
    # curve = accelPlot.plot(timebase, data, pen='b', name='X')
    # accelPlot.plot(timebase, [9,8,7,6,5,4,3,2,1], pen='g', name='Y')
    # accelPlot.plot(timebase, [9,8,7,6,5,4,3,2,1], pen='r', name='Z')

    # gyroPlot.plot(timebase, [9,8,7,6,5,4,3,2,1], pen='b', name='X')
    # gyroPlot.plot(timebase, [9,8,7,6,5,4,3,2,1], pen='g', name='Y')
    # gyroPlot.plot(timebase, [9,8,7,6,5,4,3,2,1], pen='r', name='Z')

    # while True:
    #     print()


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
    