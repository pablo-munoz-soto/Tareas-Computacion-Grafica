
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
#funcion que normaliza un vector
def normalizar(vector):
    modulo=(vector[0][0]**2+vector[1][0]**2+vector[2][0]**2)**(1/2)
    if modulo==0:return
    vector=np.multiply(vector,1/modulo)
    return vector
#funcion que a partir de tres puntos calcula el vector perpendicular a la bisectriz
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

#puntos que generan la curva
puntos=[np.array([[-0.5,-1,0]]).T,np.array([[0,-2,0.1]]).T,np.array([[0.5,-1,0.3]]).T,np.array([[0.5,0.3,0.1]]).T,np.array([[0.5,1,0.1]]).T,np.array([[0,1.5,0.2]]).T,np.array([[-0.5,4,0]]).T,np.array([[-2,5,0.2]]).T,np.array([[-4,5,0]]).T,np.array([[-4,3,0]]).T,np.array([[-1,0,0]]).T]
puntos2=[]
#llenando la lista 2 con los puntos
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
#funcion que genera la RNS
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


#funcion que crea la malla que conforma la pista
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



#funcion que crea el auto
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

#funcion que crea las decoraciones,animaciones y el contador de vueltas
def crear_ambientacion():
    textureQuad=bs.createTextureQuad('cielo.jpg')
    cielo1=sg.SceneGraphNode('cielo1')
    cielo1.childs+=[es.toGPUShape(textureQuad,GL_REPEAT, GL_NEAREST)]
    cielo1.transform=np.matmul(tr.translate(0,-10,0),np.matmul(tr.uniformScale(20),tr.rotationX(np.pi/2)))
    cielo2 = sg.SceneGraphNode('cielo2')
    cielo2.childs += [es.toGPUShape(textureQuad, GL_REPEAT, GL_NEAREST)]
    cielo2.transform = np.matmul(tr.translate(10, 0, 0),np.matmul(tr.rotationZ(np.pi/2), np.matmul(tr.uniformScale(20), tr.rotationX(np.pi / 2))))
    cielo3 = sg.SceneGraphNode('cielo3')
    cielo3.childs += [es.toGPUShape(textureQuad, GL_REPEAT, GL_NEAREST)]
    cielo3.transform = np.matmul(tr.translate(-10, 0, 0), np.matmul(tr.rotationZ(np.pi / 2),
                                                                     np.matmul(tr.uniformScale(20),
                                                                               tr.rotationX(np.pi / 2))))

    cielo4 = sg.SceneGraphNode('cielo4')
    cielo4.childs += [es.toGPUShape(textureQuad, GL_REPEAT, GL_NEAREST)]
    cielo4.transform=np.matmul(tr.translate(0,10,0),np.matmul(tr.uniformScale(20),tr.rotationX(np.pi/2)))

    sol=sg.SceneGraphNode('sol')
    sol.childs+=[es.toGPUShape(bs.createTextureQuad('sol.jpg'), GL_REPEAT, GL_NEAREST)]
    sol.transform=np.matmul(tr.translate(0,-7,1),np.matmul(tr.uniformScale(0.5),tr.rotationX(np.pi/2)))


    cielo=sg.SceneGraphNode('cielo')
    cielo.childs+=[cielo1,cielo2,cielo3,cielo4,sol]

    avion=sg.SceneGraphNode('avion')
    avion.childs+=[es.toGPUShape(bs.createTextureQuad('avion.jpg'), GL_REPEAT, GL_NEAREST)]
    avion.transform=np.matmul(tr.translate(9.9,9,1),np.matmul(np.matmul(tr.rotationX(np.pi/2),tr.rotationY(np.pi/2)),tr.uniformScale(1)))

    lap=sg.SceneGraphNode('lap')
    lap.childs += [es.toGPUShape(bs.createTextureQuad('lap.png'), GL_REPEAT, GL_NEAREST)]

    numero1 = sg.SceneGraphNode('numero1')
    numero1.childs += [es.toGPUShape(bs.createTextureQuad('1.jpg'), GL_REPEAT, GL_NEAREST)]

    numero2 = sg.SceneGraphNode('numero2')
    numero2.childs += [es.toGPUShape(bs.createTextureQuad('2.jpg'), GL_REPEAT, GL_NEAREST)]


    numero3 = sg.SceneGraphNode('numero3')
    numero3.childs += [es.toGPUShape(bs.createTextureQuad('3.jpg'), GL_REPEAT, GL_NEAREST)]




    return cielo,avion,lap, numero1, numero2, numero3





