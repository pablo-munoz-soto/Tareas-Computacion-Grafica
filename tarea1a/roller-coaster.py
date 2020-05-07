import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import csv
import transformations as tr
import easy_shaders as es
import scene_graph as sg
import basic_shapes as bs
import sys
import ex_curves as cu


puntos=[]
#leyendo el archivo y almacenando los puntos
with open(str(sys.argv[1])) as csv_file:
    csv_reader=csv.reader(csv_file, delimiter='\t')
    for row in csv_reader:
        puntos.append(', '.join(row))


i=0
while i<len(puntos):
   n=puntos[i].index(',')
   if 'x' in puntos[i]:
    puntos[i]=np.array([[float(puntos[i][1:n])/10, float(puntos[i][n+1:len(puntos[i])])/10, 1]],).T
   else:
     puntos[i]=np.array([[float(puntos[i][0:n])/10, float(puntos[i][n+1:len(puntos[i])])/10, 0]],).T
   i+=1

#implementando la funcion para leer inputs del teclado
def on_key(window, key, scancode, action, mods):
    global salto, caida, alturaSalto, n
    if action != glfw.PRESS:
        return

    if key == glfw.KEY_ESCAPE:
        sys.exit()

    if key == glfw.KEY_SPACE and caida==0 and salto==0:
        salto=1
        alturaSalto=n


#funcion que modela la curva en base a la lista de puntos
def createRiel(puntos):
    puntos = [np.array([[-0.4,0,0]]).T,np.array([[-0.3,0,0]]).T,np.array([[-0.2,0,0]]).T,np.array([[-0.1, 0, 0]]).T] + puntos + [np.array([[puntos[-1:][0][0]+0.1,puntos[-1:][0][1]/2,0]]).T,np.array([[puntos[-1:][0][0]+0.2, 0, 0]]).T,np.array([[puntos[-1:][0][0]+0.3, 0, 0]]).T]
    curvas=sg.SceneGraphNode("riel")
    subcurvas=[]
    for i in range(1,len(puntos)-2):
      if puntos[i][2][0]==0:
        Gmb=cu.spliceMatrix(puntos[i-1],puntos[i],puntos[i+1],puntos[i+2])
        #funcion que genera la spline de catmull-rom
        splicerCurve= cu.evalCurve(Gmb,1000)
        subcurvas+=[splicerCurve]
        splicer=sg.SceneGraphNode("splicer"+str(i))
        splicer.childs+=[es.toGPUShape(bs.createCurve(splicerCurve))]
        curvas.childs+=[splicer]
    return curvas,subcurvas


#funcion que crea la gpushape con la textura del cielo
def createSky():
    skyTexture = es.toGPUShape(bs.createTextureQuad("sky.jpg"), GL_REPEAT, GL_NEAREST)
    sky = sg.SceneGraphNode("sky")
    sky.transform=tr.uniformScale(2)
    sky.childs += [skyTexture]
    return sky


#funcion que crea las barras para decorar la montaña rusa
def createMetalBars(subcurvas):
    i=0
    barras=sg.SceneGraphNode('barras')
    for subcurva in subcurvas:
     barsGPU= es.toGPUShape(bs.createBars(subcurva))
     bar= sg.SceneGraphNode('bar'+str(i))
     bar.childs+=[barsGPU]
     barras.childs+=[bar]
     i+=1
    return barras


