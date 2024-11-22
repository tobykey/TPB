# import Tooltip
import pygame
import time
import sys
import mysql.connector
import textwrap
# 기존 import 아래에 추가
from pygame.cursors import *
pygame.init()
# 새로운 툴팁 클래스 추가
class Tooltip:
    def __init__(self, font_path=None, font_size=24):
        self.font = pygame.font.Font(font_path, font_size) if font_path else pygame.font.Font(None, font_size)
        self.color = (255, 255, 255)
        self.bg_color = (50, 50, 50, 200)

    def draw(self, screen, text, pos):
        # 텍스트 렌더링
        text_surface = self.font.render(text, True, self.color)

        # 반투명 배경 생성
        surface = pygame.Surface((text_surface.get_width() + 20, text_surface.get_height() + 10), pygame.SRCALPHA)
        surface.fill(self.bg_color)

        # 텍스트 배치
        surface.blit(text_surface, (10, 5))

        # 화면에 그리기
        screen.blit(surface, pos)
# 커스텀 마우스 커서 클래스
class CustomCursor:
    def __init__(self):
        # 기본 커서와 호버 커서 설정 수정
        self.default_cursor = pygame.SYSTEM_CURSOR_ARROW
        self.hover_cursor = pygame.SYSTEM_CURSOR_HAND

    def update(self, is_hovering=False):
        if is_hovering:
            pygame.mouse.set_cursor(self.hover_cursor)
        else:
            pygame.mouse.set_cursor(self.default_cursor)
# 화면 전환 관리자 클래스
class ScreenTransition:
    def __init__(self, screen_width, screen_height):
        self.transition_surface = pygame.Surface((screen_width, screen_height))
        self.alpha = 0
        self.fade_speed = 5
        self.is_fading_in = True
        self.is_transitioning = False

    def start_transition(self):
        self.is_transitioning = True
        self.is_fading_in = True
        self.alpha = 0

    def update(self, screen):
        if self.is_transitioning:
            self.transition_surface.fill((0, 0, 0))
            self.transition_surface.set_alpha(self.alpha)

            if self.is_fading_in:
                self.alpha += self.fade_speed
                if self.alpha >= 255:
                    self.is_fading_in = False
            else:
                self.alpha -= self.fade_speed
                if self.alpha <= 0:
                    self.is_transitioning = False

            screen.blit(self.transition_surface, (0, 0))
# 기존 pygame.init() 아래에 추가
# UI 개선을 위한 객체 생성
# 아이템 획득 메시지 클래스 추가
class ItemAcquisitionMessage:
    def __init__(self, font_path=None, font_size=36):
        self.font = pygame.font.Font(font_path, font_size) if font_path else pygame.font.Font(None, font_size)
        self.message = ""
        self.show_time = 0
        self.is_visible = False
        self.duration = 3  # 메시지 표시 시간 (초)

    def show(self, item_name):
        self.message = f"{item_name}을(를) 획득하였습니다."
        self.show_time = time.time()
        self.is_visible = True

    def update(self, screen, mouse_pos):
        if not self.is_visible:
            return

        # 현재 시간 체크
        current_time = time.time()
        if current_time - self.show_time > self.duration:
            self.is_visible = False
            return

        # 메시지 렌더링
        text_surface = self.font.render(self.message, True, (255, 255, 255))

        # 반투명 배경 생성
        surface = pygame.Surface((text_surface.get_width() + 40, text_surface.get_height() + 20), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 200))  # 반투명 검정 배경

        # 텍스트 배치
        surface.blit(text_surface, (20, 10))

        # 화면 중앙에 위치
        x = (screen.get_width() - surface.get_width()) // 2
        y = screen.get_height() - surface.get_height() - 50

        # 마우스 클릭 시 메시지 닫기
        rect = surface.get_rect(topleft=(x, y))
        if rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            self.is_visible = False
            return

        # 화면에 그리기
        screen.blit(surface, (x, y))


