import pygame
import time
import sys
import mysql.connector

pygame.init()

# MySQL 데이터베이스 연결
db = mysql.connector.connect(
    host="localhost",          # MySQL 서버 주소
    user="root",       # MySQL 사용자 이름
    password="root",   # MySQL 비밀번호
    database="tpb"              # 연결할 데이터베이스 이름
)
# 커서 생성
cursor = db.cursor()

# 데이터베이스에서 데이터 가져오기 예제
def fetch_items():
    cursor.execute("SELECT * FROM item")
    items = cursor.fetchall()
    for item in items:
        print(item)  # 여기서 데이터베이스의 데이터를 출력하거나 사용할 수 있습니다
    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()
    for user in users:
        print(user)


# 인벤토리 시스템
inventory = []

# UV 라이트 아이템 설정
class Item:
    def __init__(self, image, x, y, width, height, name):
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (100, 100))  # 아이템 크기 조정
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.name = name
        self.collected = False  # 획득 여부

    def draw(self, screen):
        if not self.collected:
            screen.blit(self.image, (self.x, self.y))

    def is_clicked(self, mouse_pos):
        if (self.x <= mouse_pos[0] <= self.x + self.width and
                self.y <= mouse_pos[1] <= self.y + self.height and
                    pygame.mouse.get_pressed()[0]):
            return True
        return False

# UV 라이트 아이템 생성
uv_light = Item("resource_pack/image/UV라이트.png", 200, 200, 100, 100, "UV Light")
key = Item("resource_pack/image/열쇠.png", 300,300,100,100,"key")
battery = Item("resource_pack/image/건전지.png", 500, 400,100,100, "Battery")

items=[uv_light, key, battery]
fetch_items()

background = pygame.display.set_mode((900,675))
pygame.display.set_caption("Escape")

image_bg = pygame.image.load("resource_pack/image/5호관 복도.jpg")
image_logo = pygame.image.load("resource_pack/image/로고.png")
image_team = pygame.image.load("resource_pack/image/팀명.png")
image_start = pygame.image.load("resource_pack/image/시작하기.png")
image_option = pygame.image.load("resource_pack/image/설정.png")
image_exit = pygame.image.load("resource_pack/image/종료.png")

ui_inventory = pygame.image.load("resource_pack/ui/가방.png")
ui_right = pygame.image.load("resource_pack/ui/오른쪽 화살표.png")
ui_left = pygame.image.load("resource_pack/ui/왼쪽 화살표.png")

overlay = pygame.Surface((400, 200), pygame.SRCALPHA)
overlay.fill((0, 0, 0, 102))  # RGBA 값, 알파 204는 약 80% 투명도

image_loading = pygame.image.load("resource_pack/image/불거진 무대.jpg")

image_scene1 = pygame.image.load("resource_pack/image/5호관 시계탑.jpg")
image_scene2 = pygame.image.load("resource_pack/image/5호관 복도2.jpg")
image_scene3 = pygame.image.load("resource_pack/image/기자재실.jpg")


image_start_mo = pygame.image.load("resource_pack/image/시작하기_mo.png")
image_option_mo = pygame.image.load("resource_pack/image/설정_mo.png")
image_exit_mo = pygame.image.load("resource_pack/image/종료_mo.png")

image_start_click = pygame.image.load("resource_pack/image/시작하기_click.png")
image_option_click = pygame.image.load("resource_pack/image/설정_click.png")
image_exit_click = pygame.image.load("resource_pack/image/종료_click.png")

# image_UVlight = pygame.image.load("resource_pack/image/UV라이트.png")
image_battery = pygame.image.load("resource_pack/image/건전지.png")
image_key = pygame.image.load("resource_pack/image/열쇠.png")

#BGM 로드
BGM = pygame.mixer.Sound("resource_pack/BGM.mp3")
# 효과음 로드
open_sound = pygame.mixer.Sound("resource_pack/effect/문여는소리.mp3")  # 사용할 사운드 파일 경로
click_sound = pygame.mixer.Sound("resource_pack/effect/클릭.mp3")
knock_sound = pygame.mixer.Sound("resource_pack/effect/노크.mp3")

size_1 = 0.1
size_2 = 0.2
size_5 = 0.5
size_7 = 0.7

size_bg_width = background.get_size()[0]
size_bg_height = background.get_size()[1]

size_loading_width = image_loading.get_size()[0]
size_loading_height = image_loading.get_size()[1]

size_scene1_width = image_scene1.get_size()[0]
size_scene1_height = image_scene1.get_size()[1]

size_scene2_width = image_scene2.get_size()[0]
size_scene2_height = image_scene2.get_size()[1]

size_scene3_width = image_scene3.get_size()[0]
size_scene3_height = image_scene3.get_size()[1]

size_logo_width = image_logo.get_size()[0] * size_2
size_logo_height = image_logo.get_size()[1] * size_2

