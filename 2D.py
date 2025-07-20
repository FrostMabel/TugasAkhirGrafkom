import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import sys

objects = []
current_object = None
drawing = False
object_type = 'line'
color_list = [
    (1, 1, 1), (1, 0, 0), (0, 1, 0),
    (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1)
]
color_index = 0
color = color_list[color_index]
line_width = 1.0
window_corners = None
clipping_active = False

dragging_window = False
resizing_window = False
drag_offset = [0, 0]
resize_start = None

class Object2D:
    def __init__(self, type, vertices, color, line_width):
        self.type = type
        self.vertices = vertices
        self.color = color
        self.line_width = line_width
        self.translation = [0.0, 0.0]
        self.rotation = 0.0
        self.scale = [1.0, 1.0]
    
    def draw(self):
        glColor3f(*self.color)
        glLineWidth(self.line_width)
        glPushMatrix()
        glTranslatef(*self.translation, 0)
        glRotatef(self.rotation, 0, 0, 1)
        glScalef(*self.scale, 1)

        if self.type == 'point':
            glBegin(GL_POINTS)
            glVertex2f(*self.vertices[0])
            glEnd()
        elif self.type == 'line':
            glBegin(GL_LINES)
            for v in self.vertices:
                glVertex2f(*v)
            glEnd()
        elif self.type == 'square':
            glBegin(GL_LINE_LOOP)
            for v in self.vertices:
                glVertex2f(*v)
            glEnd()
        elif self.type == 'ellipse':
            if len(self.vertices) < 2:
                glPopMatrix()
                return
            glBegin(GL_LINE_LOOP)
            center = self.vertices[0]
            radius_x = abs(self.vertices[1][0] - center[0])
            radius_y = abs(self.vertices[1][1] - center[1])
            for i in range(360):
                angle = math.radians(i)
                x = center[0] + radius_x * math.cos(angle)
                y = center[1] + radius_y * math.sin(angle)
                glVertex2f(x, y)
            glEnd()
        glPopMatrix()

def init():
    pygame.init()
    display = (800, 600)
    pygame.display.set_caption("2D")
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluOrtho2D(-400, 400, -300, 300)
    glPointSize(5.0)
    glClearColor(0.0, 0.0, 0.0, 1.0)

def draw_window():
    if window_corners and None not in window_corners:
        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(window_corners[0][0], window_corners[0][1])
        glVertex2f(window_corners[1][0], window_corners[0][1])
        glVertex2f(window_corners[1][0], window_corners[1][1])
        glVertex2f(window_corners[0][0], window_corners[1][1])
        glEnd()

def draw_resize_handle():
    if window_corners and None not in window_corners:
        x0, y0 = window_corners[0]
        x1, y1 = window_corners[1]
        xmax = max(x0, x1)
        ymin = min(y0, y1)

        size = 10
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(xmax - size, ymin)
        glVertex2f(xmax, ymin)
        glVertex2f(xmax, ymin + size)
        glVertex2f(xmax - size, ymin + size)
        glEnd()