class StoryTextSystem:
    def __init__(self, font_path, font_size=30, text_color=(255, 255, 255),
                box_color=(0, 0, 0, 180), screen_width=900, screen_height=675):
        # 기본 설정
        self.font = pygame.font.Font(font_path, font_size)
        self.text_color = text_color
        self.box_color = box_color
        self.screen_width = screen_width
        self.screen_height = screen_height

        # 텍스트 관련 변수
        self.current_text = ""
        self.displayed_text = ""
        self.text_speed = 0.05
        self.last_text_update = pygame.time.get_ticks()
        self.text_index = 0
        self.is_text_complete = False
        self.is_visible = False

        # 새로운 변수들
        self.typing_sound = pygame.mixer.Sound("resource_pack/effect/typing.mp3")
        self.typing_sound.set_volume(0.2)
        self.speaker_name = ""
        self.last_sound_time = 0
        self.sound_interval = 50
        self.text_queue = []

        # 텍스트 박스 설정
        self.box_height = 200
        self.box_padding = 20
        self.name_box_width = 150
        self.name_box_height = 40

    def set_text(self, text, speaker=""):
        """텍스트 설정 (화자 이름 포함)"""
        self.current_text = text
        self.displayed_text = ""
        self.text_index = 0
        self.is_text_complete = False
        self.is_visible = True
        self.last_text_update = pygame.time.get_ticks()
        self.speaker_name = speaker

    def add_text_to_queue(self, text, speaker=""):
        """텍스트 큐에 새 텍스트 추가"""
        self.text_queue.append((text, speaker))

    def next_text(self):
        """큐에서 다음 텍스트 가져오기"""
        if self.text_queue:
            text, speaker = self.text_queue.pop(0)
            self.set_text(text, speaker)
            return True
        return False

    def update(self, screen):
        if not self.is_visible:
            return False

        # 메인 텍스트 박스 그리기
        text_surface = pygame.Surface((self.screen_width, self.box_height), pygame.SRCALPHA)
        text_surface.fill(self.box_color)

        # 화자 이름 박스 및 이미지 그리기 (이름이 있을 때만)
        if self.speaker_name:
            # 이름 박스
            name_box = pygame.Surface((self.name_box_width, self.name_box_height), pygame.SRCALPHA)
            name_box.fill((0, 0, 0, 200))  # 이름 박스 배경색
            name_text = self.font.render(self.speaker_name, True, (255, 255, 255))
            name_box.blit(name_text, (10, 5))
            name_box_pos = (50, self.screen_height - self.box_height - 30)
            screen.blit(name_box, name_box_pos)

            # 화자 이미지 (권도현인 경우)
            if self.speaker_name == "권도현":
                # 이미지 원본 크기 유지
                character_image = image_main
                # 이름 박스 오른쪽에 이미지 표시
                # 이미지의 bottom이 이름 박스의 bottom과 일치하도록 설정
                image_x = name_box_pos[0] + self.name_box_width + 10  # 이름 박스 오른쪽에 10픽셀 간격
                image_y = name_box_pos[1] + self.name_box_height - character_image.get_height()  # 하단 정렬
                screen.blit(character_image, (image_x, image_y))

        # 텍스트 점진적 출력 및 타이핑 효과음
        current_time = pygame.time.get_ticks()
        if not self.is_text_complete:
            if current_time - self.last_text_update > self.text_speed * 1000:
                if self.text_index < len(self.current_text):
                    self.displayed_text += self.current_text[self.text_index]
                    self.text_index += 1
                    self.last_text_update = current_time

                    # 타이핑 효과음 재생 (일정 간격으로)
                    if current_time - self.last_sound_time > self.sound_interval:
                        self.typing_sound.play()
                        self.last_sound_time = current_time
                else:
                    self.is_text_complete = True

        # 텍스트 렌더링 (자동 줄바꿈 포함)
        words = self.displayed_text.split(' ')
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            text_width = self.font.size(' '.join(current_line))[0]
            if text_width > self.screen_width - 2 * self.box_padding:
                lines.append(' '.join(current_line[:-1]))
                current_line = [word]
        lines.append(' '.join(current_line))

        # 각 줄 렌더링
        for i, line in enumerate(lines):
            text_render = self.font.render(line, True, self.text_color)
            text_surface.blit(text_render, (self.box_padding, self.box_padding + i * 30))

        # "계속하려면 클릭" 메시지 (텍스트가 완료되었을 때)
        if self.is_text_complete:
            continue_text = self.font.render("계속하려면 클릭", True, (200, 200, 200))
            text_surface.blit(continue_text,
                            (self.screen_width - 250, self.box_height - 50))

        # 화면에 텍스트 박스 그리기
        screen.blit(text_surface, (0, self.screen_height - self.box_height))
        return True

    def handle_click(self, mouse_pos):
        if not self.is_visible:
            return False

        box_rect = pygame.Rect(0, self.screen_height - self.box_height,
                                self.screen_width, self.box_height)

        if box_rect.collidepoint(mouse_pos):
            if not self.is_text_complete:
                # 텍스트 즉시 완성
                self.displayed_text = self.current_text
                self.text_index = len(self.current_text)
                self.is_text_complete = True
            else:
                # 다음 텍스트가 있으면 표시, 없으면 종료
                if not self.next_text():
                    self.is_visible = False
                    return True
        return False

