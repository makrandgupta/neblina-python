#!/usr/bin/env python
###################################################################################
#
# Copyright (c)     2010-2016   Motsai
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
###################################################################################

import time
from PIL import Image

from bluepy.btle import *

from PyQt5.QtCore import (pyqtSignal)
from PyQt5.QtGui import (QSurfaceFormat, QOpenGLVersionProfile)
from PyQt5.QtWidgets import (QApplication, QOpenGLWidget, QMainWindow)

from neblina import *
from neblinaCommandPacket import NebCommandPacket
from neblinaError import *
from neblinaResponsePacket import NebResponsePacket

###################################################################################

NeblinaDeviceAddress = "EE:58:9A:81:0B:80"

NeblinaServiceUUID = "0DF9F021-1532-11E5-8960-0002A5D5C51B"
CtrlUUID = "0DF9F023-1532-11E5-8960-0002A5D5C51B"
DataUUID = "0DF9F022-1532-11E5-8960-0002A5D5C51B"

###################################################################################


class NeblinaDelegate(DefaultDelegate):
    def __init__(self, params, glWidget):
        DefaultDelegate.__init__(self)
        self.name = params
        self.glWidget = glWidget

    def handleNotification(self, cHandle, data):
        angle=[0]*3
        try:
            nebPacket = NebResponsePacket(data)
            angle[0] = nebPacket.data.yaw
            angle[1] = nebPacket.data.pitch
            angle[2] = nebPacket.data.roll
        except KeyError as e:
            print("KeyError : " + str(e))
        except NotImplementedError as e:
            print("NotImplementedError : " + str(e))
        except CRCError as e:
            print("CRCError : " + str(e))
        except InvalidPacketFormatError as e:
            print("InvalidPacketFormatError : " + str(e))

        self.glWidget.setAngle(angle)
        #print("Yaw : {0}, Pitch : {1}, Roll : {2}".format(angle[0], angle[1], angle[2]))


###################################################################################


class neblinaBLE(object):

    def __init__(self, glWidget):
        print("Connect to peripheral.")
        self.periph = Peripheral(NeblinaDeviceAddress,"random")

        print("Setup delegate.")
        self.periph.setDelegate(NeblinaDelegate('Neblina', glWidget))

        print("Printing services.")
        services = list(self.periph.getServices())
        for x in range(1, len(services)):
            print(str(services[x]))

        self.commandSend = False

        self.service = self.periph.getServiceByUUID(NeblinaServiceUUID)
        self.writeCharacteristic = self.service.getCharacteristics(CtrlUUID)[0]
        self.readCharacteristic = self.service.getCharacteristics(DataUUID)[0]

    def startStream(self):
        command = NebCommandPacket(SubSystem.Motion, Commands.Motion.EulerAngle, True)
        commandString = command.stringEncode()
        self.writeCharacteristic.write(commandString)

        # Setup notification
        self.periph.writeCharacteristic(self.readCharacteristic.handle+2, struct.pack('<bb', 0x01, 0x00))

    def waitForNotifications(self):
        self.periph.waitForNotifications(1.0)

    def getEulerAngles(self):
        try:
            angle = [0]*3

            if not self.commandSend:
                self.commandSend = True
                command = NebCommandPacket(SubSystem.Motion, Commands.Motion.EulerAngle, True)
                commandString = command.stringEncode()
                self.writeCharacteristic.write(commandString)

                # Setup notification
                self.periph.writeCharacteristic(self.readCharacteristic.handle+2, struct.pack('<bb', 0x01, 0x00))


            if not self.periph.waitForNotifications(1.0):
                print("Failed to notify")

            return angle

        except BTLEException as e:
            print("BTLEException : " + str(e))
            self.periph.disconnect()

        return None

###################################################################################


