import json
import numpy as np
import random
import modulos.transformations as tr
import modulos.basic_shapes as bs
import modulos.easy_shaders as es
import modulos.scene_graph as sg
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import sys
a= open(str(sys.argv[1]))
data=json.load(a)
a.close()

solucion=np.load(data['filename'])

h=0.25
t_a=data['t_a']
t_b=data['t_b']
t_c=data['t_c']
n_a=data['n_a']
n_b=data['n_b']
n_c=data['n_c']

area_a=[]
area_b=[]
area_c=[]
Width=(len(solucion)+1)*h
Lenght=(len(solucion[0])+1)*h
Height=(len(solucion[0][0])+1)*h
#se ve que puntos estan en el rango de los peces
for i in range(len(solucion)):
    for j in range(len(solucion[0])):
        for k in range(len(solucion[0][0])):
            valor=solucion[i][j][k]
            if t_a-2<=valor<=t_a+2:
                area_a.append([i,j,k])
            if t_b-2<=valor<=t_b+2:
                area_b.append([i,j,k])
            if t_c-2<=valor<=t_c+2:
                area_c.append([i,j,k])

#eleccion Na puntos a
voxeles_a=[]
while n_a!=0:
    a=random.randint(0,len(area_a)-1)
    voxeles_a.append(area_a[a])
    if area_a[a] in area_b:
     peces_b.remove(area_a[a])
    if area_a[a] in area_c:
     area_c.remove(area_a[a])
    area_a.remove(area_a[a])
    n_a-=1
#eleccion de Nb puntos b
voxeles_b=[]
while n_b!=0:
    if len(area_b)!=1:
     b=random.randint(0,len(area_b)-1)
    if len(area_b)==1:
        b = 0
    voxeles_b.append(area_b[b])
    if area_b[b] in area_c:
     area_c.remove(area_b[b])
    area_b.remove(area_b[b])
    n_b-=1
#eleccion de Nc puntos c
voxeles_c = []
while n_c!=0:
    c=random.randint(0,len(area_c)-1)
    voxeles_c.append(area_c[c])
    area_c.remove(area_c[c])
    n_c-=1

