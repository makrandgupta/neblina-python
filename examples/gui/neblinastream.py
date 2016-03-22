# Neblina streaming data utility
# (C) 2015 Motsai Research Inc.

streamSerialComm = True
streamBLE = False

import pyqtgraph as pg
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
import comportdialog as cd

import numpy as np
import neblina as neb
import neblinasim as sim
import math
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
import sys
import glob
import time
if streamSerialComm:
    import slip
    import serial.tools.list_ports
elif streamBLE:
    import neblinable as nebble

streamString = '/dev/ttySAF'

class DataThread(QThread):
    """docstring for DataThread"""
    def __init__(self, data, IMUupdateSignal,
                headingWindow, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.data = data
        self.IMUupdateSignal = IMUupdateSignal
        self.headingWindow = headingWindow

    def __del__(self):
        self.exiting = True
        self.wait()

    def run(self):
        while (self.exiting == False):
            self.data.update()
            self.IMUupdateSignal.emit()
            self.headingWindow.setAngle(self.data.headingData, self.data.demoHeading)
            time.sleep(0.02)

class PlottingData(object):
    """docstring Por PlottingData"""
    def __init__(self, arg):
        self.samplingFrequency = 50.0
        self.imuRollIdx = 0
        self.headingRollIdx = 0
        self.numIMUSamples = 1000
        graphSize = 250
        self.timebase = np.arange(0, graphSize)
        self.accelData = [[],[],[]]
        self.gyroData = [[],[],[]]
        self.headingData = 0.0
        self.demoHeading = 0.0

        if(streamBLE):
            packet = ble.getNeblinaPacket()
        else:
            self.imuPackets = sim.createRandomIMUDataPacketList(
                self.samplingFrequency, self.numIMUSamples, 0.5)
            self.eulerAnglePackets = sim.createSpinningObjectPacketList(
                self.samplingFrequency, yawRPS=0.25)

            # Populate the initial IMU data list
            for elem in (packet for idx,packet in enumerate(self.imuPackets) if idx < graphSize):
                # For all three axis
                for idx,axisSample in enumerate(elem.data.accel):
                    # Gyro and Accel have same num of axis
                    self.accelData[idx].append(axisSample)
                    self.gyroData[idx].append(axisSample)
            # Populate the initial euler heading data
            self.headingData = self.eulerAnglePackets[0].data.yaw
            self.demoHeading = self.eulerAnglePackets[0].data.demoHeading

    def update(self):
        # Update all three axis for both accel and gyro
        for idx,axis in enumerate(self.accelData):
            self.accelData[idx] = list(np.roll(self.accelData[idx], 1))
            self.accelData[idx][0] = self.imuPackets[self.imuRollIdx].data.accel[idx]
        for idx,axis in enumerate(self.gyroData):
            self.gyroData[idx] = list(np.roll(self.gyroData[idx], 1))
            self.gyroData[idx][0] = self.imuPackets[self.imuRollIdx].data.gyro[idx]
        # Update euler angle heading
        self.headingData = self.eulerAnglePackets[self.headingRollIdx].data.yaw
        self.demoHeading = self.eulerAnglePackets[self.headingRollIdx].data.demoHeading

        # Wrap around the samples
        self.imuRollIdx += 1    
        self.imuRollIdx %= (self.numIMUSamples)
        self.headingRollIdx += 1
        self.headingRollIdx %= len(self.eulerAnglePackets)

# This window inspired by: https://wiki.python.org/moin/PyQt/Compass%20widget
class HeadingWindow(QWidget):
    angleChangedSignal = pyqtSignal(float, float)
    def __init__(self, parent=None):
        super(HeadingWindow, self).__init__(parent)
        self._angle = 0.0
        self._demoHeading = 0.0
        self._margins = 10
        self._pointText = {0: "N", 45: "NE", 90: "E",
                             135: "SE", 180: "S",
                           225: "SW", 270: "W", 315: "NW"}
     
    def paintEvent(self, event):
        # print('redraw')
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)         
        painter.fillRect(event.rect(), self.palette().brush(QPalette.Window))
        self.drawMarkings(painter)
        self.drawNeedle(painter)
        self.drawDemoNeedle(painter)
        painter.end()

    def drawMarkings(self, painter):
    
        painter.save()
        painter.translate(self.width()/2, self.height()/2)
        scale = min((self.width() - self._margins)/120.0,
                    (self.height() - self._margins)/120.0)
        painter.scale(scale, scale)
        
        font = QFont(self.font())
        font.setPixelSize(10)
        metrics = QFontMetricsF(font)
        
        painter.setFont(font)
        painter.setPen(self.palette().color(QPalette.Shadow))
        
        i = 0
        while i < 360:
            if i % 45 == 0:
                painter.drawLine(0, -40, 0, -50)
                painter.drawText(-metrics.width(self._pointText[i])/2.0, -52,
                                 self._pointText[i])
            else:
                painter.drawLine(0, -45, 0, -50)
            painter.rotate(15)
            i += 15
        
        painter.restore()
    
    def drawNeedle(self, painter):
        painter.save()
        painter.translate(self.width()/2, self.height()/2)
        painter.rotate(self._angle)
        scale = min((self.width() - self._margins)/120.0,
                    (self.height() - self._margins)/120.0)
        painter.scale(scale, scale)
        
        painter.setPen(QPen(1))
        painter.setBrush(self.palette().brush(QPalette.Shadow))
        
        painter.drawPolygon(
            QPolygon([QPoint(-10, 0), QPoint(0, -45), QPoint(10, 0),
                      QPoint(0, 45), QPoint(-10, 0)])
            )
        
        painter.setBrush(self.palette().brush(QPalette.Highlight))
        
        painter.drawPolygon(
            QPolygon([QPoint(-5, -25), QPoint(0, -45), QPoint(5, -25),
                      QPoint(0, -30), QPoint(-5, -25)])
            )
        
        painter.restore()

    def drawDemoNeedle(self, painter):
        painter.save()
        painter.translate(self.width()/2, self.height()/2)
        painter.rotate(self._demoHeading)
        scale = min((self.width() - self._margins)/120.0,
                    (self.height() - self._margins)/120.0)
        painter.scale(scale, scale)
        
        painter.setPen(QPen(1))
        painter.setBrush(self.palette().brush(QPalette.Shadow))
        
        painter.drawPolygon(
            QPolygon([QPoint(-2, 0), QPoint(0, -25), QPoint(2, 0),
                      QPoint(0, 45), QPoint(-2, 0)])
            )
        
        painter.setBrush(self.palette().brush(QPalette.Highlight))
        
        painter.drawPolygon(
            QPolygon([QPoint(-3, -10), QPoint(0, -45), QPoint(3, -10),
                      QPoint(0, -10), QPoint(-3, -10)])
            )
        
        painter.restore()

    
    def sizeHint(self):    
        return QSize(1000, 750)
    
    def angle(self):
        return self._angle

    def demoHeading(self):
        return self._demoHeading

    @pyqtSlot(float)
    def setAngle(self, angle, demoHeading):
        if angle != self._angle:
            self._angle = angle
            self._demoHeading = demoHeading
            self.angleChangedSignal.emit(angle, demoHeading)
            self.update()
    
    angle = pyqtProperty(float, angle, demoHeading, setAngle)