size_team_width = image_team.get_size()[0] * size_7
size_team_height = image_team.get_size()[1] * size_7

size_start_width = image_start.get_size()[0] * size_2
size_start_height = image_start.get_size()[1] * size_2
size_start_mo_width = image_start_mo.get_size()[0] * size_2
size_start_mo_height = image_start_mo.get_size()[1] * size_2
size_start_click_width = image_start_click.get_size()[0] * size_2
size_start_click_height = image_start_click.get_size()[1] * size_2

size_option_width = image_option.get_size()[0] * size_2
size_option_height = image_option.get_size()[1] * size_2
size_option_mo_width = image_option_mo.get_size()[0] * size_2
size_option_mo_height = image_option_mo.get_size()[1] * size_2
size_option_click_width = image_option_click.get_size()[0] * size_2
size_option_click_height = image_option_click.get_size()[1] * size_2

size_exit_width = image_exit.get_size()[0] * size_2
size_exit_height = image_exit.get_size()[1] * size_2
size_exit_mo_width = image_exit_mo.get_size()[0] * size_2
size_exit_mo_height = image_exit_mo.get_size()[1] * size_2
size_exit_click_width = image_exit_click.get_size()[0] * size_2
size_exit_click_height = image_exit_click.get_size()[1] * size_2

size_inventory_width = ui_inventory.get_size()[0]*size_2
size_inventory_height = ui_inventory.get_size()[1]*size_2
size_left_width = ui_right.get_size()[0]*size_2
size_left_height = ui_right.get_size()[1]*size_2
size_right_width = ui_left.get_size()[0]*size_2
size_right_height = ui_left.get_size()[1]*size_2

image_logo = pygame.transform.scale(image_logo,(int(size_logo_width),int(size_logo_height)))
image_team = pygame.transform.scale(image_team,(int(size_team_width),int(size_team_height)))
image_start = pygame.transform.scale(image_start,(int(size_start_width),int(size_start_height)))
image_option = pygame.transform.scale(image_option,(int(size_option_width),int(size_option_height)))
image_exit = pygame.transform.scale(image_exit,(int(size_exit_width),int(size_exit_height)))

image_start_mo = pygame.transform.scale(image_start_mo,(int(size_start_mo_width),int(size_start_mo_height)))
image_option_mo = pygame.transform.scale(image_option_mo,(int(size_option_mo_width),int(size_option_mo_height)))
image_exit_mo = pygame.transform.scale(image_exit_mo,(int(size_exit_mo_width),int(size_exit_mo_height)))

image_start_click = pygame.transform.scale(image_start_click,(int(size_start_click_width),int(size_start_click_height)))
image_option_click = pygame.transform.scale(image_option_click,(int(size_option_click_width),int(size_option_click_height)))
image_exit_click = pygame.transform.scale(image_exit_click,(int(size_exit_click_width),int(size_exit_click_height)))

ui_inventory = pygame.transform.scale(ui_inventory,(int(size_inventory_width),int(size_inventory_height)))
ui_right = pygame.transform.scale(ui_right,(int(size_right_width),int(size_right_height)))
ui_left = pygame.transform.scale(ui_left,(int(size_left_width),int(size_left_height)))

x_pos_logo = 204
y_pos_logo = 26

x_pos_team = 349
y_pos_team = 622

x_pos_start = 370
y_pos_start = 319

x_pos_start_mo = 370
y_pos_start_mo = 319

x_pos_start_click = 370
y_pos_start_click = 319

x_pos_option = 401
y_pos_option = 405

x_pos_option_mo = 401
y_pos_option_mo = 405

x_pos_option_click = 401
y_pos_option_click = 405

x_pos_exit = 400
y_pos_exit = 499

x_pos_exit_mo = 400
y_pos_exit_mo = 499

x_pos_exit_click = 400
y_pos_exit_click = 499

x_pos_left = size_bg_width/2-size_right_width*4
y_pos_left = size_bg_height/2 - size_right_height/2

x_pos_right = size_bg_width - size_left_width*1.25
y_pos_right = size_bg_height/2 - size_left_height/2

x_pos_inventory = size_bg_width - size_inventory_width*1.15
y_pos_inventory = size_bg_height/5 - size_inventory_height

# print(x_pos_logo, y_pos_logo)
# print(x_pos_team, y_pos_team)
# print(x_pos_start, y_pos_start)
# print(x_pos_option, y_pos_option)
# print(x_pos_exit, y_pos_exit)

# 현재 화면 상태 및 로딩 타이머
current_screen = 1
loading_start_time = None

play = True
BGM.play(-1)
clock = pygame.time.Clock()

# 디졸브 효과 변수
alpha = 0  # 초기 알파 값
fade_in = True  # 페이드 인 또는 페이드 아웃 상태

def quitgame():
    pygame.quit()
    sys.exit()