def generate_voxels(voxeles_a, voxeles_b, voxeles_c, Width, Lenght, Height, area_a, area_b, area_c):

    #generando acuario
    vertices=[]
    indices=[]
    #izquierda, atras, abajo
    vertices+=[-Width/2,-Lenght/2,-Height/2,0,0,0]
    #derecha, atras, abajo
    vertices += [Width / 2, -Lenght / 2, -Height / 2, 0, 0, 0]
    #derecha, atras, arriba
    vertices += [Width / 2, -Lenght / 2, Height / 2, 0, 0, 0]
    #izquierda, atras, arriba
    vertices += [-Width / 2, -Lenght / 2, Height / 2, 0, 0, 0]
    #izquierda, adelante, abajo
    vertices += [-Width / 2, Lenght / 2, -Height / 2, 0, 0, 0]
    #derecha, adelante, abajo
    vertices += [Width / 2, Lenght / 2, -Height / 2, 0, 0, 0]
    #derecha, adelante, arriba
    vertices += [Width / 2, Lenght / 2, Height / 2, 0, 0, 0]
    #izquierda, adelante arriba
    vertices += [-Width / 2, Lenght / 2, Height / 2, 0, 0, 0]
    #cara trasera
    indices+=[0,1,1,2,2,3,3,0]
    #cara delantera
    indices+=[4,5,5,6,6,7,7,4]
    #cara inferior
    indices+=[0,1,1,5,5,4,4,0]
    #cara superior
    indices+=[2,3,3,7,7,6,6,2]
    #cara izquierda
    indices+=[0,4,4,7,7,3,3,0]
    #cara derecha
    indices+=[1,5,5,6,6,2,2,1]
    acuario = sg.SceneGraphNode('acuario')
    a=bs.Shape(vertices, indices)
    acuario.childs += [es.toGPUShape(a, GL_REPEAT, GL_NEAREST)]



    #area a
    voxeles_area_a=sg.SceneGraphNode('voxeles_area_a')
    for i in range(len(area_a)):
        area=area_a[i]
        izq = [area[0] - 1, area[1], area[2]]
        der = [area[0] + 1, area[1], area[2]]
        atras = [area[0], area[1] - 1, area[2]]
        frente = [area[0], area[1] + 1, area[2]]
        abajo = [area[0], area[1], area[2] - 1]
        arriba = [area[0], area[1], area[2] + 1]
        if not izq in area_a or not der in area_a or not atras in area_a or not frente in area_a or not abajo in area_a or not arriba in area_a:
         a=sg.SceneGraphNode('area_a'+str(i))
         a.childs+=[es.toGPUShape(bs.createColorCube(1,0,0))]
         a.transform=np.matmul(tr.translate(area[0]*h-Width/2, area[1]*h-Lenght/2, area[2]*h-Height/2),tr.uniformScale(h/0.5))
         voxeles_area_a.childs+=[a]

    # area b
    voxeles_area_b = sg.SceneGraphNode('voxeles_area_b')
    for i in range(len(area_b)):
        area = area_b[i]
        izq = [area[0] - 1, area[1], area[2]]
        der = [area[0] + 1, area[1], area[2]]
        atras = [area[0], area[1] - 1, area[2]]
        frente = [area[0], area[1] + 1, area[2]]
        abajo = [area[0], area[1], area[2] - 1]
        arriba = [area[0], area[1], area[2] + 1]
        if not izq in area_b or not der in area_b or not atras in area_b or not frente in area_b or not abajo in area_b or not arriba in area_b:
         b = sg.SceneGraphNode('area_b' + str(i))
         b.childs += [es.toGPUShape(bs.createColorCube(0, 1, 0))]
         b.transform = np.matmul(tr.translate(area[0] * h - Width / 2, area[1] * h - Lenght / 2, area[2] * h - Height / 2),tr.uniformScale(h/0.5))
         voxeles_area_b.childs += [b]

    # area c
    n=0
    voxeles_area_c = sg.SceneGraphNode('voxeles_area_c')
    for i in range(len(area_c)):
        area = area_c[i]
        izq = [area[0] - 1, area[1], area[2]]
        der = [area[0] + 1, area[1], area[2]]
        atras = [area[0], area[1] - 1, area[2]]
        frente = [area[0], area[1] + 1, area[2]]
        abajo = [area[0], area[1], area[2] - 1]
        arriba = [area[0], area[1], area[2] + 1]
        if not izq in area_c or not der in area_c or not atras in area_c or not frente in area_c or not abajo in area_c or not arriba in area_c:
         c = sg.SceneGraphNode('area_c' + str(i))
         c.childs += [es.toGPUShape(bs.createColorCube(0, 0, 1))]
         c.transform = np.matmul(tr.translate(area[0] * h - Width / 2, area[1] * h - Lenght / 2, area[2] * h - Height / 2),tr.uniformScale(h / 0.5))
         voxeles_area_c.childs += [c]
        else:n+=1

    #arreglo que contine las colas
    colas=[]
    #peces a
    vertices = [0, -1, 0, 0, 0, 0,
                0, -2, 0.5, 0, 0, 0,
                0, -2, -0.5, 0, 0, 0]
    indices = [0, 1, 2]
    peces_a = sg.SceneGraphNode('peces_a')
    for i in range(len(voxeles_a)):
     pez=voxeles_a[i]
     a=sg.SceneGraphNode('pez_a'+str(i))
     colas.append(sg.SceneGraphNode('cola_a'+str(i)))
     colas[-1].childs += [es.toGPUShape(bs.Shape(vertices, indices), GL_REPEAT, GL_NEAREST)]
     colas[-1].transform=np.matmul(tr.translate(pez[0]*h-Width/2, pez[1]*h-Lenght/2, pez[2]*h-Height/2),tr.uniformScale(3*h/4))
     a.childs+=[es.toGPUShape(bs.createColorFish(1,0,0))]
     a.transform=np.matmul(tr.translate(pez[0]*h-Width/2, pez[1]*h-Lenght/2, pez[2]*h-Height/2),tr.uniformScale(3*h/4))
     peces_a.childs+=[a]

    #peces b
    peces_b = sg.SceneGraphNode('peces_b')
    for i in range(len(voxeles_b)):
        pez = voxeles_b[i]
        b = sg.SceneGraphNode('pez_b' + str(i))
        colas.append(sg.SceneGraphNode('cola_b' + str(i)))
        colas[-1].childs += [es.toGPUShape(bs.Shape(vertices, indices), GL_REPEAT, GL_NEAREST)]
        colas[-1].transform = np.matmul(
            tr.translate(pez[0] * h - Width / 2, pez[1] * h - Lenght / 2, pez[2] * h - Height / 2),
            tr.uniformScale(3 * h / 4))
        b.childs += [es.toGPUShape(bs.createColorFish(0, 1, 0))]
        b.transform=np.matmul(tr.translate(pez[0]*h-Width/2, pez[1]*h-Lenght/2, pez[2]*h-Height/2),tr.uniformScale(3*h/4))
        peces_b.childs += [b]

    #peces c
    peces_c = sg.SceneGraphNode('peces_c')
    for i in range(len(voxeles_c)):
        pez = voxeles_c[i]
        c = sg.SceneGraphNode('pez_c' + str(i))
        colas.append(sg.SceneGraphNode('cola_c' + str(i)))
        colas[-1].childs += [es.toGPUShape(bs.Shape(vertices, indices), GL_REPEAT, GL_NEAREST)]
        colas[-1].transform = np.matmul(
            tr.translate(pez[0] * h - Width / 2, pez[1] * h - Lenght / 2, pez[2] * h - Height / 2),
            tr.uniformScale(3 * h / 4))
        c.childs += [es.toGPUShape(bs.createColorFish(0, 0, 1))]
        c.transform=np.matmul(tr.translate(pez[0]*h-Width/2, pez[1]*h-Lenght/2, pez[2]*h-Height/2),tr.uniformScale(3*h/4))
        peces_c.childs += [c]

    peces=sg.SceneGraphNode('peces')
    peces.childs+=[peces_a,peces_b,peces_c]

    return acuario,peces, voxeles_area_a,voxeles_area_b,voxeles_area_c,colas


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, "aquarium-view", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)


    # Assembling the shader program
    pipeline = es.SimpleModelViewProjectionShaderProgram()

    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # asignando las variables de control y creando las shapes
    acuario,peces,voxeles_area_a,voxeles_area_b,voxeles_area_c,colas=generate_voxels(voxeles_a, voxeles_b, voxeles_c, Width, Lenght, Height, area_a,area_b,area_c)
    t0 = glfw.get_time()
    camera_theta = np.pi / 4
    camX = 10 * np.sin(camera_theta)
    camY = 10 * np.cos(camera_theta)
    transform = tr.translate(camX, camY, 0)
    d_region=10
    draw_a=False
    draw_b=False
    draw_c=False
    angulo=0
    direccion=0
    radio=10
    altura=5
    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1
        d_region+=dt

        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta += 2 * dt

        if (glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS):
            radio*=0.95
            altura*=0.95

        if (glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS):
            radio*=1.05
            altura*=1.05

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta -= 2 * dt


        if (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS) and d_region>0.2:
            draw_a=not draw_a
            d_region=0

        if (glfw.get_key(window, glfw.KEY_B) == glfw.PRESS) and d_region>0.2:
            draw_b=not draw_b
            d_region=0

        if (glfw.get_key(window, glfw.KEY_C) == glfw.PRESS) and d_region>0.2:
            draw_c=not draw_c
            d_region=0

        if camera_theta > 2 * np.pi: camera_theta -= 2 * np.pi
        if camera_theta < -2 * np.pi: camera_theta += 2 * np.pi

        # Setting up the view transform

        camX = radio * np.sin(camera_theta)
        camY = radio * np.cos(camera_theta)

        viewPos = np.array([camX, camY, altura])


        view = tr.lookAt(
            viewPos,
            np.array([0, 0, 0]),
            np.array([0, 0, 1])
        )

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        # Setting up the projection transform

        projection = tr.perspective(45, float(width) / float(height), 0.1, 100)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        sg.drawSceneGraphNode(acuario,pipeline,"model",GL_LINES)
        sg.drawSceneGraphNode(peces,pipeline,"model")
        if draw_a:
         sg.drawSceneGraphNode(voxeles_area_a, pipeline, "model")
        if draw_b:
         sg.drawSceneGraphNode(voxeles_area_b, pipeline, "model")
        if draw_c:
         sg.drawSceneGraphNode(voxeles_area_c, pipeline, "model")
        for x in colas:
         if angulo<np.pi/2 and direccion==0:
          x.transform=np.matmul(x.transform,tr.rotationZ(0.01))
          angulo+=0.01
         if angulo > np.pi / 2 and direccion == 0:
             direccion=1
         if angulo>-np.pi/2 and direccion==1:
             x.transform = np.matmul(x.transform, tr.rotationZ(-0.01))
             angulo -= 0.01
         if angulo < -np.pi / 2 and direccion == 1:
             direccion=0
         sg.drawSceneGraphNode(x,pipeline,"model")


        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()






