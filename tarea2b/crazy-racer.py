# coding=utf-8
"""
Daniel Calderon, CC3501, 2019-2
Showing lighting effects: Flat, Gauraud and Phong
"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys

import modulos.transformations as tr
import modulos.basic_shapes as bs
import modulos.easy_shaders as es
import modulos.lighting_shaders as ls
import modulos.scene_graph as sg
import modulos.ex_curves as cu

def normalizar(vector):
    modulo=(vector[0][0]**2+vector[1][0]**2+vector[2][0]**2)**(1/2)
    if modulo==0:return
    vector=np.multiply(vector,1/modulo)
    return vector

def velocidad(P0,P1,P2):
    a=((P0[0][0] - P2[0][0]) ** 2 + (P0[1][0] - P2[1][0]) ** 2) ** (1 / 2)
    b = ((P0[0][0] - P1[0][0]) ** 2 + (P0[1][0] - P1[1][0]) ** 2 ) ** (1 / 2)
    c = ((P2[0][0] - P1[0][0]) ** 2 + (P2[1][0] - P1[1][0]) ** 2 ) ** (1 / 2)
    traslacion=P0
    P2=np.subtract(P2,P1)
    z2=P2[2][0]
    P2[2][0]=0
    P0=np.subtract(P0,P1)
    z0=P0[2][0]
    P0[2][0]=0
    P1=np.array([[0,0,0]]).T


    alfa=np.arccos((b**2+c**2-a**2)/(2*b*c))
    if -0.001<alfa-np.pi<0.001:
        velocidad=normalizar(np.array([[P2[0][0]-P0[0][0],P2[1][0]-P0[1][0],0]]).T)
        velocidad[2][0]=(z2-z0)/2
        return velocidad
    alfa/=2
    rotacion=np.array([[np.cos(alfa),-np.sin(alfa),0],[np.sin(alfa),np.cos(alfa),0],[0,0,1]])
    bisectriz=np.matmul(rotacion,P2)
    x=P2[0][0]
    if x==0:
        if traslacion[0][0]>0:x-=0.1
        else:x+=0.1
    if bisectriz[0][0]==0 :
        y=0
    if bisectriz[1][0]==0:
     y=P2[1][0]
     x=0
    if bisectriz[0][0]!=0 and bisectriz[1][0]!=0:
        y = (-bisectriz[0][0] * x) / bisectriz[1][0]
    velocidad=np.array([[x,y,(z2-z0)/2]]).T
    if (P2[0][0]-P0[0][0])*velocidad[0][0]<0:velocidad[0][0]*=-1
    if (P2[1][0] - P0[1][0]) * velocidad[1][0] < 0: velocidad[1][0] *= -1
    return normalizar(velocidad)


#puntos=[np.array([[-0.5,-1,0]]).T,np.array([[0,-2,0]]).T,np.array([[0.5,-1,0.3]]).T,np.array([[0.5,0.3,0]]).T,np.array([[0.5,1,0]]).T,np.array([[0,1.5,0.2]]).T,np.array([[-0.5,1,0]]).T,np.array([[-1.7,0,0]]).T,np.array([[-1,-0.3,0]]).T]
puntos=[np.array([[-0.5,-1,0]]).T,np.array([[0,-2,0]]).T,np.array([[0.5,-1,0.3]]).T,np.array([[0.5,0.3,0]]).T,np.array([[0.5,1,0]]).T,np.array([[0,1.5,0.2]]).T,np.array([[-0.5,4,0]]).T,np.array([[-2,5,0.3]]).T,np.array([[-4,5,0]]).T,np.array([[-3,3,0]]).T,np.array([[-1,0,0]]).T]
puntos2=[]
for i in range(len(puntos)):
    if i==0:
        v1=velocidad(puntos[len(puntos)-1],puntos[0],puntos[1])
    if i==len(puntos)-1:
        v1 = velocidad(puntos[i-1], puntos[i], puntos[0])
    elif i!=0:
        v1=velocidad(puntos[i-1], puntos[i], puntos[i+1])
    v1[2][0]=0
    x = 1
    if v1[0][0] == 0:
        y = 0
    if v1[1][0] == 0:
        y = 1
        x = 0
    if v1[0][0] != 0 and v1[1][0] != 0:
        y = (-v1[0][0] * x) / v1[1][0]
    v2 = normalizar(np.array([[x, y, 0]]).T)
    if np.cross(v1.T, v2.T)[0][2] > 0:
        v2 = -v2
    x = puntos[i][0][0] + v2[0][0]
    y = puntos[i][1][0] + v2[1][0]
    puntos2.append(np.array([[x,y,puntos[i][2][0]]]).T)

def crearSubcurvas(puntos):
 subcurvas=[]
 for i in range(len(puntos)):
    if i==0:
        P1=puntos[i]
        P2=puntos[i+1]
        v1=velocidad(puntos[len(puntos)-1],P1,P2)
        v2=velocidad(P1,P2,puntos[i+2])
        Gmb = cu.hermiteMatrix(P1, P2, v1, v2)
        # funcion que genera la spline de catmull-rom
        distancia=((puntos[i][0][0]-puntos[i+1][0][0])**2+(puntos[i][1][0]-puntos[i+1][1][0])**2+(puntos[i][2][0]-puntos[i+1][2][0])**2)**(1/2)
        splicerCurve = cu.evalCurve(Gmb, 500)
        subcurvas += [splicerCurve]

    elif i==len(puntos)-2:
        P1 = puntos[i]
        P2 = puntos[i + 1]
        v1 = velocidad(puntos[i-1], P1, P2)
        v2 = velocidad(P1, P2, puntos[0])
        Gmb = cu.hermiteMatrix(P1, P2, v1, v2)
        # funcion que genera la spline de catmull-rom
        distancia=((puntos[i][0][0]-puntos[i+1][0][0])**2+(puntos[i][1][0]-puntos[i+1][1][0])**2+(puntos[i][2][0]-puntos[i+1][2][0])**2)**(1/2)
        splicerCurve = cu.evalCurve(Gmb, 500)
        subcurvas += [splicerCurve]

    elif i==len(puntos)-1:
        P1 = puntos[i]
        P2 = puntos[0]
        v1 = velocidad(puntos[i - 1], P1, P2)
        v2 = velocidad(P1, P2, puntos[1])
        Gmb = cu.hermiteMatrix(P1, P2, v1, v2)
        # funcion que genera la spline de catmull-rom
        distancia = ((puntos[i][0][0] - puntos[0][0][0]) ** 2 + (puntos[i][1][0] - puntos[0][1][0]) ** 2 + (puntos[i][2][0] - puntos[0][2][0]) ** 2) ** (1 / 2)
        splicerCurve = cu.evalCurve(Gmb, 500)
        subcurvas += [splicerCurve]

    else:
        P1 = puntos[i]
        P2 = puntos[i+1]
        v1 = velocidad(puntos[i - 1], P1, P2)
        v2 = velocidad(P1, P2, puntos[i+2])
        Gmb = cu.hermiteMatrix(P1, P2, v1, v2)
        # funcion que genera la spline de catmull-rom
        distancia = ((puntos[i][0][0] - puntos[i + 1][0][0]) ** 2 + (puntos[i][1][0] - puntos[i + 1][1][0]) ** 2 + ( puntos[i][2][0] - puntos[i + 1][2][0]) ** 2) ** (1 / 2)
        splicerCurve = cu.evalCurve(Gmb, 500)
        subcurvas += [splicerCurve]
 curvas = sg.SceneGraphNode('curvas')
 for x in range(len(subcurvas)):
     a = es.toGPUShape(bs.createCurve(subcurvas[x]))
     n=sg.SceneGraphNode(str(x))
     n.childs+=[a]
     curvas.childs += [n]

 return curvas,subcurvas



def crearPista(subcurvas,subcurvas2):
    for i in range(len(subcurvas)):
        assert len(subcurvas[i])==len(subcurvas2[i])
    vertices=[]
    indices=[]
    normales=[]
    n=0
    for i in range(len(subcurvas)):
     j=0
     while j<len(subcurvas[i]):
        v = np.subtract(subcurvas2[i][j], subcurvas[i][j])
        v = np.multiply(v, 0.1)
        if j!=0:
          normal = normalizar(np.cross(np.array([np.subtract(subcurvas[i][j], subcurvas[i][j - 1])]), np.array([v])).T)
          if normal[2][0] < 0:
            normal = -normal
          normales.append(normal)
        if j==0:
            normal=np.array([[0,0,1]]).T
        if j!=len(subcurvas[i])-1:
         vertices+=[subcurvas[i][j][0],subcurvas[i][j][1],subcurvas[i][j][2],0,1,normal[0][0],normal[1][0],normal[2][0]]
         vertices+=[subcurvas2[i][j][0],subcurvas2[i][j][1],subcurvas2[i][j][2],1,1,normal[0][0],normal[1][0],normal[2][0]]
         vertices+=[subcurvas[i][j+1][0], subcurvas[i][j+1][1], subcurvas[i][j+1][2], 0, 0, normal[0][0], normal[1][0],normal[2][0]]
         vertices+=[subcurvas2[i][j+1][0], subcurvas2[i][j + 1][1], subcurvas2[i][j+1][2], 1, 0, normal[0][0],normal[1][0], normal[2][0]]
        if j==len(subcurvas[i])-1 and i!=len(subcurvas)-1:
            vertices += [subcurvas[i][j][0], subcurvas[i][j][1], subcurvas[i][j][2], 0, 1, normal[0][0], normal[1][0],
                         normal[2][0]]
            vertices += [subcurvas2[i][j][0], subcurvas2[i][j][1], subcurvas2[i][j][2], 1, 1, normal[0][0],
                         normal[1][0], normal[2][0]]
            vertices += [subcurvas[i+1][0][0], subcurvas[i+1][0][1], subcurvas[i+1][0][2], 0, 0, normal[0][0],
                         normal[1][0], normal[2][0]]
            vertices += [subcurvas2[i+1][0][0], subcurvas2[i+1][0][1], subcurvas2[i+1][0][2], 1, 0, normal[0][0],
                         normal[1][0], normal[2][0]]

        if j == len(subcurvas[i]) - 1 and i == len(subcurvas) - 1:
            vertices += [subcurvas[i][j][0], subcurvas[i][j][1], subcurvas[i][j][2], 0, 1, normal[0][0], normal[1][0],
                         normal[2][0]]
            vertices += [subcurvas2[i][j][0], subcurvas2[i][j][1], subcurvas2[i][j][2], 1, 1, normal[0][0],
                         normal[1][0], normal[2][0]]
            vertices += [subcurvas[0][0][0], subcurvas[0][0][1], subcurvas[0][0][2], 0, 0, normal[0][0],
                         normal[1][0], normal[2][0]]
            vertices += [subcurvas2[0][0][0], subcurvas2[0][0][1], subcurvas2[0][0][2], 1, 0, normal[0][0],
                         normal[1][0], normal[2][0]]
        indices += [n, n + 1, n + 2, n + 1, n + 2, n + 3]
        n += 4
        j+=1
    pista = sg.SceneGraphNode('pista')
    pista.childs += [es.toGPUShape(bs.Shape(vertices, indices,'pista.jpg'), GL_REPEAT, GL_NEAREST)]
    return pista




def crear_auto():
    #creando la parte trasera
    vertices = [
        #   positions        texture    normal
        -0.5, -0.3, 0.0, 0.045, 0.3,    0,0,1,
        0.5, -0.3, 0.0, 0.4425, 0.3,    0,0,1,
        0.5, 0.3, 0.0, 0.4425, 0.2,   0,0,1,
        -0.5, 0.3, 0.0, 0.045, 0.2,    0,0,1]
    indices = [
        0, 1, 2,
        2, 3, 0]
    textureFileName ='auto.png'
    rectanguloTrasero=sg.SceneGraphNode('rectanguloTrasero')
    rectanguloTrasero.childs+=[es.toGPUShape(bs.Shape(vertices, indices, textureFileName),GL_REPEAT, GL_NEAREST)]

    vertices = [
        #   positions        texture    normal
        -0.5, -0.3, 0.0, 0.045, 0.2,    0,0,1,
        0.5, -0.3, 0.0, 0.4425, 0.2,    0,0,1,
        0.5, 0.1, 0.0, 0.42, 0.1,    0,0,1,
        -0.5, 0.1, 0.0, 0.09, 0.1,    0,0,1,]
    indices = [
        0, 1, 2,
        2, 3, 0]
    ventanaTrasera=sg.SceneGraphNode('ventanaTrasera')
    ventanaTrasera.childs+=[es.toGPUShape(bs.Shape(vertices, indices, textureFileName),GL_REPEAT, GL_NEAREST)]
    ventanaTrasera.transform=tr.translate(0,0.6,0)
    atras=sg.SceneGraphNode('atras')
    atras.childs+=[ventanaTrasera,rectanguloTrasero]
    atras.transform=tr.rotationX(np.pi/2)

    #creando la parte lateral
    vertices = [
        #   positions        texture     normal
        -0.7, -0.3, 0.0, 0.035, 0.96,    0,0,-1,
        0.7, -0.3, 0.0, 0.79, 0.96,    0,0,-1,
        0.7, 0.3, 0.0, 0.79, 0.8,    0,0,-1,
        -0.7, 0.3, 0.0, 0.035, 0.8,    0,0,-1,]
    indices = [
        0, 1, 2,
        2, 3, 0]
    autoLateral1 = sg.SceneGraphNode('autoLateral1')
    autoLateral1.childs += [es.toGPUShape(bs.Shape(vertices, indices, textureFileName), GL_REPEAT, GL_NEAREST)]
    autoLateral1.transform = np.matmul(np.matmul(tr.translate(-0.5, 0.7, 0.05),tr.rotationX(np.pi/2)),tr.rotationY(np.pi/2))
    autoLateral2 = sg.SceneGraphNode('autoLateral2')
    autoLateral2.childs += [es.toGPUShape(bs.Shape(vertices, indices, textureFileName), GL_REPEAT, GL_NEAREST)]
    autoLateral2.transform = np.matmul(np.matmul(tr.translate(0.5, 0.7, 0.05), tr.rotationX(np.pi / 2)), tr.rotationY(np.pi / 2))

    vertices = [
        #   positions        texture     normal
        -0.7, -0.15, 0.0, 0.15, 0.78,    0,0,-1,
        0.7, -0.15, 0.0, 0.47, 0.78,    0,0,-1,
        0.7, 0.15, 0.0, 0.47, 0.71,    0,0,-1,
        -0.7, 0.15, 0.0, 0.15, 0.71,    0,0,-1,]
    indices = [
        0, 1, 2,
        2, 3, 0]
    ventanaLateral1 = sg.SceneGraphNode('ventanaLateral1')
    ventanaLateral1.childs += [es.toGPUShape(bs.Shape(vertices, indices, textureFileName), GL_REPEAT, GL_NEAREST)]
    ventanaLateral1.transform = np.matmul(np.matmul(tr.translate(0.5, 0.7, 0.5), tr.rotationX(np.pi / 2)),tr.rotationY(np.pi / 2))

    ventanaLateral2 = sg.SceneGraphNode('ventanaLateral2')
    ventanaLateral2.childs += [es.toGPUShape(bs.Shape(vertices, indices, textureFileName), GL_REPEAT, GL_NEAREST)]
    ventanaLateral2.transform = np.matmul(np.matmul(tr.translate(-0.5, 0.7, 0.5), tr.rotationX(np.pi / 2)),
                                          tr.rotationY(np.pi / 2))
    lateral=sg.SceneGraphNode('lateral')
    lateral.childs+=[autoLateral1,autoLateral2,ventanaLateral1,ventanaLateral2]
    lateral.transform=tr.scale(1,1,1.1)

    #creando el techo
    vertices = [
        #   positions        texture    normal
        -0.7, -0.5, 0.0, 0.28, 0.56,    0,0,1,
        0.7, -0.5, 0.0, 0.6, 0.56,    0,0,1,
        0.7, 0.5, 0.0, 0.6, 0.39,    0,0,1,
        -0.7, 0.5, 0.0, 0.28, 0.39,    0,0,1,]
    indices = [
        0, 1, 2,
        2, 3, 0]
    techo = sg.SceneGraphNode('techo')
    techo.childs += [es.toGPUShape(bs.Shape(vertices, indices, textureFileName), GL_REPEAT, GL_NEAREST)]
    techo.transform = np.matmul(tr.translate(0, 0.7, 0.7),tr.rotationZ(np.pi/2))

    vertices = [
        #   positions        texture    normal
        -0.3, -0.3, 0.0, 0.68, 0.99,    0,0,-1,
        0.3, -0.3, 0.0, 0.78, 0.99,    0,0,-1,
        0.3, 0.3, 0.0, 0.78, 0.88,    0,0,-1,
        -0.3, 0.3, 0.0, 0.68, 0.88,    0,0,-1,]
    indices = [
        0, 1, 2,
        2, 3, 0]
    ruedatrasera1 = sg.SceneGraphNode('ruedatrasera1')
    ruedatrasera1.childs += [es.toGPUShape(bs.Shape(vertices, indices, textureFileName), GL_REPEAT, GL_NEAREST)]
    ruedatrasera1.transform = np.matmul(np.matmul(tr.translate(0.51, 0.25, -0.1),tr.rotationY(np.pi/2)),tr.uniformScale(0.65))

    ruedatrasera2 = sg.SceneGraphNode('ruedatrasera2')
    ruedatrasera2.childs += [es.toGPUShape(bs.Shape(vertices, indices, textureFileName), GL_REPEAT, GL_NEAREST)]
    ruedatrasera2.transform = np.matmul(np.matmul(tr.translate(-0.51, 0.25, -0.1), tr.rotationY(np.pi / 2)),
                                        tr.uniformScale(0.65))


    auto = sg.SceneGraphNode('auto')
    auto.childs+=[atras,lateral,techo,ruedatrasera1,ruedatrasera2]
    return auto


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return

    elif key == glfw.KEY_ESCAPE:
        sys.exit()


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Lighting demo", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Different shader programs for different lighting strategies

    ModelView=es.SimpleModelViewProjectionShaderProgram()
    lightingTexturePipeline= ls.SimpleTextureGouraudShaderProgram()
    lightingPipeline=ls.SimpleGouraudShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    curvas,subcurvas = crearSubcurvas(puntos)
    curvas2,subcurvas2=crearSubcurvas(puntos2)
    pista=crearPista(subcurvas, subcurvas2)
    auto=crear_auto()
    n=0
    t0 = glfw.get_time()
    camera_theta=16.2*np.pi/14
    camX = (puntos[0][0][0]+puntos2[0][0][0])/2
    camY = (puntos[0][1][0]+puntos2[0][1][0])/2
    camZ=0.4
    lookAt=np.array([-0.27417,-2.45318624,0])
    puntosnuevos=[]
    for x in subcurvas:
        for y in x:
         puntosnuevos.append(y)
    subcurvas=puntosnuevos
    puntosnuevos = []
    for x in subcurvas2:
        for y in x:
            puntosnuevos.append(y)
    subcurvas2 = puntosnuevos
    while not glfw.window_should_close(window):

        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1
        v = np.subtract(lookAt, np.array([camX, camY, 0]))


        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta+=0.02
            rotacion = np.array(
                [[np.cos(0.02), -np.sin(0.02), 0], [np.sin(0.02), np.cos(0.02), 0],
                 [0, 0, 1]])

            lookAt = np.array([[lookAt[0], lookAt[1], lookAt[2]]]).T
            posicion_auto = np.array([[lookAt[0][0] - v[0] * 0.7, lookAt[1][0] - v[1] * 0.7, 0]]).T
            lookAt = np.subtract(lookAt, posicion_auto)
            lookAt = np.matmul(rotacion, lookAt)
            lookAt = np.subtract(lookAt, -posicion_auto)
            lookAt = np.array([lookAt[0][0], lookAt[1][0], lookAt[2][0]])

            eye = np.array([[camX, camY, 0]]).T
            eye = np.subtract(eye, posicion_auto)
            eye = np.matmul(rotacion, eye)
            eye = np.subtract(eye, -posicion_auto)
            camX = eye[0][0]
            camY = eye[1][0]

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta -= 0.02
            rotacion = np.array(
                [[np.cos(-0.02), -np.sin(-0.02), 0], [np.sin(-0.02), np.cos(-0.02), 0],
                 [0, 0, 1]])
            lookAt = np.array([[lookAt[0], lookAt[1], lookAt[2]]]).T
            posicion_auto=np.array([[lookAt[0][0] - v[0] * 0.7, lookAt[1][0] - v[1] * 0.7, 0]]).T
            lookAt = np.subtract(lookAt,posicion_auto)
            lookAt = np.matmul(rotacion, lookAt)
            lookAt = np.subtract(lookAt, -posicion_auto)
            lookAt = np.array([lookAt[0][0], lookAt[1][0], lookAt[2][0]])

            eye = np.array([[camX, camY, 0]]).T
            eye = np.subtract(eye, posicion_auto)
            eye = np.matmul(rotacion, eye)
            eye = np.subtract(eye, -posicion_auto)
            camX=eye[0][0]
            camY=eye[1][0]

        if (glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS):
            v=np.subtract(lookAt,np.array([camX,camY,0]))
            lookAt=np.array([lookAt[0]+np.multiply(v[0],0.01),lookAt[1]+np.multiply(v[1],0.01),lookAt[2]])
            camX+=np.multiply(v[0],0.01)
            camY+=np.multiply(v[1],0.01)



        if (glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS):
            v=np.subtract(lookAt,np.array([camX,camY,0]))
            lookAt=np.array([lookAt[0]-np.multiply(v[0],0.01),lookAt[1]-np.multiply(v[1],0.01),lookAt[2]])
            camX-=np.multiply(v[0],0.01)
            camY-=np.multiply(v[1],0.01)

        posicion_auto=[lookAt[0] - v[0] * 0.7, lookAt[1] - v[1] * 0.7, 0.1]
        if 100<=n<=4399:
         for i in range(n-100,n+100):
            v=np.subtract(subcurvas[i+1],subcurvas2[i])
            modulo=(v[0]**2+v[1]**2)**(1/2)
            auto_punto=np.subtract(posicion_auto,subcurvas[i+1])
            if (auto_punto[0]**2+auto_punto[1]**2)**(1/2)<modulo:
                auto_punto = np.subtract(posicion_auto, subcurvas2[i])
                if (auto_punto[0] ** 2 + auto_punto[1] ** 2) ** (1 / 2) < modulo:
                    v = np.subtract(subcurvas[i], subcurvas2[i+1])
                    modulo = (v[0] ** 2 + v[1] ** 2) ** (1 / 2)
                    auto_punto = np.subtract(posicion_auto, subcurvas[i])
                    if (auto_punto[0] ** 2 + auto_punto[1] ** 2) ** (1 / 2) < modulo:
                        auto_punto = np.subtract(posicion_auto, subcurvas2[i+1])
                        if (auto_punto[0] ** 2 + auto_punto[1] ** 2) ** (1 / 2) < modulo:
                            n=i
                            break
        if  n<100:
            a=range(4400+n,4499)
            b=range(0,101+n)
            for i in a:
                v = np.subtract(subcurvas[i + 1], subcurvas2[i])
                modulo = (v[0] ** 2 + v[1] ** 2) ** (1 / 2)
                auto_punto = np.subtract(posicion_auto, subcurvas[i + 1])
                if (auto_punto[0] ** 2 + auto_punto[1] ** 2) ** (1 / 2) < modulo:
                    auto_punto = np.subtract(posicion_auto, subcurvas2[i])
                    if (auto_punto[0] ** 2 + auto_punto[1] ** 2) ** (1 / 2) < modulo:
                        v = np.subtract(subcurvas[i], subcurvas2[i + 1])
                        modulo = (v[0] ** 2 + v[1] ** 2) ** (1 / 2)
                        auto_punto = np.subtract(posicion_auto, subcurvas[i])
                        if (auto_punto[0] ** 2 + auto_punto[1] ** 2) ** (1 / 2) < modulo:
                            auto_punto = np.subtract(posicion_auto, subcurvas2[i + 1])
                            if (auto_punto[0] ** 2 + auto_punto[1] ** 2) ** (1 / 2) < modulo:
                                n = i
                                break
            for i in b:
                v = np.subtract(subcurvas[i + 1], subcurvas2[i])
                modulo = (v[0] ** 2 + v[1] ** 2) ** (1 / 2)
                auto_punto = np.subtract(posicion_auto, subcurvas[i + 1])
                if (auto_punto[0] ** 2 + auto_punto[1] ** 2) ** (1 / 2) < modulo:
                    auto_punto = np.subtract(posicion_auto, subcurvas2[i])
                    if (auto_punto[0] ** 2 + auto_punto[1] ** 2) ** (1 / 2) < modulo:
                        v = np.subtract(subcurvas[i], subcurvas2[i + 1])
                        modulo = (v[0] ** 2 + v[1] ** 2) ** (1 / 2)
                        auto_punto = np.subtract(posicion_auto, subcurvas[i])
                        if (auto_punto[0] ** 2 + auto_punto[1] ** 2) ** (1 / 2) < modulo:
                            auto_punto = np.subtract(posicion_auto, subcurvas2[i + 1])
                            if (auto_punto[0] ** 2 + auto_punto[1] ** 2) ** (1 / 2) < modulo:
                                n = i
                                break

        if n>4399:
            for i in range(n - 100, 4499):
                v = np.subtract(subcurvas[i + 1], subcurvas2[i])
                modulo = (v[0] ** 2 + v[1] ** 2) ** (1 / 2)
                auto_punto = np.subtract(posicion_auto, subcurvas[i + 1])
                if (auto_punto[0] ** 2 + auto_punto[1] ** 2) ** (1 / 2) < modulo:
                    auto_punto = np.subtract(posicion_auto, subcurvas2[i])
                    if (auto_punto[0] ** 2 + auto_punto[1] ** 2) ** (1 / 2) < modulo:
                        v = np.subtract(subcurvas[i], subcurvas2[i + 1])
                        modulo = (v[0] ** 2 + v[1] ** 2) ** (1 / 2)
                        auto_punto = np.subtract(posicion_auto, subcurvas[i])
                        if (auto_punto[0] ** 2 + auto_punto[1] ** 2) ** (1 / 2) < modulo:
                            auto_punto = np.subtract(posicion_auto, subcurvas2[i + 1])
                            if (auto_punto[0] ** 2 + auto_punto[1] ** 2) ** (1 / 2) < modulo:
                                n = i
                                break
            for i in range(0, 4499-n):
                v = np.subtract(subcurvas[i + 1], subcurvas2[i])
                modulo = (v[0] ** 2 + v[1] ** 2) ** (1 / 2)
                auto_punto = np.subtract(posicion_auto, subcurvas[i + 1])
                if (auto_punto[0] ** 2 + auto_punto[1] ** 2) ** (1 / 2) < modulo:
                    auto_punto = np.subtract(posicion_auto, subcurvas2[i])
                    if (auto_punto[0] ** 2 + auto_punto[1] ** 2) ** (1 / 2) < modulo:
                        v = np.subtract(subcurvas[i], subcurvas2[i + 1])
                        modulo = (v[0] ** 2 + v[1] ** 2) ** (1 / 2)
                        auto_punto = np.subtract(posicion_auto, subcurvas[i])
                        if (auto_punto[0] ** 2 + auto_punto[1] ** 2) ** (1 / 2) < modulo:
                            auto_punto = np.subtract(posicion_auto, subcurvas2[i + 1])
                            if (auto_punto[0] ** 2 + auto_punto[1] ** 2) ** (1 / 2) < modulo:
                                n = i
                                break


        v = np.subtract(lookAt, np.array([camX, camY, 0]))
        if n<4300:
         auto.transform = np.matmul(
            np.matmul(tr.translate(lookAt[0] - v[0] * 0.7, lookAt[1] - v[1] * 0.7, 0.68*subcurvas[n+200][2]+0.1),
                      tr.uniformScale(0.1)), tr.rotationZ(camera_theta))
        if n>=4300:
            auto.transform = np.matmul(
                np.matmul(
                    tr.translate(lookAt[0] - v[0] * 0.7, lookAt[1] - v[1] * 0.7, 0.68 * subcurvas[n + 200-4500][2] + 0.1),
                    tr.uniformScale(0.1)), tr.rotationZ(camera_theta))

        projection = tr.ortho(-1, 1, -1, 1, 0.1, 100)
        projection = tr.perspective(45, float(width)/float(height), 0.1, 100)



        viewPos = np.array([camX,camY,camZ])

        view = tr.lookAt(
            viewPos,
            lookAt,
            np.array([0,0,1])
        )

        rotation_theta = glfw.get_time()



        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Selecting the lighting shader program
        
        glUseProgram(ModelView.shaderProgram)

        # Setting all uniform shader variables

        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(ModelView.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(ModelView.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(ModelView.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        # Object is barely visible at only ambient. Diffuse behavior is slightly red. Sparkles are white
        glUniform3f(glGetUniformLocation(ModelView.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(ModelView.shaderProgram, "Kd"), 0.9, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(ModelView.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        # TO DO: Explore different parameter combinations to understand their effect!

        glUniform3f(glGetUniformLocation(ModelView.shaderProgram, "lightPosition"), -5, -5, 5)
        glUniform3f(glGetUniformLocation(ModelView.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniform1ui(glGetUniformLocation(ModelView.shaderProgram, "shininess"), 100)
        
        glUniform1f(glGetUniformLocation(ModelView.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(ModelView.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(ModelView.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(ModelView.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(ModelView.shaderProgram, "view"), 1, GL_TRUE, view)



        # Drawing

        #sg.drawSceneGraphNode(curvas,ModelView,'model',GL_LINE_STRIP)
        #sg.drawSceneGraphNode(curvas2, ModelView, 'model', GL_LINE_STRIP)




        glUseProgram(lightingTexturePipeline.shaderProgram)

        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(lightingTexturePipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingTexturePipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingTexturePipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        # Object is barely visible at only ambient. Diffuse behavior is slightly red. Sparkles are white
        glUniform3f(glGetUniformLocation(lightingTexturePipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(lightingTexturePipeline.shaderProgram, "Kd"), 0.9, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(lightingTexturePipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        # TO DO: Explore different parameter combinations to understand their effect!

        glUniform3f(glGetUniformLocation(lightingTexturePipeline.shaderProgram, "lightPosition"), -5, -5, 5)
        glUniform3f(glGetUniformLocation(lightingTexturePipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1],
                    viewPos[2])
        glUniform1ui(glGetUniformLocation(lightingTexturePipeline.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(lightingTexturePipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(lightingTexturePipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(lightingTexturePipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(lightingTexturePipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(lightingTexturePipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        sg.drawSceneGraphNode(auto, lightingTexturePipeline, 'model')
        sg.drawSceneGraphNode(pista, lightingTexturePipeline, 'model')








        glUseProgram(lightingPipeline.shaderProgram)

        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        # Object is barely visible at only ambient. Diffuse behavior is slightly red. Sparkles are white
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 0.9, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        # TO DO: Explore different parameter combinations to understand their effect!

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPosition"), -5, -5, 5)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1],
                    viewPos[2])
        glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE,
                           projection)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)





        
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