if __name__ == "__main__":

    if not glfw.init():
        sys.exit()
    #creando la ventana
    width = 600
    height = 600

    window = glfw.create_window(width, height, "Crazy Racer", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)


    #creando los modos que usaremos

    ModelViewTexture=es.SimpleTextureModelViewProjectionShaderProgram()
    lightingTexturePipeline= ls.SimpleTextureGouraudShaderProgram()

    glClearColor(0.85, 0.85, 0.85, 1.0)

    glEnable(GL_DEPTH_TEST)

    # creando las shapes y asignando variables para controlar
    curvas,subcurvas = crearSubcurvas(puntos)
    curvas2,subcurvas2=crearSubcurvas(puntos2)
    pista=crearPista(subcurvas, subcurvas2)
    auto=crear_auto()
    cielo,avion,lap,numero1,numero2,numero3=crear_ambientacion()
    traslacion_avion=0
    vuelta=1
    check=0
    n=0
    t0 = glfw.get_time()
    camera_theta=16.2*np.pi/14
    camX = (puntos[0][0][0]+puntos2[0][0][0])/2
    camY = (puntos[0][1][0]+puntos2[0][1][0])/2
    camZ=0.4
    lookAt=np.array([-0.27417,-2.45318624,0])
    v = np.subtract(lookAt, np.array([camX, camY, 0]))
    v=np.array([[v[0],v[1],v[2]]]).T
    x = 1
    if v[0][0] == 0:
        y = 0
    if v[1][0] == 0:
        y = 1
        x = 0
    if v[0][0] != 0 and v[1][0] != 0:
        y = (-v[0][0] * x) / v[1][0]
    v2 = normalizar(np.array([[x, y, 0]]).T)
    if np.cross(v.T, v2.T)[0][2] > 0:
        v2 = -v2
    v2=np.array([v2[0][0],v2[1][0],0])
    posicion_lap=np.subtract(lookAt,np.multiply(v2,0.45))
    posicion_numero=np.subtract(lookAt,np.multiply(v2,0.25))
    lap.transform = np.matmul(tr.translate(posicion_lap[0],posicion_lap[1],0.47),
                              np.matmul(tr.rotationZ(camera_theta - np.pi / 2+0.3),
                                        np.matmul(np.matmul(tr.rotationX(np.pi / 2), tr.rotationY(np.pi / 2)),
                                                  tr.uniformScale(0.2))))
    numero1.transform=np.matmul(tr.translate(posicion_numero[0],posicion_numero[1],0.47),
                              np.matmul(tr.rotationZ(camera_theta - np.pi / 2+0.3),
                                        np.matmul(np.matmul(tr.rotationX(np.pi / 2), tr.rotationY(np.pi / 2)),
                                                  tr.uniformScale(0.2))))
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

        v = np.subtract(lookAt, np.array([camX, camY, 0]))

        #giro a la izquierda del auto
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
        #giro a la derecha del auto
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
        #avance del auto
        if (glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS):
            v=np.subtract(lookAt,np.array([camX,camY,0]))
            lookAt=np.array([lookAt[0]+np.multiply(v[0],0.01),lookAt[1]+np.multiply(v[1],0.01),lookAt[2]])
            camX+=np.multiply(v[0],0.01)
            camY+=np.multiply(v[1],0.01)
        #retroceso del auto
        if (glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS):
            v=np.subtract(lookAt,np.array([camX,camY,0]))
            lookAt=np.array([lookAt[0]-np.multiply(v[0],0.01),lookAt[1]-np.multiply(v[1],0.01),lookAt[2]])
            camX-=np.multiply(v[0],0.01)
            camY-=np.multiply(v[1],0.01)

        #calculando la posicion del auto en la pista
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
        #asignando la transformacion al auto
        if n<4300:
         auto.transform = np.matmul(
            np.matmul(tr.translate(lookAt[0] - v[0] * 0.7, lookAt[1] - v[1] * 0.7, 0.68*subcurvas[n+200][2]+0.1),
                      tr.uniformScale(0.1)), tr.rotationZ(camera_theta))
        if n>=4300:
            auto.transform = np.matmul(
                np.matmul(
                    tr.translate(lookAt[0] - v[0] * 0.7, lookAt[1] - v[1] * 0.7, 0.68 * subcurvas[n + 200-4500][2] + 0.1),
                    tr.uniformScale(0.1)), tr.rotationZ(camera_theta))
        #se usa un check a la mitad de la pista para el contador de vueltas
        if 2300<n<2400 and vuelta==1 and check==0:
            check+=1
        if 2300<n<2400 and vuelta==2 and check==1:
            check+=1

        #solo si el check fue pasado se cuenta la vuelta
        if n==0 and vuelta==1 and check==1:
            vuelta+=1
        if n==0 and vuelta==2 and check==2:
            vuelta+=1
        #asignando las matrices
        projection = tr.ortho(-1, 1, -1, 1, 0.1, 100)
        projection = tr.perspective(45, float(width)/float(height), 0.1, 100)



        viewPos = np.array([camX,camY,camZ])

        view = tr.lookAt(
            viewPos,
            lookAt,
            np.array([0,0,1])
        )

        rotation_theta = glfw.get_time()


        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        
        glUseProgram(ModelViewTexture.shaderProgram)



        glUniformMatrix4fv(glGetUniformLocation(ModelViewTexture.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(ModelViewTexture.shaderProgram, "view"), 1, GL_TRUE, view)



        #creando el contador de vueltas
        v = np.subtract(lookAt, np.array([camX, camY, 0]))
        v = np.array([[v[0], v[1], v[2]]]).T
        x = 1
        if v[0][0] == 0:
            y = 0
        if v[1][0] == 0:
            y = 1
            x = 0
        if v[0][0] != 0 and v[1][0] != 0:
            y = (-v[0][0] * x) / v[1][0]
        v2 = normalizar(np.array([[x, y, 0]]).T)
        if np.cross(v.T, v2.T)[0][2] > 0:
            v2 = -v2
        v2 = np.array([v2[0][0], v2[1][0], 0])

        posicion_lap = np.subtract(lookAt, np.multiply(v2, 0.45))
        posicion_numero = np.subtract(lookAt, np.multiply(v2, 0.25))
        lap.transform = np.matmul(tr.translate(posicion_lap[0], posicion_lap[1], 0.47),
                                  np.matmul(tr.rotationZ(camera_theta - np.pi / 2 + 0.3),
                                            np.matmul(np.matmul(tr.rotationX(np.pi / 2), tr.rotationY(np.pi / 2)),
                                                      tr.uniformScale(0.2))))


        #mostrando el numero correspondiente a la vuelta
        if vuelta==1:
         numero1.transform = np.matmul(tr.translate(posicion_numero[0], posicion_numero[1], 0.47),
                                      np.matmul(tr.rotationZ(camera_theta - np.pi / 2 + 0.3),
                                                np.matmul(np.matmul(tr.rotationX(np.pi / 2), tr.rotationY(np.pi / 2)),
                                                          tr.uniformScale(0.2))))
         sg.drawSceneGraphNode(numero1, ModelViewTexture, 'model')

        if vuelta==2:
         numero2.transform = np.matmul(tr.translate(posicion_numero[0], posicion_numero[1], 0.47),
                                      np.matmul(tr.rotationZ(camera_theta - np.pi / 2 + 0.3),
                                                np.matmul(np.matmul(tr.rotationX(np.pi / 2), tr.rotationY(np.pi / 2)),
                                                          tr.uniformScale(0.2))))
         sg.drawSceneGraphNode(numero2, ModelViewTexture, 'model')

        if vuelta==3:
         numero3.transform = np.matmul(tr.translate(posicion_numero[0], posicion_numero[1], 0.47),
                                      np.matmul(tr.rotationZ(camera_theta - np.pi / 2 + 0.3),
                                                np.matmul(np.matmul(tr.rotationX(np.pi / 2), tr.rotationY(np.pi / 2)),
                                                          tr.uniformScale(0.2))))
         sg.drawSceneGraphNode(numero3, ModelViewTexture, 'model')
        #controlando la animacion del avion
        avion.transform=np.matmul(tr.translate(9.9,9-traslacion_avion,1),np.matmul(np.matmul(tr.rotationX(np.pi/2),tr.rotationY(np.pi/2)),tr.uniformScale(1)))
        traslacion_avion+=0.05
        if traslacion_avion>19:traslacion_avion=-6




        #dibujando la ambientacion y animaciones
        sg.drawSceneGraphNode(avion, ModelViewTexture, 'model')
        sg.drawSceneGraphNode(cielo, ModelViewTexture, 'model')
        sg.drawSceneGraphNode(lap, ModelViewTexture, 'model')


        #usando el segundo modo


        glUseProgram(lightingTexturePipeline.shaderProgram)

        glUniform3f(glGetUniformLocation(lightingTexturePipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingTexturePipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingTexturePipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(lightingTexturePipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(lightingTexturePipeline.shaderProgram, "Kd"), 0.9, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(lightingTexturePipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)


        glUniform3f(glGetUniformLocation(lightingTexturePipeline.shaderProgram, "lightPosition"), 0, -7, 1)
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

        glfw.swap_buffers(window)

    glfw.terminate()