#funcion que crea el carrito y organiza las gpuShape anteriores
def createRollercoaster(puntos):
    #creando los cuadrados
    gpuBlackQuad = es.toGPUShape(bs.createColorQuad(0, 0, 0))
    gpuRedQuad = es.toGPUShape(bs.createColorQuad(1, 0, 0))
    gpuSkinQuad = es.toGPUShape(bs.createColorQuad(0.98,0.82,0.77))
    gpuGreenQuad= es.toGPUShape(bs.createColorQuad(0,1,0))
    gpuBlueQuad = es.toGPUShape(bs.createColorQuad(0, 0, 1))
    #creando la curva
    riel,subcurvas=createRiel(puntos)
    #creando las barras
    bars=createMetalBars(subcurvas)
    riel.childs+=[bars]
    riel.transform = np.matmul(tr.uniformScale(1.7), tr.translate(-0.29, -0.025, 0))
    curva=[]
    for subcurva in subcurvas:
        for punto in subcurva:
         curva.append(punto)

    #creando el carrito con los cuadrados
    body1scaled = sg.SceneGraphNode("body1scaled")
    body1scaled.transform = tr.scale(0.03,0.05,0)
    body1scaled.childs += [gpuRedQuad]

    body1 = sg.SceneGraphNode('body1')
    body1.transform=tr.translate(-0.005,0.05,0)
    body1.childs+=[body1scaled]

    head1scaled = sg.SceneGraphNode('head1scaled')
    head1scaled.transform = tr.uniformScale(0.025)
    head1scaled.childs += [gpuSkinQuad]

    head1=sg.SceneGraphNode('head1')
    head1.transform = tr.translate(-0.005,0.087,0)
    head1.childs += [head1scaled]

    person1 = sg.SceneGraphNode('person1')
    person1.transform= tr.translate(-0.04,0.005,0)
    person1.childs += [head1, body1]

    body2scaled = sg.SceneGraphNode("body2scaled")
    body2scaled.transform = tr.scale(0.03, 0.05, 0)
    body2scaled.childs += [gpuBlueQuad]

    body2 = sg.SceneGraphNode('body2')
    body2.transform = tr.translate(-0.0025, 0.05, 0)
    body2.childs += [body2scaled]

    head2scaled = sg.SceneGraphNode('head2scaled')
    head2scaled.transform = tr.uniformScale(0.025)
    head2scaled.childs += [gpuSkinQuad]

    head2 = sg.SceneGraphNode('head1')
    head2.transform = tr.translate(-0.0025, 0.087, 0)
    head2.childs += [head2scaled]

    person2 = sg.SceneGraphNode('person2')
    person2.transform = tr.translate(-0.003, 0.005, 0)
    person2.childs += [head2, body2]

    body3scaled = sg.SceneGraphNode("body3scaled")
    body3scaled.transform = tr.scale(0.03, 0.05, 0)
    body3scaled.childs += [gpuGreenQuad]

    body3 = sg.SceneGraphNode('body3')
    body3.transform = tr.translate(-0.0025, 0.05, 0)
    body3.childs += [body3scaled]

    head3scaled = sg.SceneGraphNode('head3scaled')
    head3scaled.transform = tr.uniformScale(0.025)
    head3scaled.childs += [gpuSkinQuad]

    head3 = sg.SceneGraphNode('head3')
    head3.transform = tr.translate(-0.0035, 0.087, 0)
    head3.childs += [head3scaled]

    person3 = sg.SceneGraphNode('person2')
    person3.transform = tr.translate(0.04, 0.005, 0)
    person3.childs += [head3, body3]

    wheel = sg.SceneGraphNode("wheel")
    wheel.transform = tr.uniformScale(0.025)
    wheel.childs += [gpuBlackQuad]


    frontWheel = sg.SceneGraphNode("frontWheel")
    frontWheel.transform = tr.translate(0.0375, -0.0375, 0)
    frontWheel.childs += [wheel]

    backWheel = sg.SceneGraphNode("backWheel")
    backWheel.transform = tr.translate(-0.0375, -0.0375, 0)
    backWheel.childs += [wheel]

    chasis = sg.SceneGraphNode("chasis")
    chasis.transform = tr.scale(0.125, 0.0625, 0.0625)
    chasis.childs += [gpuRedQuad]

    rollercoaster = sg.SceneGraphNode("rollercoaster")
    rollercoaster.childs += [chasis]
    rollercoaster.childs += [frontWheel]
    rollercoaster.childs += [backWheel]
    rollercoaster.childs += [person1, person2, person3]
    rollercoaster.transform=tr.uniformScale(0.8)

    traslatedRollercoaster = sg.SceneGraphNode("traslatedRollercoaster")
    traslatedRollercoaster.transform = tr.translate(-0.9, 0, 0)
    traslatedRollercoaster.childs += [rollercoaster]

    final= sg.SceneGraphNode("final")
    final.transform=tr.translate(0,-0.3,0)
    final.childs += [traslatedRollercoaster,riel]
    return final,curva