tooltip = Tooltip("resource_pack/font/이순신Bold.ttf", 24)
custom_cursor = CustomCursor()
screen_transition = ScreenTransition(900, 675)
# 아이템 획득 메시지 및 효과음 초기화
item_acquisition_sound = pygame.mixer.Sound("resource_pack/effect/아이템 획득 효과음.mp3")
item_acquisition_message = ItemAcquisitionMessage("resource_pack/font/이순신Bold.ttf", 30)
story_text_system = StoryTextSystem("resource_pack/font/이순신Bold.ttf", 24)


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
image_news = pygame.image.load("resource_pack/image/5호관 사고.jpg")
image_scene4 = pygame.image.load("resource_pack/image/5호관 교실.jpg")

image_main = pygame.image.load("resource_pack/image/권도현.png")

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

size_news_width = image_news.get_size()[0]
size_news_height = image_news.get_size()[1]

size_main_width = image_main.get_size()[0]
size_main_height = image_main.get_size()[1]

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
screen3_initialized = False  # screen3의 초기화 상태를 추적하는 변수 추가
screen4_initialized = False
screen5_initialized = False
news_initialized = False
tried_to_leave = False
screen6_initialized = False
classroom_visited = False  # 교실 방문 가능 상태 체크
return_message_shown = False
inventory_open = False

mysterious_letter_puzzle = [
    ['연', '마', '카', '타', '파', '하', '차', '바', '나', '다'],
    ['라', '극', '사', '아', '자', '카', '타', '파', '하', '가'],
    ['마', '바', '장', '카', '타', '파', '하', '차', '바', '나'],
    ['사', '아', '자', '으', '타', '파', '하', '차', '바', '다'],
    ['자', '차', '카', '타', '로', '파', '하', '차', '바', '가'],
    ['아', '바', '사', '아', '자', '지', '하', '차', '바', '나'],
    ['차', '마', '바', '사', '아', '자', '금', '차', '바', '다'],
    ['카', '라', '마', '바', '사', '아', '자', '가', '바', '가'],
    ['타', '파', '라', '마', '바', '사', '아', '자', '야', '나'],
    ['파', '하', '차', '라', '마', '바', '사', '아', '자', '해']
]

answer = "연극장으로지금가야해"
puzzle_solved = False
input_active = False
user_text = ""
letter = Item("resource_pack/image/편지.png", 300, 200, 100, 100, "의문의 편지")



last_click_time = 0  # 마지막 클릭 시간 추적
CLICK_DELAY = 100 # 클릭 간 최소 시간 간격 (밀리초)

play = True
BGM.play(-1)
clock = pygame.time.Clock()

# 디졸브 효과 변수
alpha = 0  # 초기 알파 값
fade_in = True  # 페이드 인 또는 페이드 아웃 상태

def quitgame():
    pygame.quit()
    sys.exit()

# 클릭 처리를 위한 함수 추가
def can_click():
    current_time = pygame.time.get_ticks()
    global last_click_time
    if current_time - last_click_time >= CLICK_DELAY:
        last_click_time = current_time
        return True
    return False

