import math
import random
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

window_width = 800
window_height = 600

score = 0
redballX = 50
redballY = 100
starX = random.randint(20, window_width-80)
starY = random.randint(100, 300)
pause = False
eye_open = True
game_over = False
smile = True
jumping_direction = 1
jumping = False
active_timer = True
stoneX = window_width
stoneY = 120
stone_speed = 10
stone_exists = False
lives = 3
stone_radius = random.randint(37,46)

def find_zone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    
    if abs(dx) >= abs(dy):  
        if dx >= 0:  # Right side
            return 0 if dy >= 0 else 7  # Upper-right (0) or Lower-right (7)
        else:  # Left side
            return 3 if dy >= 0 else 4  # Upper-left (3) or Lower-left (4)
    else: 
        if dy >= 0:  # Upper half
            return 1 if dx >= 0 else 2  # Upper-right (1) or Upper-left (2)
        else:  # Lower half
            return 6 if dx >= 0 else 5  # Lower-right (6) or Lower-left (5)
def convert_to_zone0(x, y, zone):
    # Dictionary mapping each zone to the corresponding transformation
    transformations = {
        0: (x, y),
        1: (y, x),
        2: (y, -x),
        3: (-x, y),
        4: (-x, -y),
        5: (-y, -x),
        6: (-y, x),
        7: (x, -y),
    }
    
    # Return the transformation corresponding to the zone, default to (x, y) if zone is invalid
    return transformations.get(zone, (x, y))
def convert_from_zone0(x, y, zone):
    # Dictionary mapping each zone to the corresponding reverse transformation
    reverse_transformations = {
        0: (x, y),
        1: (y, x),
        2: (-y, x),
        3: (-x, y),
        4: (-x, -y),
        5: (-y, -x),
        6: (y, -x),
        7: (x, -y),
    }

    # Return the reverse transformation corresponding to the zone, default to (x, y) if zone is invalid
    return reverse_transformations.get(zone, (x, y))

def midpoint_line(x1, y1, x2, y2):
    zone = find_zone(x1, y1, x2, y2)  # Determine the zone
    x1_z0, y1_z0 = convert_to_zone0(x1, y1, zone)
    x2_z0, y2_z0 = convert_to_zone0(x2, y2, zone)

    dx = x2_z0 - x1_z0
    dy = y2_z0 - y1_z0
    d = 2 * dy - dx
    dE = 2 * dy
    dNE = 2 * (dy - dx)

    x, y = x1_z0, y1_z0 

    glPointSize(2)
    glBegin(GL_POINTS)
    while x <= x2_z0:  
        x_orig, y_orig = convert_from_zone0(x, y, zone)
        glVertex2f(x_orig, y_orig)
        if d < 0:
            d += dE
        else:
            d += dNE
            y += 1
        x += 1
    glEnd()

def BG_midpoint_line(x1, y1, x2, y2):
    zone = find_zone(x1, y1, x2, y2)  # Determine the zone
    x1_z0, y1_z0 = convert_to_zone0(x1, y1, zone)
    x2_z0, y2_z0 = convert_to_zone0(x2, y2, zone)

    dx = x2_z0 - x1_z0
    dy = y2_z0 - y1_z0
    d = 2 * dy - dx
    dE = 2 * dy
    dNE = 2 * (dy - dx)

    x, y = x1_z0, y1_z0 
    #give a size of the point before begining
    glPointSize(100)
    glBegin(GL_POINTS)
    while x <= x2_z0:  
        x_orig, y_orig = convert_from_zone0(x, y, zone)
        glVertex2f(x_orig, y_orig)
        if d < 0:
            d += dE
        else:
            d += dNE
            y += 1
        x += 1
    glEnd()

def midpoint_circle(cx, cy, r):
    x = 0
    y = r
    d = 1 - r
    points = []

    while x <= y:
        points.extend([
            (x + cx, y + cy), (-x + cx, y + cy), (x + cx, -y + cy), (-x + cx, -y + cy), (y + cx, x + cy), (-y + cx, x + cy), (y + cx, -x + cy), (-y + cx, -x + cy)
        ]) # Adduing all 8 symmetric points

        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1

        x += 1

    return points

