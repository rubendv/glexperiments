#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2010 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################


import sys
import math
import numpy as np

from PyQt4 import QtCore, QtGui, QtOpenGL

try:
    from OpenGL.GL import *
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL hellogl",
            "PyOpenGL must be installed to run this example.")
    sys.exit(1)

def create_program():
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader, """
    #version 330

    in vec2 vPosition;
    out vec2 fPosition;

    void main() {
        fPosition = vPosition;
        gl_Position = vec4(vPosition, 0.0, 1.0);
    }
    """)
    glCompileShader(vertex_shader)
    print glGetShaderInfoLog(vertex_shader)
    
    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, """
    #version 330
    
    in vec2 fPosition;
    out vec4 fColor;
    
    void main() {
        vec4 colors[4] = vec4[](vec4(1.0, 0.0, 0.0, 1.0), vec4(0.0, 1.0, 0.0, 1.0), vec4(0.0, 0.0, 1.0, 1.0), vec4(0.0, 0.0, 0.0, 1.0));
        fColor = vec4(1.0);
        for(int row = 0; row < 2; row++) {
            for(int col = 0; col < 2; col++) {
                float dist = distance(fPosition, vec2(-0.50 + col, 0.50 - row));
                float delta = fwidth(dist);
                float alpha = smoothstep(0.45-delta, 0.45, dist);
                fColor = mix(colors[row*2+col], fColor, alpha);
            }
        }
    }
    """)
    glCompileShader(fragment_shader)
    print glGetShaderInfoLog(fragment_shader)

    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    print glGetProgramInfoLog(program)
    return program

class Window(QtGui.QWidget):
    def __init__(self):
        super(Window, self).__init__()

        self.glWidget = GLWidget()

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        self.setLayout(mainLayout)
        self.setWindowTitle("Hello GL")

class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)
    def sizeHint(self):
        return QtCore.QSize(400, 400)
    def initializeGL(self):
        self.program = create_program()
        self.vertex_array = glGenVertexArrays(1)
        glBindVertexArray(self.vertex_array)
        
        vertices = np.array([
            [ -1.0, -1.0 ],
            [  1.0, -1.0 ],
            [ -1.0,  1.0 ],
            [  1.0, -1.0 ],
            [  1.0,  1.0 ],
            [ -1.0,  1.0 ]
        ], dtype=np.float32)
        
        self.buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glUseProgram(self.program)
        vPosition = glGetAttribLocation(self.program, "vPosition")
        glVertexAttribPointer(vPosition, 2, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(vPosition)
        print "Using OpenGL version", glGetString(GL_VERSION)
    def paintGL(self):
        print "Drawing"
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glBindVertexArray(self.vertex_array)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glFlush()
        self.grabFrameBuffer().save("screenshot.png", "png")
    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return
        glViewport((width - side) / 2, (height - side) / 2, side, side)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
