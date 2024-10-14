import pygame

pygame.init()

background = pygame.display.set_mode((900,675))
pygame.display.set_caption("Escape")

image_bg = pygame.image.load("resource_pack/image/5호관 복도.jpg")
image_logo = pygame.image.load("resource_pack/image/로고.png")
image_team = pygame.image.load("resource_pack/image/팀명.png")
image_start = pygame.image.load("resource_pack/image/시작하기.png")
image_option = pygame.image.load("resource_pack/image/설정.png")
image_exit = pygame.image.load("resource_pack/image/종료.png")

BGM = pygame.mixer.Sound("resource_pack/BGM.mp3")
size1 = 0.2
size2 = 0.7

size_bg_width = background.get_size()[0]
size_bg_height = background.get_size()[1]

size_logo_width = image_logo.get_size()[0]
size_logo_height = image_logo.get_size()[1]

size_team_width = image_team.get_size()[0]
size_team_height = image_team.get_size()[1]

size_start_width = image_start.get_size()[0]
size_start_height = image_start.get_size()[1]

size_option_width = image_option.get_size()[0]
size_option_height = image_option.get_size()[1]

size_exit_width = image_exit.get_size()[0]
size_exit_height = image_exit.get_size()[1]

image_logo = pygame.transform.scale(image_logo,(int(size_logo_width*size1),int(size_logo_height*size1)))
image_team = pygame.transform.scale(image_team,(int(size_team_width*size2),int(size_team_height*size2)))
image_start = pygame.transform.scale(image_start,(int(size_start_width*size1),int(size_start_height*size1)))
image_option = pygame.transform.scale(image_option,(int(size_option_width*size1),int(size_option_height*size1)))
image_exit = pygame.transform.scale(image_exit,(int(size_exit_width*size1),int(size_exit_height*size1)))


x_pos_logo = size_bg_width/2 - size_logo_width/11
y_pos_logo = size_bg_height - size_logo_height/1.6

x_pos_team = size_bg_width/2 - size_team_width/3
y_pos_team = size_bg_height - size_team_height

x_pos_start = size_bg_width - size_start_width/1.8
y_pos_start = size_bg_height - size_start_height/1.25

x_pos_option = size_bg_width - size_option_width/1.15
y_pos_option = size_bg_height - size_option_height/1.65

x_pos_exit = size_bg_width - size_exit_width/1.1
y_pos_exit = size_bg_height - size_exit_height/2.5

print(x_pos_logo, y_pos_logo)
print(x_pos_team, y_pos_team)
print(x_pos_start, y_pos_start)
print(x_pos_option, y_pos_option)
print(x_pos_exit, y_pos_exit)

play = True
BGM.play(-1)
while play:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            play = False

    # background.fill((255,255,255))
    background.blit(image_bg, (0,0))

    background.blit(image_logo, (x_pos_logo, y_pos_logo))
    background.blit(image_team, (x_pos_team, y_pos_team))
    background.blit(image_start, (x_pos_start, y_pos_start))
    background.blit(image_option, (x_pos_option, y_pos_option))
    background.blit(image_exit, (x_pos_exit, y_pos_exit))

    pygame.display.update()