# def draw_circle(cx, cy, r, color, segments=100):
#     glColor3f(*color)
#     glBegin(GL_LINE_LOOP)  # Use GL_POLYGON for filled circle
#     for i in range(segments):
#         theta = 2.0 * math.pi * i / segments
#         x = cx + r * math.cos(theta)
#         y = cy + r * math.sin(theta)
#         glVertex2f(x, y)
#     glEnd()

def draw_circle(cx, cy, r, color):
    glColor3f(*color)
    glPointSize(5)
    glBegin(GL_POINTS)
    for x, y in midpoint_circle(cx, cy, r):
        glVertex2f(x, y)
    glEnd()

def draw_ellipse(xc, yc, a, b, color):
    glColor3f(*color)
    glBegin(GL_POINTS)
    for angle in range(360):
        theta = math.radians(angle)
        x = xc + int(a * math.cos(theta))
        y = yc + int(b * math.sin(theta))
        glVertex2f(x, y)
    glEnd()

# def draw_ellipse(xc, yc, a, b, color, segments=100):
#     glColor3f(*color)
#     glBegin(GL_LINE_LOOP)  # use GL_POLYGON if you want a filled ellipse
#     for i in range(segments):
#         theta = 2.0 * math.pi * i / segments
#         x = xc + a * math.cos(theta)
#         y = yc + b * math.sin(theta)
#         glVertex2f(x, y)
#     glEnd()

def toggle_eyes(value):
    global eye_open, game_over, pause
    if not game_over:
        eye_open = not eye_open  # Toggle the state of the eyes
        glutPostRedisplay() 
        glutTimerFunc(700, toggle_eyes, 0)
def redBall(xc, yc):
    global eye_open, pause, game_over, smile
    radius = 30

    # Draw the red bal
    glColor3f(1.0, 0.0, 0.0)  # Red
    for r in range(1, radius + 1,15):
        for x, y in midpoint_circle(xc, yc, r):
            draw_circle(x, y, 15, (1.0, 0.0, 0.0)) #red Ball

    if eye_open and not game_over:
        for x, y in midpoint_circle(xc - 10, yc + 10, 3):
            draw_ellipse(x, y, 5, 2, (1.0, 1.0, 1.0))  # Left eye (open, ellipse)
        for x, y in midpoint_circle(xc + 10, yc + 10, 3):
            draw_ellipse(x, y, 5, 2, (1.0, 1.0, 1.0)) # Right eye (open, ellipse)
        # Draw the pupils
        for x, y in midpoint_circle(xc - 10, yc + 10, 1):
            draw_circle(x, y, 1, (0, 0, 0))
        for x, y in midpoint_circle(xc + 10, yc + 10, 1):
            draw_circle(x, y, 1, (0, 0, 0))

    elif not eye_open and not game_over:
        # Draw closed eyes (lines)
        glColor3f(0.0, 0.0, 0.0)  # Black
        midpoint_line(xc - 15, yc + 10, xc - 5, yc + 10)
        midpoint_line(xc + 5, yc + 10, xc + 15, yc + 10)
    
    if game_over:
        # Draw the eyes in a sad expression (X X)
        glColor3f(0.0, 0.0, 0.0)
       
        midpoint_line(xc - 15, yc + 10, xc - 5, yc + 10)
        midpoint_line(xc - 10, yc + 5, xc - 10, yc + 15)
        
        midpoint_line(xc + 5, yc + 10, xc + 15, yc + 10)
        midpoint_line(xc + 10, yc + 5, xc + 10, yc + 15)
        

    if game_over:
       smile = False 
    draw_mouth(xc, yc, radius - 5)

def draw_mouth(xc, yc, r):
    # Drawing mouth smile or sad based on the smile flag
    glColor3f(0.0, 0.0, 0.0)  # Black
    glPointSize(2)
    glBegin(GL_POINTS)
    if smile:
        for angle in range(210, 330): 
            angle_rad = math.radians(angle)
            x = xc + int(r * math.cos(angle_rad))
            y = yc + int(r * math.sin(angle_rad))+5  # smile
            glVertex2f(x, y)
        glEnd()
    else:
        for angle in range(40, 140):  
            angle_rad = math.radians(angle)
            x = xc + int(r * math.cos(angle_rad))
            y = yc + int(r * math.sin(angle_rad)) - 30  # sad
            glVertex2f(x, y)
        glEnd()