class PlottingWindow(pg.GraphicsWindow):
    """docstring for PlottingGUI"""
    packetReceivedSignal = Signal()
    def __init__(self, plottingData, parent=None):
        super(PlottingWindow, self).__init__(parent)
        self.packetReceivedSignal.connect(self.draw)
        self.data = plottingData
        self.setWindowTitle('Neblina Accel/Gyro')
        self.accelPlot = self.addPlot(title='Accelerometer Data')
        self.accelPlot.addLegend()
        self.nextRow()
        self.gyroPlot = self.addPlot(title='Gyroscope Data')
        self.gyroPlot.addLegend()
        self.nextRow()
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

class StartDialog(QDialog, cd.Ui_Dialog):
    """docstring for StartDialog"""
    def __init__(self, parent=None):
        super(StartDialog, self).__init__(parent)
        self.setupUi(self)
        # self.plottingWindow = plottingWindow
        # self.headingWindow = headingWindow
        self.buttonBox.accepted.connect(self.serialPortSelected)
        self.ports = self.serialPorts()
        for port in self.ports:
            # item.setText(port)
            self.listWidget.addItem(port[0])

    def serialPortSelected(self):
        item = self.listWidget.selectedItems()[0]
        self.thread.serial = item.text()
        self.w1.show()
        self.w2.show()
        self.w1.raise_() # Raise instance on top of window stack
        self.w1.resize(500,500)
        self.w2.raise_() # Raise instance on top of window stack
        self.w2.move(1000,0)
        self.thread.start()

    def serialPorts(self):
        ports = list(serial.tools.list_ports.comports())
        return ports


    # drawThread = DrawingThread(plottingWindow)

    
    # Start the threads
    # drawThread.start()

def start():
    # here you can argparse your CLI arguments, so you can choose
    # your interface (readline, ncurses, Qt, web, whatever...?)
    # and setup your application (logfile, port to bind to, look 
    # of the GUI...)

    plottingApplication = QApplication(sys.argv) # create application

    # comPortDialog = uic.loadUi("./ui/comportdialog.ui")

    data = PlottingData(1)
    plottingWindow = PlottingWindow(data) # Create the instance of the plotting window
    headingWindow = HeadingWindow() # Create the instance of the heading window
    dataWorkerThread = DataThread(data, plottingWindow.packetReceivedSignal, headingWindow)
    if streamSerialComm:
        dialog = StartDialog()
        dialog.w1 = plottingWindow
        dialog.w2 = headingWindow
        dialog.thread = dataWorkerThread
        dialog.show()
    elif streamBLE:
        # Show windows
        plottingWindow.raise_() # Raise instance on top of window stack
        plottingWindow.resize(500,500)
        headingWindow.raise_() # Raise instance on top of window stack
        headingWindow.move(500,0)
        plottingWindow.show() # Make the instance visible
        headingWindow.show() # Make the instance visible
        dataWorkerThread.start()
        
    plottingApplication.exec_()



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    sys.exit(start())
    
