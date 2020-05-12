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


#puntos=[np.array([[-0.5,-0.5,0]]).T,np.array([[0.5,-0.5,0]]).T,np.array([[0.5,0.5,0]]).T,np.array([[-0.5,0.5,0]]).T]
puntos=[np.array([[-0.7,-0.7,0]]).T,np.array([[0.5,-0.7,0]]).T,np.array([[0.5,-0.5,0]]).T,np.array([[0.7,0.3,0]]).T,np.array([[0.3,0.7,0]]).T,np.array([[0.2,0.3,0]]).T,np.array([[0.2,0.1,0]]).T,np.array([[-0.2,0.1,0]]).T,np.array([[-0.5,0.7,0]]).T,np.array([[-0.7,0.3,0]]).T,np.array([[-0.8,-0.6,0]]).T]

def crearSubcurvas(puntos):
 subcurvas=[]
 for i in range(len(puntos)):
    if i==0:
        Gmb = cu.spliceMatrix(puntos[len(puntos)-1], puntos[i], puntos[i + 1], puntos[i + 2])
        # funcion que genera la spline de catmull-rom
        distancia=((puntos[i][0][0]-puntos[i+1][0][0])**2+(puntos[i][1][0]-puntos[i+1][1][0])**2+(puntos[i][2][0]-puntos[i+1][2][0])**2)**(1/2)
        splicerCurve = cu.evalCurve(Gmb, int(distancia*500))
        subcurvas += [splicerCurve]
    elif i==len(puntos)-2:
        Gmb = cu.spliceMatrix(puntos[i-1], puntos[i], puntos[i + 1], puntos[0])
        # funcion que genera la spline de catmull-rom
        distancia=((puntos[i][0][0]-puntos[i+1][0][0])**2+(puntos[i][1][0]-puntos[i+1][1][0])**2+(puntos[i][2][0]-puntos[i+1][2][0])**2)**(1/2)
        splicerCurve = cu.evalCurve(Gmb, int(distancia*500))
        subcurvas += [splicerCurve]

    elif i==len(puntos)-1:
        Gmb = cu.spliceMatrix(puntos[i-1], puntos[i], puntos[0], puntos[1])
        # funcion que genera la spline de catmull-rom
        distancia = ((puntos[i][0][0] - puntos[0][0][0]) ** 2 + (puntos[i][1][0] - puntos[0][1][0]) ** 2 + (puntos[i][2][0] - puntos[0][2][0]) ** 2) ** (1 / 2)
        splicerCurve = cu.evalCurve(Gmb, int(distancia*500))
        subcurvas += [splicerCurve]

    else:
        Gmb = cu.spliceMatrix(puntos[i - 1], puntos[i], puntos[i + 1], puntos[i + 2])
        # funcion que genera la spline de catmull-rom
        distancia = ((puntos[i][0][0] - puntos[i + 1][0][0]) ** 2 + (puntos[i][1][0] - puntos[i + 1][1][0]) ** 2 + ( puntos[i][2][0] - puntos[i + 1][2][0]) ** 2) ** (1 / 2)
        splicerCurve = cu.evalCurve(Gmb, int(distancia*500))
        subcurvas += [splicerCurve]
 curvas = sg.SceneGraphNode('curvas')
 for x in range(len(subcurvas)):
     a = es.toGPUShape(bs.createCurve(subcurvas[x]))
     n=sg.SceneGraphNode(str(x))
     n.childs+=[a]
     curvas.childs += [n]
 return curvas