def keyboard(key, x, y):
    global jumping, redballX, redballY, window_height, window_width, game_over, pause
    if game_over or pause:
        return
    speed = 10
    global jumping, redballX, redballY, window_height, window_width
    if key == b'a':
        redballX = max(30, redballX-speed)
    elif key == b'd':
        redballX = min(window_width-30, redballX+speed)
    
    elif key == b'w':
        jumping = True
        jump()
def special_keys(key, x, y):
    global jumping, redballX, redballY, window_height, window_width, game_over, pause
    if game_over or pause:
        return
    speed = 10
    global jumping, redballX, redballY, window_height, window_width
    if key == GLUT_KEY_LEFT:
        redballX = max(30, redballX-speed)
    elif key == GLUT_KEY_RIGHT:
        redballX = min(window_width-30, redballX+speed)
    
    elif key == GLUT_KEY_UP:
        jumping = True
        jump()

def jump():
    global redballY, jumping, jumping_direction
    if jumping:
        redballY += jumping_direction*6
        if redballY >= 280:
            jumping_direction = -1
        elif redballY <= 100:
            redballY = 100
            jumping_direction = 1
            jumping = False

def draw_star(sx, sy):
    glColor3f(1.0, 1.0, 0.0)
    midpoint_line(sx-20, sy+5, sx-5, sy+5)
    midpoint_line(sx-5, sy+5, sx, sy+20)
    midpoint_line(sx, sy+20, sx+5, sy+5)
    midpoint_line(sx+5, sy+5, sx+20, sy+5)
    midpoint_line(sx+20, sy+5, sx+10, sy)
    midpoint_line(sx+10, sy, sx+15, sy-15)
    midpoint_line(sx+15, sy-15, sx, sy-5)
    midpoint_line(sx, sy-5, sx-15, sy-15)
    midpoint_line(sx-15, sy-15, sx-10, sy)
    midpoint_line(sx-10, sy, sx-20, sy+5)
def collision_detector(px1, py1, pr1, px2, py2, pr2):
    #first boundary box
    p1_left = px1 - pr1
    p1_right = px1 + pr1
    p1_top = py1 + pr1
    p1_bottom = py1 - pr1

    #second boundary box
    p2_left = px2 - pr2
    p2_right = px2 + pr2
    p2_top = py2 + pr2
    p2_bottom = py2 - pr2

    # Check for collision
    if p1_right < p2_left or p1_left > p2_right or p1_top < p2_bottom or p1_bottom > p2_top:
        return False
    else:
        return True


def draw_stone(): 
    global stoneX, stoneY, stone_radius
    glColor3f(0.5, 0.5, 0.5)  # Gray
    for radius in range(1, stone_radius, 20):
        for x, y in midpoint_circle(stoneX, stoneY, radius):
            draw_circle(x, y, 20, (0.5, 0.5, 0.5))
        
def spawn_stone(value):
    global stone_exists
    stone_exists = True


def update(value):
    global redballX, redballY, starX, lives, starY, score, stoneX, stoneY, stone_exists,stone_speed, game_over,smile, pause,stone_radius,stone_speed
    if not pause and not game_over:
        glutPostRedisplay()
        
        jump()
        if collision_detector(redballX, redballY, 30, starX, starY, 20):
            global score
            score += 1
            new_starX = random.randint(20, window_width - 80)
            new_starY = random.randint(100, 300)
            while math.sqrt((new_starX - starX)**2 + (new_starY - starY)**2) < 150 or new_starX == starX or (starX-20<new_starX<starX+20) or new_starY == starY:
                new_starX = random.randint(20, window_width - 80)
                new_starY = random.randint(100, 300)
            starX, starY = new_starX, new_starY
        
         # Move the stone
        if stone_exists:
            stoneX -= stone_speed

            # Check collision with the red ball
            if collision_detector(redballX, redballY, 30, stoneX, stoneY, stone_radius):
                lives -= 1
                
                if lives == 0:
                    smile = False
                    game_over = True  # End the game on collision
                    
                else:
                    stoneX = window_width
                    stoneY = 100
                    stone_radius = random.randint(37,46)
                    stone_exists = False    
            # Remove stone if it moves off the screen and generate a new one after delay
            if stoneX < -20:
                stone_exists = False
                stoneX = window_width
                stoneY = 100 #random.randint(100, 300)
                stone_radius = random.randint(37,46)

        if not stone_exists:
            delay = random.randint(500, 1500)  # Random delay between 500ms to 1500ms
            glutTimerFunc(delay, spawn_stone, 0)
    if not game_over and not pause and active_timer:
        glutTimerFunc(30, update, 0)