while play:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            play = False
    # pygame.mouse.set_cursor(*pygame.cursors.diamond)
    # 화면 전환 효과 업데이트
    GAME_STATE = {
        'loading_done': False,  # 로딩이 끝났는지 여부
        'intro': False,  # 뉴스 보도 장면
        'main_game': False
    }

    HALLWAY_SPOTS = {
        'window': {'rect': pygame.Rect(100, 150, 200, 300), 'text': "창문 밖으로는 어두운 하늘이 보인다..."},
        'locker': {'rect': pygame.Rect(400, 200, 150, 250), 'text': "사물함이다. 잠겨있어 열리지 않는다."},
        'notice': {'rect': pygame.Rect(600, 150, 100, 150), 'text': "게시판에 여러 공지사항들이 붙어있다."}
    }
    screen_transition.update(background)
    mouse_pos = pygame.mouse.get_pos()
    # 마우스 위치와 클릭 상태 확인
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed()
    # 현재 화면 상태에 따른 커서 및 툴팁 처리
    is_hovering = False

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
                GAME_STATE['intro'] = True  # 뉴스 보도 장면으로 시작=
                loading_start_time = time.time()  # 로딩 타이머 시작

            # 마우스 오버 했을 때
            else:
                background.blit(image_start_mo, (x_pos_start_mo, y_pos_start_mo))
                is_hovering = True
                # 툴팁 추가
                tooltip.draw(background, "게임 시작", (mouse_x + 10, mouse_y))
        # 평상시
        else:
            background.blit(image_start, (x_pos_start, y_pos_start))

        if (x_pos_option <= mouse_x <= x_pos_option + size_option_width and
                y_pos_option <= mouse_y <= y_pos_option + size_option_height):
            if mouse_buttons[0]:
                background.blit(image_option_click, (x_pos_option_click, y_pos_option_click))
                click_sound.play()  # 효과음 재생
            else:
                background.blit(image_option_mo, (x_pos_option_mo, y_pos_option_mo))
                is_hovering = True
                tooltip.draw(background, "게임 설정", (mouse_x + 10, mouse_y))
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
                is_hovering = True
                tooltip.draw(background, "게임 종료", (mouse_x + 10, mouse_y))
        else:
            background.blit(image_exit, (x_pos_exit, y_pos_exit))
            # 커서 업데이트
        custom_cursor.update(is_hovering)

        pygame.display.flip()


    elif current_screen == 2:
        # 로딩 화면 표시
        background.blit(image_loading, (0, 0))
        font = pygame.font.Font(None, 74)
        text = font.render("Loading...", True, (255, 255, 255))
        background.blit(text, (350, 300))

        # 3초 후
        if time.time() - loading_start_time >= 3:
            if not GAME_STATE['loading_done']:
                GAME_STATE['loading_done'] = True
                GAME_STATE['intro'] = True

            # 뉴스 화면 (로딩 완료 후)
            if GAME_STATE['intro']:
                background.blit(image_news, (0, 0))  # 검은 배경 대신 사고 이미지
                # 뉴스 화면 효과
                if not news_initialized:
                    story_text_system.set_text("[속보] 인하대학교 5호관에서 사고 발생", "뉴스 앵커")
                    story_text_system.add_text_to_queue("연극부 공연 준비 중 조명 시설 사고로 학생 1명 사망", "뉴스 앵커")
                    story_text_system.add_text_to_queue("사고 경위에 대해서는 현재 조사가 진행 중입니다.", "뉴스 앵커")
                    news_initialized = True
                # 뉴스 텍스트 업데이트
                if story_text_system.update(background):
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONDOWN and can_click():
                            if story_text_system.handle_click(event.pos):
                                GAME_STATE['intro'] = False
                                GAME_STATE['main_game'] = True
                                current_screen = 3  # 기존 흐름대로 진행


    elif current_screen == 3:
        background.blit(image_scene1, (0, 0))
        # 첫 번째 스토리 텍스트 설정 (최초 1회)
        if not screen3_initialized:
            story_text_system.set_text("이건 인하대학교 5호관에 관한 이야기이다. 오래된 건물 복도에 mysterious한 분위기가 감돈다.")
            screen3_initialized = True
        # 스토리 텍스트 업데이트
        story_text_system.update(background)
        # 클릭 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if story_text_system.handle_click(event.pos):
                    current_screen = 4



    elif current_screen == 4:
        background.blit(image_scene2, (0, 0))
        # 처음 진입시 대사 설정 (최초 1회)
        if not screen4_initialized:
            story_text_system.set_text("선배가 사고를 당했던 5호관...", "권도현")
            story_text_system.add_text_to_queue("분명 그날 누군가가 조명을 건드리는 걸 봤는데...", "권도현")
            story_text_system.add_text_to_queue("이 사건의 진실을 밝혀내야만 해.", "권도현")
            screen4_initialized = True
        # 기자재실에서 돌아왔을 때의 대사
        elif classroom_visited and not return_message_shown:
            story_text_system.set_text("필요한 물건은 다 찾았어.", "권도현")
            story_text_system.add_text_to_queue("이제 다른 곳도 둘러보자.", "권도현")
            return_message_shown = True
        # UI 요소 그리기
        background.blit(ui_inventory, (x_pos_inventory, y_pos_inventory))
        background.blit(ui_right, (x_pos_right, y_pos_right))
        background.blit(ui_left, (x_pos_left, y_pos_left))
        # 인벤토리 호버 처리
        if (x_pos_inventory <= mouse_x <= x_pos_inventory + size_inventory_width and
                y_pos_inventory <= mouse_y <= y_pos_inventory + size_inventory_height):
            background.blit(overlay, (450, 100))
            tooltip.draw(background, "인벤토리", (mouse_x + 10, mouse_y))
            is_hovering = True
            # 인벤토리 아이템 표시
            for i, item in enumerate(inventory):
                background.blit(item.image, (450 + i * 100, 100))
        # 화살표 호버 및 클릭 처리 - 대화 중에는 비활성화
        if not story_text_system.is_visible:
            # 오른쪽 화살표 호버 및 클릭 처리
            right_arrow_rect = pygame.Rect(x_pos_right, y_pos_right, size_right_width, size_right_height)
            if right_arrow_rect.collidepoint(mouse_x, mouse_y):
                is_hovering = True
                tooltip.draw(background, "기자재실로 이동", (mouse_x + 10, mouse_y))
                if mouse_buttons[0]:
                    click_sound.play()
                    current_screen = 5
            # 왼쪽 화살표 호버 및 클릭 처리
            left_arrow_rect = pygame.Rect(x_pos_left, y_pos_left, size_left_width, size_left_height)
            if left_arrow_rect.collidepoint(mouse_x, mouse_y):
                is_hovering = True
                if classroom_visited:  # 기자재실을 방문한 후
                    tooltip.draw(background, "5호관 교실로 이동", (mouse_x + 10, mouse_y))
                    if mouse_buttons[0]:
                        click_sound.play()
                        current_screen = 6
                else:  # 기자재실 방문 전
                    tooltip.draw(background, "아직은 갈 수 없다", (mouse_x + 10, mouse_y))
                    if mouse_buttons[0]:
                        click_sound.play()
                        story_text_system.set_text("아직 이쪽으로 갈 필요는 없을 것 같다.", "권도현")
        else:
            # 대화 중일 때 화살표에 호버하면
            if (pygame.Rect(x_pos_right, y_pos_right, size_right_width, size_right_height).collidepoint(mouse_x,
                                                                                                        mouse_y) or
                    pygame.Rect(x_pos_left, y_pos_left, size_left_width, size_left_height).collidepoint(mouse_x,
                                                                                                        mouse_y)):
                is_hovering = True
                tooltip.draw(background, "대화 완료 후 이동 가능", (mouse_x + 10, mouse_y))
        # 스토리 텍스트 업데이트
        story_text_system.update(background)
        # 대화 클릭 처리
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                story_text_system.handle_click(event.pos)


    elif current_screen == 5:
        # 1. 배경 및 기본 UI 그리기
        background.blit(image_scene3, (0, 0))
        background.blit(ui_inventory, (x_pos_inventory, y_pos_inventory))
        background.blit(ui_left, (x_pos_left, y_pos_left))

        # 2. 첫 진입 시 대사 설정
        if not screen5_initialized:
            story_text_system.set_text("기자재실... 혹시 여기서 단서를 찾을 수 있을까?", "권도현")
            story_text_system.add_text_to_queue("어? 저기 뭔가 있는 것 같은데...", "권도현")
            story_text_system.add_text_to_queue("UV 라이트와 건전지... 그리고 열쇠까지. 이걸로 뭔가 알아낼 수 있을지도.", "권도현")
            screen5_initialized = True

        # 3. 이벤트 처리
        is_hovering = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play = False
            elif event.type == pygame.MOUSEBUTTONDOWN and can_click():
                # 인벤토리 관련 클릭 처리
                if pygame.Rect(x_pos_inventory, y_pos_inventory, size_inventory_width,
                                size_inventory_height).collidepoint(mouse_pos):
                    inventory_open = not inventory_open
                    click_sound.play()
                elif inventory_open and pygame.Rect(810, 110, 30, 30).collidepoint(mouse_pos):
                    inventory_open = False
                    click_sound.play()

                # 뒤로가기 버튼 클릭
                elif (not story_text_system.is_visible and
                        pygame.Rect(x_pos_left, y_pos_left, size_left_width, size_left_height).collidepoint(mouse_pos)):
                    # 모든 아이템이 수집되었는지 확인
                    all_items_collected = all(item.collected for item in items)
                    if all_items_collected:
                        current_screen = 4
                        classroom_visited = True  # 교실 방문 가능하도록 설정
                        click_sound.play()
                        # 복도로 돌아왔을 때의 대사 설정을 위한 플래그
                        screen4_return = True
                    else:
                        story_text_system.set_text("아직 수집하지 못한 아이템이 있는 것 같아.", "권도현")
                        click_sound.play()


                # 아이템 획득 클릭
                elif not story_text_system.is_visible:
                    for item in items:
                        if (not item.collected and
                                pygame.Rect(item.x, item.y, item.width, item.height).collidepoint(mouse_pos)):
                            item.collected = True
                            inventory.append(item)
                            item_acquisition_sound.play()
                            item_acquisition_message.show(item.name)
                # 스토리 텍스트 클릭
                story_text_system.handle_click(mouse_pos)
        # 4. 아이템 표시 및 상호작용
        if not story_text_system.is_visible:
            # 대화가 없을 때 아이템 표시
            for item in items:
                if not item.collected:
                    item.draw(background)
                    if pygame.Rect(item.x, item.y, item.width, item.height).collidepoint(mouse_pos):
                        is_hovering = True
                        tooltip.draw(background, f"{item.name} 획득하기", (mouse_x + 10, mouse_y))

        else:
            # 대화 중일 때 아이템 반투명 표시
            for item in items:
                if not item.collected:
                    item.draw(background)
                    s = pygame.Surface((item.width, item.height), pygame.SRCALPHA)
                    s.fill((0, 0, 0, 128))
                    background.blit(s, (item.x, item.y))

        # 5. 인벤토리 UI 표시
        if inventory_open:
            # 인벤토리 배경
            inventory_bg = pygame.Surface((400, 300), pygame.SRCALPHA)
            inventory_bg.fill((0, 0, 0, 200))
            background.blit(inventory_bg, (450, 100))

            # 인벤토리 제목
            font = pygame.font.Font("resource_pack/font/이순신Bold.ttf", 24)
            title = font.render("인벤토리", True, (255, 255, 255))
            background.blit(title, (460, 110))

            # 인벤토리 슬롯
            for i in range(8):
                slot_x = 460 + (i % 4) * 90
                slot_y = 150 + (i // 4) * 90
                pygame.draw.rect(background, (50, 50, 50), (slot_x, slot_y, 80, 80))
                pygame.draw.rect(background, (100, 100, 100), (slot_x, slot_y, 80, 80), 2)
                if i < len(inventory):
                    scaled_item = pygame.transform.scale(inventory[i].image, (70, 70))
                    background.blit(scaled_item, (slot_x + 5, slot_y + 5))
                    if pygame.Rect(slot_x, slot_y, 80, 80).collidepoint(mouse_pos):
                        tooltip.draw(background, inventory[i].name, (mouse_x + 10, mouse_y))

            # 닫기 버튼
            close_btn = pygame.Rect(810, 110, 30, 30)
            pygame.draw.rect(background, (150, 0, 0), close_btn)
            if close_btn.collidepoint(mouse_pos):
                is_hovering = True
                tooltip.draw(background, "닫기", (mouse_x + 10, mouse_y))

        # 6. UI 호버 효과
        # 인벤토리 아이콘 호버
        if pygame.Rect(x_pos_inventory, y_pos_inventory, size_inventory_width, size_inventory_height).collidepoint(
                mouse_pos):
            is_hovering = True
            tooltip.draw(background, "인벤토리 열기/닫기", (mouse_x + 10, mouse_y))

        # 뒤로가기 버튼 호버
        if pygame.Rect(x_pos_left, y_pos_left, size_left_width, size_left_height).collidepoint(mouse_pos):
            is_hovering = True
            if story_text_system.is_visible:
                tooltip.draw(background, "대화 완료 후 이동 가능", (mouse_x + 10, mouse_y))
            else:
                tooltip.draw(background, "복도로 돌아가기", (mouse_x + 10, mouse_y))

        # 7. 시스템 업데이트
        story_text_system.update(background)
        item_acquisition_message.update(background, mouse_pos)
        custom_cursor.update(is_hovering)



    elif current_screen == 6:
        # 1. 배경 및 기본 UI 그리기
        background.blit(image_scene4, (0, 0))
        background.blit(ui_inventory, (x_pos_inventory, y_pos_inventory))
        background.blit(ui_left, (x_pos_left, y_pos_left))
        # 2. 첫 진입 시 대사 설정
        if not screen6_initialized:
            story_text_system.set_text("교실이다... 이곳에서 무슨 일이 있었던 걸까?", "권도현")
            story_text_system.add_text_to_queue("어? 저기 책상 위에 뭔가 있는데...", "권도현")
            story_text_system.add_text_to_queue("의문의 편지...? 글자가 이상하게 배열되어 있어.", "권도현")
            screen6_initialized = True
        # 버튼 정의를 조건문 밖으로 이동
        solve_btn = pygame.Rect(300, 480, 200, 40)
        font = pygame.font.Font("resource_pack/font/이순신Bold.ttf", 20)
        # 3. 퍼즐 표시 - 대화가 끝난 후에만 표시
        if not puzzle_solved and not story_text_system.is_visible:
            # 배경 패널 그리기
            panel_width = 300
            panel_height = 300
            cell_size = 30
            start_x = 250
            start_y = 150
            # 패널 배경
            pygame.draw.rect(background, (245, 245, 220), (start_x, start_y, panel_width, panel_height))
            # 격자 그리기
            for i in range(11):
                pygame.draw.line(background, (0, 0, 0),
                        (start_x + i * cell_size, start_y),
                        (start_x + i * cell_size, start_y + panel_height))
                pygame.draw.line(background, (0, 0, 0),
                        (start_x, start_y + i * cell_size),
                        (start_x + panel_width, start_y + i * cell_size))
            # 글자 그리기
            for i in range(10):
                for j in range(10):
                    text = font.render(mysterious_letter_puzzle[i][j], True, (0, 0, 0))
                    text_rect = text.get_rect(center=(start_x + j * cell_size + cell_size / 2,
                                                    start_y + i * cell_size + cell_size / 2))
                    background.blit(text, text_rect)
            # 입력 버튼 그리기
            pygame.draw.rect(background, (100, 100, 100), solve_btn)
            solve_text = font.render("정답 입력하기", True, (255, 255, 255))
            solve_text_rect = solve_text.get_rect(center=(solve_btn.centerx, solve_btn.centery))
            background.blit(solve_text, solve_text_rect)
            # 입력 필드 (버튼 아래에 위치)
            if input_active:
                # 입력 안내 메시지
                guide = font.render("정답을 입력하세요 (Enter로 확인)", True, (0, 0, 0))
                guide_rect = guide.get_rect(center=(400, 540))
                background.blit(guide, guide_rect)
                # 입력 필드 배경
                input_rect = pygame.Rect(250, 560, 300, 40)
                pygame.draw.rect(background, (255, 255, 255), input_rect)
                pygame.draw.rect(background, (100, 100, 100), input_rect, 2)
                # 입력 텍스트
                text_surface = font.render(user_text, True, (0, 0, 0))
                text_rect = text_surface.get_rect(midleft=(input_rect.left + 10, input_rect.centery))
                background.blit(text_surface, text_rect)
        # 4. 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play = False
            # 마우스 클릭 처리
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 대화 시스템 클릭 처리
                story_text_system.handle_click(event.pos)
                # 버튼 클릭 처리 (대화가 끝난 후에만)
                if not story_text_system.is_visible:
                    if solve_btn.collidepoint(event.pos) and can_click():
                        input_active = True
            # 한글 입력 처리
            elif event.type == pygame.TEXTINPUT and input_active:
                if len(user_text) < 20:  # 최대 길이 제한
                    user_text += event.text
            elif event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    if user_text == answer:
                        puzzle_solved = True
                        input_active = False
                        story_text_system.set_text("이건...! 연극장으로 가라는 메시지야!", "권도현")
                        letter.collected = False
                        items.append(letter)
                    else:
                        story_text_system.set_text("뭔가 잘못 읽은 것 같아...", "권도현")
                    user_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
        # 5. 스토리 텍스트 시스템 업데이트
        story_text_system.update(background)
        # 6. 커서 업데이트
        if solve_btn.collidepoint(mouse_pos):
            is_hovering = True
        custom_cursor.update(is_hovering)

    pygame.display.flip()
    
