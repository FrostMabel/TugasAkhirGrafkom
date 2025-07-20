import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

rotate_x, rotate_y = 0, 0
translate_x, translate_y, translate_z = 0, 0, -6
scale = 1.0
current_object = "pyramid"

enable_ambient = True
enable_diffuse = True
enable_specular = True

light_position = [2.0, 2.0, 2.0, 1.0]
ambient_light = [0.2, 0.2, 0.2, 1.0]
diffuse_light = [0.7, 0.7, 0.7, 1.0]
specular_light = [1.0, 1.0, 1.0, 1.0]
shininess = [50.0]

def init_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

def update_lighting():
    if enable_ambient:
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)
    else:
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.0, 0.0, 0.0, 1.0])
    
    if enable_diffuse:
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)
    else:
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.0, 0.0, 0.0, 1.0])
    
    if enable_specular:
        glLightfv(GL_LIGHT0, GL_SPECULAR, specular_light)
        glMaterialfv(GL_FRONT, GL_SPECULAR, specular_light)
    else:
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])
    
    glMaterialfv(GL_FRONT, GL_SHININESS, shininess)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

def draw_pyramid():
    vertices = [
        (0, 1, 0),
        (-1, -1, 1),
        (1, -1, 1),
        (1, -1, -1),
        (-1, -1, -1)
    ]
    faces = [
        (0, 1, 2),
        (0, 2, 3),
        (0, 3, 4),
        (0, 4, 1)
    ]
    base = (1, 2, 3, 4)
    colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1)]
    
    glBegin(GL_TRIANGLES)
    for i, face in enumerate(faces):
        glColor3fv(colors[i])
        for v in face:
            glVertex3fv(vertices[v])
    glEnd()
    
    glBegin(GL_QUADS)
    glColor3fv(colors[4])
    for v in base:
        glVertex3fv(vertices[v])
    glEnd()

def draw_cube():
    vertices = [
        (-1, -1, -1),
        (1, -1, -1),
        (1, 1, -1),
        (-1, 1, -1),
        (-1, -1, 1),
        (1, -1, 1),
        (1, 1, 1),
        (-1, 1, 1)
    ]
    faces = [
        (0, 1, 2, 3),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (2, 3, 7, 6),
        (0, 3, 7, 4),
        (1, 2, 6, 5)
    ]
    colors = [
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
        (1, 1, 0),
        (1, 0, 1),
        (0, 1, 1)
    ]
    glBegin(GL_QUADS)
    for i, face in enumerate(faces):
        glColor3fv(colors[i])
        for v in face:
            glVertex3fv(vertices[v])
    glEnd()

def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (800 / 600), 0.1, 50.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(
        0, 0, 6,
        0, 0, 0,
        0, 1, 0
    )

def apply_transformations():
    glTranslatef(translate_x, translate_y, translate_z)
    glRotatef(rotate_x, 1, 0, 0)
    glRotatef(rotate_y, 0, 1, 0)
    glScalef(scale, scale, scale)

def main():

    print("Kontrol:")
    print("Tab: Ganti objek Piramida/Kubus")
    print("1: Toggle Ambient Light")
    print("2: Toggle Diffuse Light")
    print("3: Toggle Specular Light")

    global rotate_x, rotate_y, translate_x, translate_y, translate_z
    global scale, current_object
    global enable_ambient, enable_diffuse, enable_specular

    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("3D")

    glEnable(GL_DEPTH_TEST)
    init_lighting()
    setup_camera()

    clock = pygame.time.Clock()
    dragging = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return

            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    rotate_y -= 5
                if event.key == K_RIGHT:
                    rotate_y += 5
                if event.key == K_UP:
                    rotate_x -= 5
                if event.key == K_DOWN:
                    rotate_x += 5
                if event.key == K_w:
                    translate_z += 0.3
                if event.key == K_s:
                    translate_z -= 0.3
                if event.key == K_a:
                    translate_x -= 0.3
                if event.key == K_d:
                    translate_x += 0.3
                if event.key == K_q:
                    translate_y += 0.3
                if event.key == K_e:
                    translate_y -= 0.3
                if event.key == K_z:
                    scale += 0.1
                if event.key == K_x:
                    scale = max(0.1, scale - 0.1)

                if event.key == K_TAB:
                    current_object = "cube" if current_object == "pyramid" else "pyramid"

                if event.key == K_1:
                    enable_ambient = not enable_ambient
                if event.key == K_2:
                    enable_diffuse = not enable_diffuse
                if event.key == K_3:
                    enable_specular = not enable_specular

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            if event.type == MOUSEMOTION and dragging:
                dx, dy = event.rel
                rotate_y += dx * 0.5
                rotate_x += dy * 0.5

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        update_lighting()

        glPushMatrix()
        apply_transformations()
        if current_object == "pyramid":
            draw_pyramid()
        else:
            draw_cube()
        glPopMatrix()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