##background
def background():
    # Sky
    for y in range(400, window_height, 80):
        glColor3f(0.5, 0.7, 1.0)  # Light blue
        BG_midpoint_line(0, y, window_width, y)

    # Grass Area
    for y in range(110, 400, 100):
        glColor3f(0.2, 0.6, 0.2)  # Green
        BG_midpoint_line(0, y, window_width, y)


    # # Underground Area
    for y in range(0, 50,20):
        glColor3f(0.5, 0.25, 0.0)  # Brown
        BG_midpoint_line(0, y, window_width, y)
    #draw cloudes
    
    cx1, cy1 = 100, 480 #using this, drawing all clouds

    glColor3f(1.0, 1.0, 1.0)  # White
    for r in range(1, 35, 20):
        for x, y in midpoint_circle(cx1, cy1, r):
            draw_circle(x, y, 20, (1.0, 1.0, 1.0)) #cloud1
            draw_circle(x+200, y-50, 20, (1.0, 1.0, 1.0)) #cloud2
            draw_circle(x+400, y, 20, (1.0, 1.0, 1.0)) #cloud3
    for r in range(1, 25, 15):  # Smaller circles
        for x, y in midpoint_circle(cx1, cy1, r):
            draw_circle(x+30, y, 10, (1.0, 1.0, 1.0))
            draw_circle(x-40, y, 10, (1.0, 1.0, 1.0))

            draw_circle(x+230, y-50, 10, (1.0, 1.0, 1.0))
            draw_circle(x+160, y-50, 10, (1.0, 1.0, 1.0))

            draw_circle(x+430, y, 10, (1.0, 1.0, 1.0))
            draw_circle(x+360, y, 10, (1.0, 1.0, 1.0))
    

    # Sun
    sun_center_x = window_width - 80  # Center of the sun
    sun_center_y = window_height - 100  
    sun_radius = 20

    glColor3f(1.0, 1.0, 0.0)  # Yellow
    for r in range(1, sun_radius + 1, 10): 
        for x, y in midpoint_circle(sun_center_x, sun_center_y, r):
            draw_circle(x, y, 10, (1.0, 1.0, 0.0))
    # sun rays
    glColor3f(1.0, 1.0, 0.0)
    for angle in range(0, 360, 30): 
        ray_length = sun_radius + 10
        ray_start_x = sun_center_x + int(sun_radius * math.cos(math.radians(angle)))
        ray_start_y = sun_center_y + int(sun_radius * math.sin(math.radians(angle)))
        ray_end_x = sun_center_x + int(ray_length * math.cos(math.radians(angle)))
        ray_end_y = sun_center_y + int(ray_length * math.sin(math.radians(angle)))
        midpoint_line(ray_start_x, ray_start_y, ray_end_x, ray_end_y)
    