def cohen_sutherland_clip(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8
    def compute_code(x, y):
        code = INSIDE
        if x < xmin: code |= LEFT
        elif x > xmax: code |= RIGHT
        if y < ymin: code |= BOTTOM
        elif y > ymax: code |= TOP
        return code
    
    code1 = compute_code(x1, y1)
    code2 = compute_code(x2, y2)
    accept = False

    while True:
        if not (code1 | code2):
            accept = True
            break
        elif code1 & code2:
            break
        else:
            x, y = 0, 0
            code_out = code1 if code1 else code2
            if code_out & TOP:
                x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
                y = ymax
            elif code_out & BOTTOM:
                x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
                y = ymin
            elif code_out & RIGHT:
                y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
                x = xmax
            elif code_out & LEFT:
                y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
                x = xmin
            if code_out == code1:
                x1, y1 = x, y
                code1 = compute_code(x1, y1)
            else:
                x2, y2 = x, y
                code2 = compute_code(x2, y2)
    return [(x1, y1), (x2, y2)] if accept else None

def main():
    global current_object, drawing, object_type, color, color_index
    global line_width, window_corners, clipping_active
    global dragging_window, resizing_window, drag_offset, resize_start

    init()
    print("Kontrol:\n1: Titik | 2: Garis | 3: Persegi | 4: Ellipse")
    print("c: Ganti warna | w: Ganti ketebalan")
    print("t: Translasi | r: Rotasi | s: Skala")
    print("n: Buat window | v: Toggle clipping")
    print("Drag window / resize dengan mouse")
    print("ESC: Keluar")

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                x = x - 400
                y = 300 - y

                if window_corners and None not in window_corners:
                    x0, y0 = window_corners[0]
                    x1, y1 = window_corners[1]
                    xmin, xmax = min(x0, x1), max(x0, x1)
                    ymin, ymax = min(y0, y1), max(y0, y1)

                    if abs(x - xmax) < 10 and abs(y - ymin) < 10:
                        resizing_window = True
                        continue
                    elif xmin <= x <= xmax and ymin <= y <= ymax:
                        dragging_window = True
                        drag_offset = [x - xmin, y - ymin]
                        continue

                if object_type == 'point':
                    objects.append(Object2D('point', [(x, y)], color, line_width))
                elif object_type in ['line', 'square', 'ellipse']:
                    if not drawing:
                        current_object = Object2D(object_type, [(x, y)], color, line_width)
                        drawing = True
                    else:
                        if object_type == 'line':
                            current_object.vertices.append((x, y))
                            objects.append(current_object)
                            drawing = False
                        elif object_type == 'square' and len(current_object.vertices) == 1:
                            current_object.vertices.append((x, y))
                            p1, p2 = current_object.vertices
                            current_object.vertices = [p1, (p2[0], p1[1]), p2, (p1[0], p2[1])]
                            objects.append(current_object)
                            drawing = False
                        elif object_type == 'ellipse' and len(current_object.vertices) == 1:
                            current_object.vertices.append((x, y))
                            objects.append(current_object)
                            drawing = False

            elif event.type == MOUSEBUTTONUP:
                dragging_window = False
                resizing_window = False

            elif event.type == MOUSEMOTION:
                x, y = pygame.mouse.get_pos()
                x = x - 400
                y = 300 - y

                if dragging_window and window_corners and None not in window_corners:
                    dx = x - window_corners[0][0] - drag_offset[0]
                    dy = y - window_corners[0][1] - drag_offset[1]
                    window_corners[0] = (window_corners[0][0] + dx, window_corners[0][1] + dy)
                    window_corners[1] = (window_corners[1][0] + dx, window_corners[1][1] + dy)

                elif resizing_window and window_corners and None not in window_corners:
                    window_corners[1] = (x, y)

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == K_1: object_type = 'point'
                elif event.key == K_2: object_type = 'line'
                elif event.key == K_3: object_type = 'square'
                elif event.key == K_4: object_type = 'ellipse'
                elif event.key == K_c:
                    color_index = (color_index + 1) % len(color_list)
                    color = color_list[color_index]
                    print(f"Warna: {color}")
                elif event.key == K_w:
                    line_width = line_width + 1 if line_width < 10 else 1
                elif event.key == K_t and objects:
                    obj = objects[-1]
                    obj.translation[0] += 10
                    obj.translation[1] += 10
                elif event.key == K_r and objects:
                    objects[-1].rotation += 15
                elif event.key == K_s and objects:
                    objects[-1].scale[0] *= 1.1
                    objects[-1].scale[1] *= 1.1
                elif event.key == K_n:
                    if not window_corners:
                        window_corners = [None, None]
                    x, y = pygame.mouse.get_pos()
                    x = x - 400
                    y = 300 - y
                    if window_corners[0] is None:
                        window_corners[0] = (x, y)
                    else:
                        window_corners[1] = (x, y)
                elif event.key == K_v:
                    clipping_active = not clipping_active
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if clipping_active and window_corners and None not in window_corners:
            xmin = min(window_corners[0][0], window_corners[1][0])
            xmax = max(window_corners[0][0], window_corners[1][0])
            ymin = min(window_corners[0][1], window_corners[1][1])
            ymax = max(window_corners[0][1], window_corners[1][1])
            for obj in objects:
                if obj.type == 'line':
                    clipped = cohen_sutherland_clip(
                        obj.vertices[0][0], obj.vertices[0][1],
                        obj.vertices[1][0], obj.vertices[1][1],
                        xmin, ymin, xmax, ymax
                    )
                    if clipped:
                        Object2D(obj.type, clipped, (0, 1, 0), obj.line_width).draw()
                else:
                    all_inside = all(
                        xmin <= v[0] <= xmax and ymin <= v[1] <= ymax
                        for v in obj.vertices
                    )
                    if all_inside:
                        Object2D(obj.type, obj.vertices, (0, 1, 0), obj.line_width).draw()
                    else:
                        obj.draw()
        else:
            for obj in objects:
                obj.draw()

        draw_window()
        draw_resize_handle()

        if drawing and current_object:
            current_object.draw()

        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()
