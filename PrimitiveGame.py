import pygame
import random
import numpy as np
import matplotlib.pyplot as plt

# mag(arr) computes the magnitude of a vector 'arr':
def mag(arr):
    total = 0
    for d in arr:
        total += d**2
    return np.sqrt(total)

# WINDOW INITIALIZATION
pygame.init()
width = 1000
height = 600
screen_res = (width, height)
pygame.display.set_caption("Bomboclat")
screen = pygame.display.set_mode(screen_res)
red = (255, 0, 0)
white = (255, 255, 255)
black = (0,0,0)
FONT = pygame.font.Font(None, 36)
clock = pygame.time.Clock()
fps = 60

# PARAMETERS
T = 5
num_balls = 500    # Number of particles
r = 5               # Particle Radius
mass = 6.646476406e-27
boltz_k = 1.380649e-23
v = np.sqrt((3*boltz_k*T)/mass)


# ARRAY INITIALIZATIONS
data = []
ensemble = []
speed_dist = []
centers = []

# prepares particles: 
for _ in range(num_balls):
    b = False
    # ensures that particle locations are randomized and do not overlap 
    while not b:
        center = [random.randint(20, width-20), random.randint(20, height-20)]
        b = True
        for j in centers:
            x_pos_check = j[0]
            y_pos_check = j[1]

            x_pos = center[0]
            y_pos = center[1]

            dist_check = ((x_pos - x_pos_check)**2 + (y_pos - y_pos_check)**2)**0.5
            if dist_check < 2 * r:
                b = False
                break
    centers.append(center)
    ball = pygame.draw.circle(screen, black, center, r)

    # initializing particle velocities
    v_x = v/np.sqrt(2)
    v_y = v/np.sqrt(2)
    if v_x == 0:
        v_x = random.randint(-1, 1)
    if v_y == 0:
        v_y = random.randint(-1, 1)
    vel = [v_x, v_y]  # insert velocity components into velocity vector
    ensemble.append((ball, vel)) # create particle ensemble
        
# frame updater
while not any(pygame.key.get_pressed()): # simulation stops when any key is pressed
    
    # INITIALIZATIONS
    vel_arr = []
    speeds_arr = []
    s = []
    speed_sq = 0
    
    screen.fill(white)  # maintain white background

    for i, (ball, vel) in enumerate(ensemble):
        vel_arr.append(vel)
        ball = ball.move(vel) # move particle per frame

        # if ball goes out of screen then change direction of movement:
        if ball.left < 0:
            ball.left = 0
            vel[0] = -vel[0]
        elif ball.right > width:
            ball.right = width
            vel[0] = -vel[0]
        if ball.top < 0:
            ball.top = 0
            vel[1] = -vel[1]
        elif ball.bottom > height:
            ball.bottom = height
            vel[1] = -vel[1]
            
        for j, (other_ball, other_vel) in enumerate(ensemble[i + 1:], start=i + 1):
            dx = other_ball.centerx - ball.centerx
            dy = other_ball.centery - ball.centery
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance < (r * 2):  # if distance between two particles is less than sum of radii, they've collided
                
                # renaming variables:
                x_pos, y_pos = ball.centerx, ball.centery
                other_x_pos, other_y_pos = other_ball.centerx, other_ball.centery
                x_1 = np.array([x_pos, y_pos])
                x_2 = np.array([other_x_pos, other_y_pos])
                v_1 = np.array(vel)
                v_2 = np.array(other_vel)

                # updating velocities: 
                vel_1_f = v_1 - (((v_1 - v_2) @ ((x_1 - x_2))/((mag((x_1 - x_2)))**2))*(x_1 - x_2))
                vel_2_f = v_2 - (((v_2 - v_1) @ ((x_2 - x_1))/((mag((x_2 - x_1)))**2))*(x_2 - x_1))
                
                # preventing division of 0 in velocity update (TO BE FIXED IN THE FUTURE): 
                if mag((x_1 - x_2)) != 0:
                    vel[0], other_vel[0] = vel_1_f[0], vel_2_f[0]
                    vel[1], other_vel[1] = vel_1_f[1], vel_2_f[1]         

        ensemble[i] = (ball, vel)  # update particle location in the list
        pygame.draw.circle(surface=screen, color=red, center=ball.center, radius=r) # draw particle
    
    for vel in vel_arr:
        speed = (vel[0] ** 2 + vel[1] ** 2) ** 0.5
        speed_sq += speed**2
        s.append(speed)
    ke = (1/2)*mass*(speed_sq)                 # this computes the total energy of the system (in Joules)
    avg_ke = ke / num_balls                    # this computes the average energy of each particle (in Joules)
    
    # computing average speed of system per frame:
    speeds_arr = np.array(s)
    speed_dist = speeds_arr
    avg_speed = np.sum(speeds_arr) / num_balls
    data.append(avg_speed)

    temp = (2/(3*boltz_k))*avg_ke     # this computes the temperature of the system per frame

    # text rendering:
    
    text_surface_1 = FONT.render(f"Average Speed: {round(avg_speed, 5)}", True, black)
    text_rect_1 = text_surface_1.get_rect()
    text_rect_1.center = (150, height-30)                                                       
    screen.blit(text_surface_1, text_rect_1)

    text_surface_2 = FONT.render(f"Total Energy (U): {round(ke, 5)} J", True, black)
    text_rect_2 = text_surface_2.get_rect()
    text_rect_2.center = (width-180, height-30)
    screen.blit(text_surface_2, text_rect_2)

    text_surface_3 = FONT.render(f"Temperature: {round(temp, 5)} K", True, black)
    text_rect_3 = text_surface_3.get_rect()
    text_rect_3.center = (width-180, 30)
    screen.blit(text_surface_3, text_rect_3)                 
 
    pygame.display.flip()
    clock.tick(fps)

    for event in pygame.event.get():
        # check if a user wants to exit the game or not
        if event.type == pygame.QUIT:
            exit()

# creates histogram displaying the distribution of particle velocities after simulation stops:
plt.hist(speed_dist, bins=50, color='blue', alpha=0.7)
plt.xlabel('Speed')
plt.ylabel('Frequency')
plt.title('Speed Distribution')
plt.show()

# plots average speed as a function of time:
plt.plot(data)
plt.xlabel("Time")
plt.ylabel("Average Speed")
plt.title("Average Speed Over Time")
plt.show()