def crear_auto():
    #creando la parte trasera
    vertices = [
        #   positions        texture
        -0.5, -0.3, 0.0, 0.045, 0.3,
        0.5, -0.3, 0.0, 0.4425, 0.3,
        0.5, 0.3, 0.0, 0.4425, 0.2,
        -0.5, 0.3, 0.0, 0.045, 0.2]
    indices = [
        0, 1, 2,
        2, 3, 0]
    textureFileName ='auto.png'
    rectanguloTrasero=sg.SceneGraphNode('rectanguloTrasero')
    rectanguloTrasero.childs+=[es.toGPUShape(bs.Shape(vertices, indices, textureFileName),GL_REPEAT, GL_NEAREST)]

    vertices = [
        #   positions        texture
        -0.5, -0.3, 0.0, 0.045, 0.2,
        0.5, -0.3, 0.0, 0.4425, 0.2,
        0.5, 0.1, 0.0, 0.42, 0.1,
        -0.5, 0.1, 0.0, 0.09, 0.1]
    indices = [
        0, 1, 2,
        2, 3, 0]
    ventanaTrasera=sg.SceneGraphNode('ventanaTrasera')
    ventanaTrasera.childs+=[es.toGPUShape(bs.Shape(vertices, indices, textureFileName),GL_REPEAT, GL_NEAREST)]
    ventanaTrasera.transform=tr.translate(0,0.5,0)
    atras=sg.SceneGraphNode('atras')
    atras.childs+=[ventanaTrasera,rectanguloTrasero]
    atras.transform=tr.rotationX(np.pi/2)

    #creando la parte lateral
    vertices = [
        #   positions        texture
        -0.7, -0.3, 0.0, 0.035, 0.96,
        0.7, -0.3, 0.0, 0.79, 0.96,
        0.7, 0.3, 0.0, 0.79, 0.8,
        -0.7, 0.3, 0.0, 0.035, 0.8]
    indices = [
        0, 1, 2,
        2, 3, 0]
    autoLateral1 = sg.SceneGraphNode('autoLateral1')
    autoLateral1.childs += [es.toGPUShape(bs.Shape(vertices, indices, textureFileName), GL_REPEAT, GL_NEAREST)]
    autoLateral1.transform = np.matmul(np.matmul(tr.translate(-0.5, 0.7, 0),tr.rotationX(np.pi/2)),tr.rotationY(np.pi/2))
    autoLateral2 = sg.SceneGraphNode('autoLateral2')
    autoLateral2.childs += [es.toGPUShape(bs.Shape(vertices, indices, textureFileName), GL_REPEAT, GL_NEAREST)]
    autoLateral2.transform = np.matmul(np.matmul(tr.translate(0.5, 0.7, 0), tr.rotationX(np.pi / 2)), tr.rotationY(np.pi / 2))

    vertices = [
        #   positions        texture
        -0.7, -0.15, 0.0, 0.15, 0.78,
        0.7, -0.15, 0.0, 0.47, 0.78,
        0.7, 0.15, 0.0, 0.47, 0.71,
        -0.7, 0.15, 0.0, 0.15, 0.71]
    indices = [
        0, 1, 2,
        2, 3, 0]
    ventanaLateral1 = sg.SceneGraphNode('ventanaLateral1')
    ventanaLateral1.childs += [es.toGPUShape(bs.Shape(vertices, indices, textureFileName), GL_REPEAT, GL_NEAREST)]
    ventanaLateral1.transform = np.matmul(np.matmul(tr.translate(0.5, 0.7, 0.45), tr.rotationX(np.pi / 2)),tr.rotationY(np.pi / 2))

    ventanaLateral2 = sg.SceneGraphNode('ventanaLateral2')
    ventanaLateral2.childs += [es.toGPUShape(bs.Shape(vertices, indices, textureFileName), GL_REPEAT, GL_NEAREST)]
    ventanaLateral2.transform = np.matmul(np.matmul(tr.translate(-0.5, 0.7, 0.45), tr.rotationX(np.pi / 2)),
                                          tr.rotationY(np.pi / 2))
    lateral=sg.SceneGraphNode('lateral')
    lateral.childs+=[autoLateral1,autoLateral2,ventanaLateral1,ventanaLateral2]

    #creando el techo
    vertices = [
        #   positions        texture
        -0.7, -0.5, 0.0, 0.28, 0.56,
        0.7, -0.5, 0.0, 0.6, 0.56,
        0.7, 0.5, 0.0, 0.6, 0.39,
        -0.7, 0.5, 0.0, 0.28, 0.39]
    indices = [
        0, 1, 2,
        2, 3, 0]
    techo = sg.SceneGraphNode('techo')
    techo.childs += [es.toGPUShape(bs.Shape(vertices, indices, textureFileName), GL_REPEAT, GL_NEAREST)]
    techo.transform = np.matmul(tr.translate(0, 0.7, 0.6),tr.rotationZ(np.pi/2))


    auto = sg.SceneGraphNode('auto')
    auto.childs+=[atras,lateral,techo]
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

    #lightingPipeline=es.SimpleModelViewProjectionShaderProgram()
    lightingPipeline=es.SimpleTextureModelViewProjectionShaderProgram()
    #lightingPipeline = ls.SimpleTexturePhongShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    gpu = crearSubcurvas(puntos)
    auto=crear_auto()

    t0 = glfw.get_time()
    camera_theta = np.pi/4

    while not glfw.window_should_close(window):

        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta -= 2 * dt

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta += 2* dt

        projection = tr.ortho(-1, 1, -1, 1, 0.1, 100)
        projection = tr.perspective(45, float(width)/float(height), 0.1, 100)

        camX = 3 * np.sin(camera_theta)
        camY = 3 * np.cos(camera_theta)

        viewPos = np.array([camX,camY,2])

        view = tr.lookAt(
            viewPos,
            np.array([0,0,0]),
            np.array([0,0,1])
        )

        rotation_theta = glfw.get_time()



        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Selecting the lighting shader program
        
        glUseProgram(lightingPipeline.shaderProgram)

        # Setting all uniform shader variables

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
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 100)
        
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        gpuShape=es.toGPUShape(bs.createColorNormalsCube(0,1,0))
        nodo=sg.SceneGraphNode('nodo')
        nodo.childs+=[gpuShape]

        #gpu=crearSubcurvas(puntos)
        # Drawing
        #sg.drawSceneGraphNode(gpu,lightingPipeline,'model',GL_LINE_STRIP)
        sg.drawSceneGraphNode(auto, lightingPipeline, 'model')
        
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
