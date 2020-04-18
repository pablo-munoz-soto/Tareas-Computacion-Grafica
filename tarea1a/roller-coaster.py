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
"with open(str(sys.argv[1])) as csv_file:"
with open("track.txt") as csv_file:
    csv_reader=csv.reader(csv_file, delimiter='\t')
    for row in csv_reader:
        puntos.append(', '.join(row))
i=0
while i<len(puntos):
   if 'x' in puntos[i]:
    puntos[i]=np.array([[float(puntos[i][1])/10, float(puntos[i][3])/10, 1]],).T
   else:
     puntos[i]=np.array([[float(puntos[i][0])/10, float(puntos[i][2])/10, 0]],).T
   i+=1
def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return

    if key == glfw.KEY_ESCAPE:
        sys.exit()

    else:
        print('Unknown key')

def createRiel(puntos):
    puntos = [np.array([[-0.4,0,0]]).T,np.array([[-0.3,0,0]]).T,np.array([[-0.2,0,0]]).T,np.array([[-0.1, 0, 0]]).T] + puntos + [np.array([[puntos[-1:][0][0]+0.1,puntos[-1:][0][1]/2,0]]).T,np.array([[puntos[-1:][0][0]+0.2, 0, 0]]).T,np.array([[puntos[-1:][0][0]+0.3, 0, 0]]).T]
    curvas=sg.SceneGraphNode("curvas")
    subcurvas=[]
    for i in range(1,len(puntos)-2):
      if puntos[i][2][0]==0:
        Gmb=cu.spliceMatrix(puntos[i-1],puntos[i],puntos[i+1],puntos[i+2])
        splicerCurve= cu.evalCurve(Gmb,1000)
        subcurvas+=[splicerCurve]
        splicer=sg.SceneGraphNode("splicer"+str(i))
        splicer.childs+=[es.toGPUShape(bs.createCurve(splicerCurve))]
        curvas.childs+=[splicer]

    curvas.transform=np.matmul(tr.uniformScale(1.7),tr.translate(-0.29,-0.025,0))
    return curvas,subcurvas

def createSky():
    skyTexture = es.toGPUShape(bs.createTextureQuad("sky.jpg"), GL_REPEAT, GL_NEAREST)
    sky = sg.SceneGraphNode("sky")
    sky.transform=tr.uniformScale(2)
    sky.childs += [skyTexture]
    return sky

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

def createRollercoaster(puntos):
    gpuBlackQuad = es.toGPUShape(bs.createColorQuad(0, 0, 0))
    gpuRedQuad = es.toGPUShape(bs.createColorQuad(1, 0, 0))
    gpuSkinQuad = es.toGPUShape(bs.createColorQuad(0.98,0.82,0.77))
    gpuGreenQuad= es.toGPUShape(bs.createColorQuad(0,1,0))
    gpuBlueQuad = es.toGPUShape(bs.createColorQuad(0, 0, 1))
    riel,subcurvas=createRiel(puntos)
    bars=createMetalBars(subcurvas)
    riel.childs+=[bars]


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

    wheelRotation = sg.SceneGraphNode("wheelRotation")
    wheelRotation.childs += [wheel]

    # Instanciating 2 wheels, for the front and back parts
    frontWheel = sg.SceneGraphNode("frontWheel")
    frontWheel.transform = tr.translate(0.0375, -0.0375, 0)
    frontWheel.childs += [wheelRotation]

    backWheel = sg.SceneGraphNode("backWheel")
    backWheel.transform = tr.translate(-0.0375, -0.0375, 0)
    backWheel.childs += [wheelRotation]

    # Creating the chasis of the car
    chasis = sg.SceneGraphNode("chasis")
    chasis.transform = tr.scale(0.125, 0.0625, 0.0625)
    chasis.childs += [gpuRedQuad]

    rollercoaster = sg.SceneGraphNode("rollercoaster")
    rollercoaster.transform= tr.uniformScale(0.8)
    rollercoaster.childs += [chasis]
    rollercoaster.childs += [frontWheel]
    rollercoaster.childs += [backWheel]
    rollercoaster.childs += [person1, person2, person3]

    traslatedRollercoaster = sg.SceneGraphNode("traslatedCar")
    traslatedRollercoaster.transform = tr.translate(-0.9, 0, 0)
    traslatedRollercoaster.childs += [rollercoaster]

    final= sg.SceneGraphNode("final")
    final.childs += [traslatedRollercoaster,riel]
    return final


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, "2D cars via scene graph", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)




    # Setting up the clear screen color
    glClearColor(1, 1, 1, 1.0)

    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)
        # Assembling the shader program (pipeline) with both shaders
        pipeline2 = es.SimpleTextureTransformShaderProgram()

        glUseProgram(pipeline2.shaderProgram)

        sky = createSky()

        sg.drawSceneGraphNode(sky, pipeline2, "transform")


        pipeline = es.SimpleTransformShaderProgram()

        # Telling OpenGL to use our shader program
        glUseProgram(pipeline.shaderProgram)
        rollercoaster=createRollercoaster(puntos)
        # Drawing the roller coaster
        sg.drawSceneGraphNode(rollercoaster, pipeline, "transform")


        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    glfw.terminate()