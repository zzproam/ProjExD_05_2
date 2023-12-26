import pygame
import os


# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Lightning Animation')

folder_path = 'ProjExD_05_2/Lightning'  
image_files = sorted([img for img in os.listdir(folder_path) if img.endswith('.png')])
images = [pygame.image.load(os.path.join(folder_path, img)) for img in image_files]

# Animation settings
fps = 15
clock = pygame.time.Clock()
running = True

# Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Loop through each image to display it
    for image in images:
        screen.fill((0, 0, 0))  # Clear the screen by filling it with black
        screen.blit(image, (0, 0))
        pygame.display.flip()  # Update the full display
        pygame.time.wait(int(1000 / fps))  # Wait to create the correct frame rate

    clock.tick(fps)

pygame.quit()