def navbar():
    #Drawing the navigation bar

    global window_width, window_height, pause
    
    #drawing left arrow at the top left of my window dimensions
    glColor3f(0.0, 1.0, 1.0)
    midpoint_line(10, window_height - 30, 40, window_height - 30)  # Horizontal line
    midpoint_line(10, window_height - 30, 20, window_height - 20)  # Left side of the arrow
    midpoint_line(10, window_height - 30, 20, window_height - 40)  # Right side of the arrow

    # drawing pause or play button at the top middle of my window dimensions
    if pause:
        glColor3f(1.0, 0.5, 0.0)
        #(triangle)
        midpoint_line(window_width//2 - 5, window_height - 30, window_width//2 - 5, window_height - 60)  # left line of triangle
        midpoint_line(window_width//2 - 5, window_height - 30, window_width//2 + 15, window_height - 45)   # upper line of triangle
        midpoint_line(window_width//2 - 5, window_height - 60, window_width//2 + 15, window_height - 45)   # Bottom line of triangle
    else:
        glColor3f(0.0, 1.0, 0.0)
        #(two vertical line)
        midpoint_line(window_width//2 - 5, window_height - 20, window_width//2 - 5, window_height - 50) # Left bar
        midpoint_line(window_width//2 + 5, window_height - 20, window_width//2 + 5, window_height - 50)  # Right bar
    

    # Exit button (cross) at the top right of my window dimensions
    glColor3f(1.0, 0.0, 0.0) 
    midpoint_line(window_width-10, window_height-25, window_width - 40, window_height - 50)  # cross line 1
    midpoint_line(window_width-10, window_height - 50, window_width - 40, window_height-25)  #cross line2

def mouse(button, state, x, y):
    global pause, game_over, window_height, score, window_width

    y = window_height - y

    # Restart button (left arrow)
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if 10 <= x <= 40 and window_height - 40 <= y <= window_height - 20:
            print("Starting Over")
            reset_game() # Reset the game
            return

    # Play/Pause button
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if (window_width // 2 - 15) <= x <= (window_width // 2 + 15) and (window_height - 60) <= y <= (window_height - 30):
            
            pause = not pause  # Toggle the pause state
            if pause:
                print("Game Paused")
            else:
                print("Game Resumed")
                glutTimerFunc(30, update, 0)  # Ensure the update function resumes
            return 

    # Exit button (cross)
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if (window_width - 50) <= x <= (window_width - 20) and (window_height - 50) <= y <= (window_height - 20):
            print(f"Goodbye! Final Score: {score}")
            glutLeaveMainLoop()  # Terminate the game

    glutPostRedisplay()

def reset_game():
    global window_width, window_height, active_timer, jumping_direction, jumping, stoneX, stoneY, stone_speed, stone_exists, stone_radius, redballX, redballY, starX, starY, pause, score, game_over, eye_open, smile
    window_width = 800
    window_height = 600
    jumping_direction = 1
    jumping = False
    stoneX = window_width
    stoneY = 120
    stone_speed = 10
    stone_exists = False
    stone_radius = random.randint(37,46)
    redballX = 50
    redballY = 100
    starX = random.randint(20, window_width-80)
    starY = random.randint(100, 300)
    pause = False
    score = 0
    game_over = False
    eye_open = True
    smile = True
    lives = 3
    active_timer = True

def draw_lives():
    for i in range(lives):
        glColor3f(1.0, 0.0, 0.0)
        for x, y in midpoint_circle(20 + 20*i, window_height - 75, 3):
            draw_circle(x, y, 3, (1.0, 0.0, 0.0))
            
def display():
    glClear(GL_COLOR_BUFFER_BIT)
    #draw red ball
    background()
    
    navbar()
    draw_lives()
    redBall(redballX, redballY)
    draw_star(starX, starY)
    
    if stone_exists:
        draw_stone()

    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(10, window_height - 60)
    score_text = f"Score: {score}"
    for char in score_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    # Display game over message
    if game_over:
        glColor3f(1.0, 0.0, 0.0)
        glRasterPos2f(window_width // 2 - 50, window_height // 2)
        for char in "Game Over!":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        glRasterPos2f(window_width // 2 - 60, window_height // 2-20)
        for char in "Your Score: " + str(score):
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        


    glutSwapBuffers()

def init():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    gluOrtho2D(0, window_width, 0, window_height)

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(window_width, window_height)
glutCreateWindow(b"Red Ball Game")
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutSpecialFunc(special_keys)
glutMouseFunc(mouse)
glutTimerFunc(30, update, 0)
glutTimerFunc(700, toggle_eyes, 0)
init()
glutMainLoop()