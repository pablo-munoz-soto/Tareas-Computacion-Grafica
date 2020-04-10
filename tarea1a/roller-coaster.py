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
puntos=[]
with open(str(sys.argv[1])) as csv_file:
    csv_reader=csv.reader(csv_file, delimiter='\t')
    for row in csv_reader:
        puntos.append(', '.join(row))

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return

    if key == glfw.KEY_ESCAPE:
        sys.exit()

    else:
        print('Unknown key')


def createRollercoaster():
    gpuBlackQuad = es.toGPUShape(bs.createColorQuad(0, 0, 0))
    gpuRedQuad = es.toGPUShape(bs.createColorQuad(1, 0, 0))
    gpuSkinQuad = es.toGPUShape(bs.createColorQuad(0.99,0.86,0.79))
    gpuGreenQuad= es.toGPUShape(bs.createColorQuad(0,1,0))
    gpuBlueQuad = es.toGPUShape(bs.createColorQuad(0, 0, 1))


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
    rollercoaster.childs += [chasis]
    rollercoaster.childs += [frontWheel]
    rollercoaster.childs += [backWheel]
    rollercoaster.childs += [person1, person2, person3]

    traslatedRollercoaster = sg.SceneGraphNode("traslatedCar")
    traslatedRollercoaster.transform = tr.translate(-0.9, 0, 0)
    traslatedRollercoaster.childs += [rollercoaster]

    return traslatedRollercoaster


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

    # Assembling the shader program (pipeline) with both shaders
    pipeline = es.SimpleTransformShaderProgram()

    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(1, 1, 1, 1.0)

    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)
        rollercoaster=createRollercoaster()
        # Drawing the roller coaster
        sg.drawSceneGraphNode(rollercoaster, pipeline, "transform")

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    glfw.terminate()