#iniciando el programa
if __name__ == "__main__":

    # iniciando glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Roller Coaster", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    #creando la gpuShape
    rollercoaster, curva = createRollercoaster(puntos)
    #almacenando donde no hay riel en la figura
    cortes=[]
    for punto in curva:
        if punto[2]==1:cortes.append(np.array([punto[0],punto[1],0]))
    #creando la gpuShape de la textura
    sky = createSky()

    glClearColor(1, 1, 1, 1.0)

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    #asignando las variables necesarias para controlar el movimiento
    t=0
    n=600
    vacio=0
    contador=0
    salto=0
    contadorSalto=0
    caida=0
    alturaSalto=0
    alturaCaida=0
    while not glfw.window_should_close(window):

        if len(curva)-n<20: sys.exit()

        glfw.poll_events()


        glClear(GL_COLOR_BUFFER_BIT)


        pipeline2 = es.SimpleTextureTransformShaderProgram()

        glUseProgram(pipeline2.shaderProgram)



        sg.drawSceneGraphNode(sky, pipeline2, "transform")


        pipeline = es.SimpleTransformShaderProgram()


        glUseProgram(pipeline.shaderProgram)

        riel=sg.findNode(rollercoaster,'riel')
        #creando el movimiento del rollercoaster
        riel.transform=np.matmul(tr.uniformScale(1.7), tr.translate(-0.29-0.0001*int(t), -0.025, 0))
        carro=sg.findNode(rollercoaster,"rollercoaster")
        #evitando que se indetermine el angulo
        while curva[n][0] - curva[n - 1][0] == 0:
            n+=1
            t+=1
        #calculando el angulo de rotacion del carrito
        angulo=np.arctan((curva[n][1]-curva[n-1][1])/(curva[n][0]-curva[n-1][0]))

        #viendo si el carrito esta en el vacio
        for punto in cortes:
         if (0<punto[0] - curva[n][0] <= 0.002)  and vacio==0:
            vacio=1
            contador=0
        if contador==50:
            contador=0
            vacio=0

        #aplicando la rotacion
        carro.transform=np.matmul(tr.rotationZ(angulo),tr.uniformScale(0.8))
        carro=sg.findNode(rollercoaster,"traslatedRollercoaster")
        #si no esta saltando ni en caida el carrito sigue la pista
        if salto==0 and caida==0:
         carro.transform=tr.translate(-0.9, curva[n][1]*1.7, 0)

        #contador para ver la duracion del salto
        if salto==1: contadorSalto+=1
        #si el contador es menor a 50 el carrito esta subiendo
        if salto==1 and contadorSalto<50 :
            carro.transform = tr.translate(-0.9, curva[alturaSalto][1]* 1.7 +contadorSalto*0.01, 0)

        #si el contador es mayor a 50 el carrito esta bajando
        if salto==1 and contadorSalto>=50 :
            carro.transform = tr.translate(-0.9, curva[alturaSalto][1] * 1.7-(contadorSalto-50)*0.01+0.5, 0)

        #si detecta que el carrito aterrizó en el riel se detiene el salto y se vuelve a estado inicial
        if curva[alturaSalto][1] * 1.7-(contadorSalto-50)*0.01+0.5-curva[n][1]*1.7<0.001 and salto==1:
            contadorSalto = 0
            salto = 0

        #contador para ver la duracion del vacio
        if vacio==1:
            contador+=1

        #si el carrito entra al vacio sin haber saltado se inicia la secuencia de caida
        if vacio==1 and salto==0 or caida>0:
            if alturaCaida==0:
                alturaCaida=n
            carro.transform=tr.translate(-0.9, curva[alturaCaida][1]*1.7-0.01*caida, 0)
            caida+=1

        #si el carrito aterriza en el riel debido a la caida se retorna al estado inicial
        if 0<=curva[alturaCaida][1] * 1.7 - caida * 0.01 - curva[n][1] * 1.7 <= 0.02 and caida > 10:
            alturaCaida=0
            caida=0


        #si no se esta en el vacio se sigue avanzando por el riel
        if vacio==0:
         n+=20
        sg.drawSceneGraphNode(rollercoaster, pipeline, "transform")


        #detectando si el carrito se cae hacia abajo de la pantalla
        if curva[alturaCaida][1] * 1.7 - caida * 0.01<-1 or curva[alturaSalto][1] * 1.7-(contadorSalto-50)*0.01<-1:
            sys.exit()


        t += 20


        glfw.swap_buffers(window)

    glfw.terminate()