class ModelOBJ:

    def __init__(self, filename, glContext):
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []

        material = None
        for line in open(filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = list(map(float, values[1:4]))
                self.vertices.append(v)
            elif values[0] == 'vn':
                v = list(map(float, values[1:4]))
                self.normals.append(v)
            elif values[0] == 'vt':
                self.texcoords.append(list(map(float, values[1:3])))
            elif values[0] in ('usemtl', 'usemat'):
                material = values[1]
            elif values[0] == 'mtllib':
                self.material = self.MTL(values[1], glContext)
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        texcoords.append(int(w[1]))
                    else:
                        texcoords.append(0)
                    if len(w) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        norms.append(0)
                self.faces.append((face, norms, texcoords, material))

    def MTL(self, filename, glContext):
        contents = {}
        mtl = None
        filename = os.path.join( os.path.dirname( __file__ ), "FA-22_Raptor",filename )
        for line in open(filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'newmtl':
                mtl = contents[values[1]] = {}
            elif mtl is None:
                raise(ValueError, "mtl file doesn't start with newmtl stmt")
            elif values[0] == 'map_Kd':
                # load the texture referred to by this declaration
                mtl[values[0]] = values[1]
                path = os.path.join( os.path.dirname( __file__ ), "FA-22_Raptor", mtl['map_Kd'] )
                surf = Image.open(path)
                image =  surf.tobytes()
                ix, iy = surf.size
                texid = mtl['texture_Kd'] = glContext.glGenTextures(1)
                glContext.glBindTexture(glContext.GL_TEXTURE_2D, texid)
                glContext.glTexParameteri(glContext.GL_TEXTURE_2D, glContext.GL_TEXTURE_MIN_FILTER,
                    glContext.GL_LINEAR)
                glContext.glTexParameteri(glContext.GL_TEXTURE_2D, glContext.GL_TEXTURE_MAG_FILTER,
                    glContext.GL_LINEAR)
                glContext.glTexImage2D(glContext.GL_TEXTURE_2D, 0, glContext.GL_RGBA, ix, iy, 0, glContext.GL_RGBA,
                    glContext.GL_UNSIGNED_BYTE, image)
            else:
                mtl[values[0]] = map(float, values[1:])
        return contents

###################################################################################


class GLWidget(QOpenGLWidget):
    eulerAngleReceived = pyqtSignal(float, float, float)

    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.eulerAngleReceived.connect(self.receivedAngle)

        self.xRot = 0
        self.yRot = 0
        self.zRot = 0

    def initializeGL(self):
        profile = QOpenGLVersionProfile()
        profile.setVersion(2, 0)
        profile.setProfile(QSurfaceFormat.CompatibilityProfile)

        self.gl = self.context().versionFunctions(profile)
        self.gl.initializeOpenGLFunctions()

        self.obj = ModelOBJ("/home/souellet/motsai/neblina-python/examples/gui/FA-22_Raptor/FA-22_Raptor.obj", self.gl)

        self.gl.glClearDepth(1.0)
        self.gl.glEnable(self.gl.GL_DEPTH_TEST)
        self.gl.glDepthFunc(self.gl.GL_LEQUAL)
        self.gl.glShadeModel(self.gl.GL_SMOOTH)
        self.gl.glHint(self.gl.GL_PERSPECTIVE_CORRECTION_HINT, self.gl.GL_NICEST)

        # Load model
        self.list = self.gl.glGenLists(1)
        self.gl.glNewList(self.list, self.gl.GL_COMPILE)
        self.gl.glEnable(self.gl.GL_TEXTURE_2D)
        self.gl.glFrontFace(self.gl.GL_CCW)
        for face in self.obj.faces:
            vertices, normals, texture_coords, material = face

            mtl = self.obj.material[material]
            if 'texture_Kd' in mtl:
                # use diffuse texmap
                self.gl.glBindTexture(self.gl.GL_TEXTURE_2D, mtl['texture_Kd'])
            else:
                # just use diffuse colour
                self.gl.glColor(*mtl['Kd'])

            self.gl.glBegin(self.gl.GL_POLYGON)
            for i in range(len(vertices)):
                if normals[i] > 0:
                    self.gl.glNormal3fv(self.obj.normals[normals[i] - 1])
                if texture_coords[i] > 0:
                    self.gl.glTexCoord2fv(self.obj.texcoords[texture_coords[i] - 1])
                self.gl.glVertex3fv(self.obj.vertices[vertices[i] - 1])
            self.gl.glEnd()
        self.gl.glDisable(self.gl.GL_TEXTURE_2D)
        self.gl.glEndList()


        self.gl.glEnable(self.gl.GL_NORMALIZE)
        self.gl.glClearColor(0.0, 0.0, 0.0, 1.0)

    def paintGL(self):
        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)
        self.gl.glMatrixMode(self.gl.GL_MODELVIEW)

        self.gl.glLoadIdentity()
        self.gl.glRotated(self.xRot, 1.0, 0.0, 0.0)
        self.gl.glRotated(self.yRot, 0.0, 1.0, 0.0)
        self.gl.glRotated(self.zRot, 0.0, 0.0, 1.0)

        self.gl.glPushMatrix()
        self.gl.glCallList(self.list)
        self.gl.glPopMatrix()

    def resizeGL(self, width, height):
        aspect = width / height
        side = min(width, height)
        self.gl.glViewport((width - side) / 2, (height - side) / 2, side, side)

        threshold = 100
        self.gl.glMatrixMode(self.gl.GL_PROJECTION)
        self.gl.glLoadIdentity()
        self.gl.glOrtho(-width / threshold, width / threshold, -height / threshold, height / threshold, -20.0, 60.0)

        self.gl.glMatrixMode(self.gl.GL_MODELVIEW)
        self.gl.glLoadIdentity()
        self.gl.glTranslated(0.0, 0.0, 00.0)

    def setAngle(self, angle):
        self.eulerAngleReceived.emit(angle[0], angle[1], angle[2])

    def receivedAngle(self, yaw, pitch, roll):
        print("Yaw : {0}, Pitch : {1}, Roll : {2}".format(yaw, pitch, roll))
        self.yRot = -yaw
        self.xRot = pitch
        self.zRot = -roll
        self.update()

###################################################################################


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.glWidget = GLWidget()
        self.setCentralWidget(self.glWidget)

        self.resize(640, 640)


    def getGLWidget(self):
        return self.glWidget

###################################################################################

def main(argv):

    app = QApplication(argv)
    mainWin = MainWindow()

    ble = neblinaBLE(mainWin.getGLWidget())
    ble.startStream()

    mainWin.show()

    while True:
        app.processEvents()
        ble.waitForNotifications()


    sys.exit(app.exec_())

    # print("Infinite loop.")
    # while True:
    #     angles = ble.getEulerAngles()
    #     #print("Yaw : {0}, Pitch : {1}, Roll : {2}".format(angles[0], angles[1], angles[2]))
    #
    #     #time.sleep(1)



###################################################################################


if __name__ == "__main__":
    main(sys.argv)