while play:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            play = False
    pygame.mouse.set_cursor(*pygame.cursors.diamond)
    mouse_pos = pygame.mouse.get_pos()
    # 마우스 위치와 클릭 상태 확인
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed()

    if current_screen == 1:
        background.blit(image_bg, (0,0))
        background.blit(image_logo, (x_pos_logo, y_pos_logo))
        background.blit(image_team, (x_pos_team, y_pos_team))
        # 시작버튼 마우스오버 및 클릭시 이미지 변경
        if (x_pos_start <= mouse_x <= x_pos_start + size_start_width and
                y_pos_start <= mouse_y <= y_pos_start + size_start_height):
            # 클릭 했을 때
            if mouse_buttons[0]:
                background.blit(image_start_click, (x_pos_start_click, y_pos_start_click))
                open_sound.play()
                # time.sleep(3)
                current_screen += 1
                loading_start_time = time.time()  # 로딩 타이머 시작

            # 마우스 오버 했을 때
            else:
                background.blit(image_start_mo, (x_pos_start_mo, y_pos_start_mo))
        # 평상시
        else:
            background.blit(image_start, (x_pos_start, y_pos_start))

        if (x_pos_option <= mouse_x <= x_pos_option + size_start_width and
                y_pos_option <= mouse_y <= y_pos_option + size_option_height):
            if mouse_buttons[0]:
                background.blit(image_option_click, (x_pos_option_click, y_pos_option_click))
                click_sound.play()  # 효과음 재생
            else:
                background.blit(image_option_mo, (x_pos_option_mo, y_pos_option_mo))
        else:
            background.blit(image_option, (x_pos_option, y_pos_option))

        if (x_pos_exit <= mouse_x <= x_pos_exit + size_exit_width and
                y_pos_exit <= mouse_y <= y_pos_exit + size_exit_height):
            if mouse_buttons[0]:
                background.blit(image_exit_click, (x_pos_exit_click, y_pos_exit_click))
                click_sound.play()  # 효과음 재생
                quitgame()
            else:
                background.blit(image_exit_mo, (x_pos_exit_mo, y_pos_exit_mo))
        else:
            background.blit(image_exit, (x_pos_exit, y_pos_exit))
        pygame.display.flip()

    elif current_screen == 2:
        background.blit(image_loading,(0,0))
        font = pygame.font.Font(None, 74)
        text = font.render("Loading...", True, (255, 255, 255))
        background.blit(text, (350, 300))
        # 로딩 후 3번 화면으로 전환
        if time.time() - loading_start_time >= 3:  # 3초 로딩
            current_screen = 3

    elif current_screen == 3:
        background.blit(image_scene1, (0, 0))
        font = pygame.font.Font("resource_pack/font/이순신Bold.ttf", 40)
        text = font.render("이건 인하대학교 5호관에 관한 이야기이다..", True, (255, 255, 255))
        text.set_alpha(alpha)
        background.blit(text, (135, 300))
        if fade_in:
            alpha += 0.4
            if alpha >= 255:
                fade_in = False
        else:
            alpha -= 0.25
        text1=font.render("아무 곳이나 클릭하십시오.",True,(255,255,255))
        background.blit(text1,(250,600))
        if time.time() - loading_start_time >= 3:  # 3초 로딩
            if mouse_buttons[0]:
                click_sound.play()
                current_screen = 4

    elif current_screen == 4:
        background.blit(image_scene2, (0, 0))
        background.blit(ui_inventory,(x_pos_inventory,y_pos_inventory))
        if (x_pos_inventory <= mouse_x <= x_pos_inventory + size_inventory_width and
                y_pos_inventory <= mouse_y <= y_pos_inventory + size_inventory_height):
            background.blit(overlay, (450,100))
        background.blit(ui_right,(x_pos_right,y_pos_right))
        background.blit(ui_left,(x_pos_left,y_pos_left))

        if mouse_buttons[1]:
            click_sound.play()
            current_screen = 5

    elif current_screen == 5:
        background.blit(image_scene3, (0, 0))
        background.blit(ui_inventory, (x_pos_inventory, y_pos_inventory))

        for item in items:
            if item.is_clicked(mouse_pos) and not item.collected:
                item.collected = True
                inventory.append(item)
                print(f"{item.name} added to inventory.")

        # 아이템 그리기
        for item in items:
            item.draw(background)

        if (x_pos_inventory <= mouse_x <= x_pos_inventory + size_inventory_width and
                y_pos_inventory <= mouse_y <= y_pos_inventory + size_inventory_height):
            background.blit(overlay, (450,100))
            # 인벤토리에 아이템 그리기
            for i, item in enumerate(inventory):
                font = pygame.font.Font(None, 36)
                # text = font.render(item, True, (255, 255, 255))
                # background.blit(text, (450, 120))  # 인벤토리 위치 설정
                background.blit(item.image, (450 + i * 100, 100))  # 인벤토리 위치를 지정, 간격 조정
    pygame.display.flip()
    
