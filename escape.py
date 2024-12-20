# import Tooltip
import random

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

        # 사운드 관련 변수
        self.typing_sound = pygame.mixer.Sound("resource_pack/effect/typing.mp3")
        self.typing_sound.set_volume(0.2)
        self.last_sound_time = 0
        self.sound_interval = 50
        self.typing_end_time = 0
        self.original_bgm_volume = 1.0  # BGM 원래 볼륨
        self.reduced_bgm_volume = 0.3  # 타이핑 중 BGM 볼륨
        self.is_typing = False
        self.fade_duration = 2000  # 페이드 지속 시간 (2초)
        self.fade_start_time = 0

        # 화자 정보
        self.speaker_name = ""
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

        current_time = pygame.time.get_ticks()

        # 텍스트 점진적 출력 및 타이핑 효과음
        if not self.is_text_complete:
            if current_time - self.last_text_update > self.text_speed * 1000:
                if self.text_index < len(self.current_text):
                    self.displayed_text += self.current_text[self.text_index]
                    self.text_index += 1
                    self.last_text_update = current_time

                    # 타이핑 효과음 재생 및 BGM 볼륨 조절
                    if current_time - self.last_sound_time > self.sound_interval:
                        if not self.is_typing:
                            self.is_typing = True
                            BGM.set_volume(self.reduced_bgm_volume)
                        self.typing_sound.play()
                        self.last_sound_time = current_time
                else:
                    self.is_text_complete = True
                    self.typing_end_time = current_time
                    self.fade_start_time = current_time + 2000  # 타이핑 종료 2초 후 페이드 시작

        # BGM 볼륨 페이드 처리
        if self.is_typing and self.is_text_complete:
            if current_time >= self.fade_start_time:
                # 페이드 진행률 계산 (0.0 ~ 1.0)
                fade_progress = min(1.0, (current_time - self.fade_start_time) / self.fade_duration)
                # 볼륨 선형 보간
                current_volume = self.reduced_bgm_volume + (
                            self.original_bgm_volume - self.reduced_bgm_volume) * fade_progress
                BGM.set_volume(current_volume)

                if fade_progress >= 1.0:
                    self.is_typing = False

        # 메인 텍스트 박스 그리기
        text_surface = pygame.Surface((self.screen_width, self.box_height), pygame.SRCALPHA)
        text_surface.fill(self.box_color)

        # 화자 이름 박스 및 이미지 그리기 (이름이 있을 때만)
        if self.speaker_name:
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
pygame.display.set_caption("인하대탈출 Ver 0.4.0")

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
image_scene5 = pygame.image.load("resource_pack/image/5호관 무섭.jpg")
image_scene6 = pygame.image.load("resource_pack/image/5호관 계단 입구.jpg")
image_scene7 = pygame.image.load("resource_pack/image/5호관 화장실.png")
image_scene7_quiz = pygame.image.load("resource_pack/image/5호관 화장실_문제.png")

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

image_lock = pygame.image.load("resource_pack/image/9버튼 자물쇠.png")
image_glow = pygame.image.load("resource_pack/image/형광부분.png")

image_cold = pygame.image.load("resource_pack/image/냉수.png")
image_hot = pygame.image.load("resource_pack/image/온수.png")
image_washstand = pygame.image.load("resource_pack/image/세면대.png")
image_mirror = pygame.image.load("resource_pack/image/거울.png")
image_mirror_steam = pygame.image.load("resource_pack/image/거울김.png")
image_mirror_number = pygame.image.load("resource_pack/image/거울위글자.png")
image_steam = pygame.image.load("resource_pack/image/화장실 김서림.png")

#BGM 로드
BGM = pygame.mixer.Sound("resource_pack/BGM.mp3")
# 효과음 로드
open_sound = pygame.mixer.Sound("resource_pack/effect/문여는소리.mp3")  # 사용할 사운드 파일 경로
click_sound = pygame.mixer.Sound("resource_pack/effect/클릭.mp3")
knock_sound = pygame.mixer.Sound("resource_pack/effect/노크.mp3")
lock_sound = pygame.mixer.Sound("resource_pack/effect/공포멀어지는소리.mp3")
quiz_sound = pygame.mixer.Sound("resource_pack/effect/문제 시작 효과음.mp3")
solve_sound = pygame.mixer.Sound("resource_pack/effect/문제 해결 효과음.mp3")
surprise_sound = pygame.mixer.Sound("resource_pack/effect/공포피아노소리.mp3")
water_sound = pygame.mixer.Sound("resource_pack/effect/물소리.mp3")

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

image_lock = pygame.transform.scale(image_lock,
    (int(image_lock.get_width() * 0.5), int(image_lock.get_height() * 0.5)))

image_glow = pygame.transform.scale(image_glow,
    (int(image_glow.get_width() * 0.5), int(image_glow.get_height() * 0.5)))

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
show_inventory_ui = False
show_left_arrow = True
ready_for_dark_effect = False
screen7_initialized = False
uv_light_activated = False  # UV라이트 활성화 상태
battery_used = False  # 건전지 사용 여부
uv_light_selected = False  # UV 라이트가 선택되었는지
uv_light_powered = False  # UV 라이트에 배터리가 장착되었는지
lock_zoomed = False  # 자물쇠 줌인 상태
glow_fixed = False
steam_alpha = 255  # 완전 투명
number_alpha = 255  # 완전 투명
steam_start_time = None
number_start_time = None
hot_water_activated = False
effects_completed = False  # 효과 완료 상태 추적을 위한 변수 추가

global clicked_buttons, lock_opened, screen8_initialized, screen9_initialized, mirror_zoom
clicked_buttons = set()
lock_opened = False
screen8_initialized = False
screen9_initialized = False
mirror_zoom = False


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

scene_buttons = [
   {'rect': pygame.Rect(10 + i*60, 10, 50, 30),
    'color': (random.randint(50,255), random.randint(50,255), random.randint(50,255)),
    'text': str(i+1),
    'screen': i+1} for i in range(9)  # 1~7번 씬
]


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

# 인벤토리 시스템을 함수로 분리
def draw_inventory_system(background, mouse_pos, mouse_x, mouse_y):
    is_hovering = False

    # 인벤토리 아이콘 그리기
    background.blit(ui_inventory, (x_pos_inventory, y_pos_inventory))

    # 인벤토리 아이콘 호버 처리
    inventory_rect = pygame.Rect(x_pos_inventory, y_pos_inventory,
                                 size_inventory_width, size_inventory_height)
    if inventory_rect.collidepoint(mouse_pos):
        is_hovering = True
        tooltip.draw(background, "인벤토리 열기/닫기", (mouse_x + 10, mouse_y))

    # 인벤토리 창이 열려있을 때
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

    return is_hovering


# 인벤토리 이벤트 처리 함수
def handle_inventory_events(event):
    global inventory_open
    if event.type == pygame.MOUSEBUTTONDOWN and can_click():
        # 인벤토리 아이콘 클릭
        if pygame.Rect(x_pos_inventory, y_pos_inventory,
                       size_inventory_width, size_inventory_height).collidepoint(event.pos):
            inventory_open = not inventory_open
            click_sound.play()
        # 닫기 버튼 클릭
        elif inventory_open and pygame.Rect(810, 110, 30, 30).collidepoint(event.pos):
            inventory_open = False
            click_sound.play()
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
        background.blit(image_bg, (0, 0))
        background.blit(image_logo, (x_pos_logo, y_pos_logo))
        background.blit(image_team, (x_pos_team, y_pos_team))

        # 씬 선택 버튼 그리기
        for btn in scene_buttons:
            pygame.draw.rect(background, btn['color'], btn['rect'])
            text = pygame.font.Font("resource_pack/font/이순신Bold.ttf", 20).render(btn['text'], True, (255, 255, 255))
            text_rect = text.get_rect(center=btn['rect'].center)
            background.blit(text, text_rect)

            # 버튼 호버 효과
            if btn['rect'].collidepoint(mouse_pos):
                is_hovering = True
                tooltip.draw(background, f"씬 {btn['text']}로 이동", (mouse_x + 10, mouse_y))
                if mouse_buttons[0] and can_click():
                    # 각 씬으로 이동하기 전 필요한 준비 작업
                    if btn['screen'] >= 2:
                        GAME_STATE['intro'] = True
                        loading_start_time = time.time()
                    if btn['screen'] >= 3:
                        news_initialized = True
                    if btn['screen'] >= 4:
                        screen3_initialized = True
                    if btn['screen'] >= 5:
                        screen4_initialized = True
                        classroom_visited = True
                    if btn['screen'] >= 6:
                        screen5_initialized = True
                        for item in items:  # 모든 아이템 획득 처리
                            item.collected = True
                            if item not in inventory:
                                inventory.append(item)
                    if btn['screen'] == 7:
                        screen6_initialized = True
                        puzzle_solved = True
                        ready_for_dark_effect = True
                        show_left_arrow = False
                        uv_light_selected = False
                        uv_light_powered = False
                        lock_zoomed = False
                    if btn['screen'] == 8:
                        screen7_initialized = True
                        screen8_initialized = False  # 8번 씬 초기화
                        clicked_buttons = set()
                        lock_opened = True
                    if btn['screen'] == 9:
                        screen8_initialized = True
                        screen9_initialized = False  # 9번 씬 초기화
                        mirror_zoom = False

                    current_screen = btn['screen']
                    click_sound.play()
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
        show_inventory_ui = True  # 인벤토리 표시 활성화
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
        background.blit(ui_right, (x_pos_right, y_pos_right))
        background.blit(ui_left, (x_pos_left, y_pos_left))
        # 인벤토리 시스템 적용
        if show_inventory_ui:
            inventory_hovering = draw_inventory_system(background, mouse_pos, mouse_x, mouse_y)
            is_hovering = is_hovering or inventory_hovering
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
        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 스토리 텍스트 클릭 처리를 먼저
                story_text_system.handle_click(event.pos)
            # 인벤토리 이벤트 처리는 그 다음에
            if show_inventory_ui:  # elif 대신 if 사용
                handle_inventory_events(event)
        # 스토리 텍스트 업데이트
        story_text_system.update(background)
        custom_cursor.update(is_hovering)


    elif current_screen == 5:
        background.blit(image_scene3, (0, 0))
        show_inventory_ui = True
        # 첫 진입 시 대사 설정
        if not screen5_initialized:
            story_text_system.set_text("기자재실... 혹시 여기서 단서를 찾을 수 있을까?", "권도현")
            story_text_system.add_text_to_queue("어? 저기 뭔가 있는 것 같은데...", "권도현")
            story_text_system.add_text_to_queue("UV 라이트와 건전지... 그리고 열쇠까지. 이걸로 뭔가 알아낼 수 있을지도.", "권도현")
            screen5_initialized = True
        # UI 요소 그리기
        background.blit(ui_left, (x_pos_left, y_pos_left))
        # 인벤토리 시스템 적용
        if show_inventory_ui:
            inventory_hovering = draw_inventory_system(background, mouse_pos, mouse_x, mouse_y)
            is_hovering = is_hovering or inventory_hovering
        # 아이템 드로잉 및 상호작용
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

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 스토리 텍스트 클릭 처리를 가장 먼저
                story_text_system.handle_click(event.pos)

                # 대화가 진행 중이 아닐 때만 다른 상호작용 가능
                if not story_text_system.is_visible:
                    # 뒤로가기 버튼 클릭
                    if pygame.Rect(x_pos_left, y_pos_left, size_left_width, size_left_height).collidepoint(event.pos):
                        # 모든 아이템이 수집되었는지 확인
                        all_items_collected = all(item.collected for item in items)
                        if all_items_collected:
                            current_screen = 4
                            classroom_visited = True
                            click_sound.play()
                        else:
                            story_text_system.set_text("아직 수집하지 못한 아이템이 있는 것 같아.", "권도현")
                            click_sound.play()

                    # 아이템 획득 클릭
                    for item in items:
                        if (not item.collected and
                                pygame.Rect(item.x, item.y, item.width, item.height).collidepoint(event.pos)):
                            item.collected = True
                            inventory.append(item)
                            item_acquisition_sound.play()
                            item_acquisition_message.show(item.name)

            # 인벤토리 이벤트 처리는 별도로
            if show_inventory_ui:
                handle_inventory_events(event)

        # 왼쪽 화살표(뒤로가기) 호버
        if pygame.Rect(x_pos_left, y_pos_left, size_left_width, size_left_height).collidepoint(mouse_pos):
            is_hovering = True
            if story_text_system.is_visible:
                tooltip.draw(background, "대화 완료 후 이동 가능", (mouse_x + 10, mouse_y))

            else:
                tooltip.draw(background, "복도로 돌아가기", (mouse_x + 10, mouse_y))

        # 시스템 업데이트
        story_text_system.update(background)
        item_acquisition_message.update(background, mouse_pos)
        custom_cursor.update(is_hovering)

    global lock_sound_start_time
    if 'lock_sound_start_time' not in globals():
        lock_sound_start_time = None

    elif current_screen == 6:
        # 1. 배경 및 기본 UI 그리기
        background.blit(image_scene4, (0, 0))
        if show_left_arrow:
            background.blit(ui_left, (x_pos_left, y_pos_left))
        show_inventory_ui = True
        # 버튼과 폰트 정의를 앞부분으로 이동
        solve_btn = pygame.Rect(300, 480, 200, 40)
        font = pygame.font.Font("resource_pack/font/이순신Bold.ttf", 20)

        # 2. 첫 진입 시 대사 설정
        if not screen6_initialized:
            story_text_system.set_text("교실이다... 이곳에서 무슨 일이 있었던 걸까?", "권도현")
            story_text_system.add_text_to_queue("어? 저기 책상 위에 뭔가 있는데...", "권도현")
            story_text_system.add_text_to_queue("의문의 편지...? 글자가 이상하게 배열되어 있어.", "권도현")
            quiz_sound.play()  # 퀴즈 시작 효과음
            screen6_initialized = True
        # 3. 인벤토리 시스템 적용
        if show_inventory_ui:
            inventory_hovering = draw_inventory_system(background, mouse_pos, mouse_x, mouse_y)
            is_hovering = is_hovering or inventory_hovering

        # 4. 어두워짐 효과 체크
        if puzzle_solved and story_text_system.current_text == "이제 나가야겠어." and story_text_system.is_text_complete and not ready_for_dark_effect:
            ready_for_dark_effect = True
            show_left_arrow = False  # 화살표 숨기기
            BGM.stop()  # BGM 일시 정지
            lock_sound.play()  # 효과음 재생
            lock_sound_start_time = time.time()  # BGM 재시작 타이머 설정

            # 어두워지는 효과를 위한 오버레이
            darkness_overlay = pygame.Surface((size_bg_width, size_bg_height))
            darkness_overlay.fill((0, 0, 0))
            darkness_overlay.set_alpha(100)
            background.blit(darkness_overlay, (0, 0))

            # 다음 대사 추가
            story_text_system.add_text_to_queue("...", "")
            story_text_system.add_text_to_queue("어..? 갑자기 왜 이러지..?", "권도현")
            story_text_system.add_text_to_queue("문이... 문이 잠겼어!", "권도현")

        # 별도의 대사 체크 부분 추가
        if story_text_system.current_text == "문이... 문이 잠겼어!" and story_text_system.is_text_complete and ready_for_dark_effect:
            current_screen = 7

        # 5. 퍼즐 관련 UI
        if not puzzle_solved and not story_text_system.is_visible:
            # 퍼즐 배경과 격자 그리기
            panel_width, panel_height = 300, 300
            cell_size = 30
            start_x, start_y = 250, 150

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
            font = pygame.font.Font("resource_pack/font/이순신Bold.ttf", 20)
            for i in range(10):
                for j in range(10):
                    text = font.render(mysterious_letter_puzzle[i][j], True, (0, 0, 0))
                    text_rect = text.get_rect(center=(start_x + j * cell_size + cell_size / 2,
                                                      start_y + i * cell_size + cell_size / 2))
                    background.blit(text, text_rect)
            # 정답 입력 버튼
            solve_btn = pygame.Rect(300, 480, 200, 40)
            pygame.draw.rect(background, (100, 100, 100), solve_btn)
            solve_text = font.render("정답 입력하기", True, (255, 255, 255))
            solve_text_rect = solve_text.get_rect(center=(solve_btn.centerx, solve_btn.centery))
            background.blit(solve_text, solve_text_rect)

            # 입력 필드
            if input_active:
                guide = font.render("정답을 입력하세요 (Enter로 확인)", True, (255, 255, 255))
                guide_rect = guide.get_rect(center=(400, 540))
                background.blit(guide, guide_rect)
                input_rect = pygame.Rect(250, 560, 300, 40)
                pygame.draw.rect(background, (255, 255, 255), input_rect)
                pygame.draw.rect(background, (100, 100, 100), input_rect, 2)
                text_surface = font.render(user_text, True, (0, 0, 0))
                text_rect = text_surface.get_rect(midleft=(input_rect.left + 10, input_rect.centery))
                background.blit(text_surface, text_rect)

        # 6. 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 스토리 텍스트 클릭 처리
                story_text_system.handle_click(event.pos)
                # 정답 입력 버튼 클릭
                if not story_text_system.is_visible and not puzzle_solved:
                    if solve_btn.collidepoint(event.pos) and can_click():
                        input_active = True

            # 인벤토리 이벤트 처리
            if show_inventory_ui:
                handle_inventory_events(event)

            # 텍스트 입력 처리
            if event.type == pygame.TEXTINPUT and input_active:
                if len(user_text) < 20:
                    user_text += event.text

            elif event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    if user_text == answer:
                        solve_sound.play()  # 퀴즈 해결 효과음
                        puzzle_solved = True
                        input_active = False
                        story_text_system.set_text("이건...! 연극장으로 가라는 메시지야!", "권도현")
                        story_text_system.add_text_to_queue("의문의 편지를 획득했다.", "권도현")
                        story_text_system.add_text_to_queue("이제 나가야겠어.", "권도현")
                        letter.collected = False
                        items.append(letter)
                        item_acquisition_sound.play()
                        item_acquisition_message.show("의문의 편지")
                    else:
                        story_text_system.set_text("뭔가 잘못 읽은 것 같아...", "권도현")
                    user_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]

        # 7. BGM 재시작 체크
        if puzzle_solved and lock_sound_start_time is not None:
            current_time = pygame.time.get_ticks()
            if current_time - lock_sound_start_time >= 5000:  # 5000ms = 5초
                BGM.play(-1)
                lock_sound_start_time = None  # 타이머 초기화

        # 8. 왼쪽 화살표 호버 처리
        if show_left_arrow and pygame.Rect(x_pos_left, y_pos_left, size_left_width, size_left_height).collidepoint(
                mouse_pos):
            is_hovering = True
            if story_text_system.is_visible:
                tooltip.draw(background, "대화 완료 후 이동 가능", (mouse_x + 10, mouse_y))
            elif puzzle_solved:
                tooltip.draw(background, "문이 잠겼다", (mouse_x + 10, mouse_y))
                if mouse_buttons[0] and can_click():
                    click_sound.play()
                    story_text_system.set_text("문이 잠겼어... 다른 방법을 찾아보자.", "권도현")
            else:
                tooltip.draw(background, "복도로 돌아가기", (mouse_x + 10, mouse_y))
                if mouse_buttons[0] and can_click():
                    click_sound.play()
                    current_screen = 4
        # 9. 시스템 업데이트
        story_text_system.update(background)
        custom_cursor.update(is_hovering)


    elif current_screen == 7:
        # 1. 배경 및 UI 그리기
        background.blit(image_scene5, (0, 0))
        show_inventory_ui = True

        if not lock_zoomed:
            # 일반 상태 - 작은 자물쇠 표시
            background.blit(image_lock, (450, 500))
            if uv_light_powered and not glow_fixed:
                # UV 라이트 효과
                circle_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
                pygame.draw.circle(circle_surface, (0, 255, 255, 51), (100, 100), 100)
                background.blit(circle_surface, (mouse_pos[0] - 100, mouse_pos[1] - 100))

                # 자물쇠 위에서 클릭 감지
                lock_rect = pygame.Rect(450, 500, image_lock.get_width(), image_lock.get_height())
                if lock_rect.collidepoint(mouse_pos):
                    resized_glow = pygame.transform.scale(image_glow, (60, 60))
                    background.blit(resized_glow, (495, 574))
                    if mouse_buttons[0] and can_click():
                        lock_zoomed = True
                        click_sound.play()

        else:
            # 줌인 상태
            zoomed_lock = pygame.transform.scale(image_lock, (400, 400))
            lock_x = (size_bg_width - zoomed_lock.get_width()) // 2
            lock_y = (size_bg_height - zoomed_lock.get_height()) // 2
            background.blit(zoomed_lock, (lock_x, lock_y))

            if uv_light_powered:
                glow_center = (446, 427)
                distance = ((mouse_pos[0] - glow_center[0]) ** 2 + (mouse_pos[1] - glow_center[1]) ** 2) ** 0.5

                # UV 라이트 원형 효과 (고정 여부에 따라)
                circle_surface = pygame.Surface((300, 300), pygame.SRCALPHA)
                pygame.draw.circle(circle_surface, (0, 255, 255, 51), (150, 150), 150)

                # glow 중앙에 가까우면 고정
                if distance < 20 or glow_fixed:  # 20픽셀 반경 내
                    background.blit(circle_surface, (glow_center[0] - 150, glow_center[1] - 150))
                    if not glow_fixed:
                        story_text_system.set_text("이건... 누군가가 눌렀던 흔적..?", "권도현")
                        glow_fixed = True
                else:
                    # 고정되지 않았을 때만 마우스 따라다님
                    background.blit(circle_surface, (mouse_pos[0] - 150, mouse_pos[1] - 150))

                zoomed_glow = pygame.transform.scale(image_glow, (150, 150))
                background.blit(zoomed_glow, (371, 355))

                # 자물쇠 버튼들 (대사가 나온 후에만)
                if glow_fixed:
                    lock_buttons = [
                        {'pos': (394, 376), 'radius': 15, 'id': 0},
                        {'pos': (446, 427), 'radius': 15, 'id': 1},
                        {'pos': (506, 428), 'radius': 15, 'id': 2},
                        {'pos': (506, 474), 'radius': 15, 'id': 3}
                    ]

                    # 버튼 그리기 및 상호작용
                    for btn in lock_buttons:
                        button_surface = pygame.Surface((btn['radius'] * 2, btn['radius'] * 2), pygame.SRCALPHA)
                        # 클릭된 버튼은 다른 색상으로 표시
                        color = (0, 255, 0, 30) if btn['id'] in clicked_buttons else (255, 255, 255, 30)
                        pygame.draw.circle(button_surface, color,
                                           (btn['radius'], btn['radius']), btn['radius'])
                        background.blit(button_surface,
                                        (btn['pos'][0] - btn['radius'], btn['pos'][1] - btn['radius']))

                        # 버튼 클릭 체크를 위한 Rect 추가
                        btn['rect'] = pygame.Rect(btn['pos'][0] - btn['radius'],
                                                  btn['pos'][1] - btn['radius'],
                                                  btn['radius'] * 2, btn['radius'] * 2)

                    # 모든 버튼이 클릭되었을 때
                    if len(clicked_buttons) >= 4 and not lock_opened:
                        lock_opened = True
                        solve_sound.play()
                        story_text_system.set_text("자물쇠가 열렸다!", "권도현")
                        story_text_system.add_text_to_queue("다음으로 넘어가려면 클릭하세요.", "")

        # 2. 첫 진입 시 대사 설정
        if not screen7_initialized:
            story_text_system.set_text("이게 뭐지...? 갑자기 자물쇠가...", "권도현")
            story_text_system.add_text_to_queue("어두워서 잘 안 보이는데... UV 라이트를 사용해볼까?", "권도현")
            quiz_sound.play()  # 퀴즈 시작 효과음
            screen7_initialized = True

        # 3. 인벤토리 상호작용 처리
        if show_inventory_ui:
            inventory_hovering = draw_inventory_system(background, mouse_pos, mouse_x, mouse_y)
            is_hovering = is_hovering or inventory_hovering

            if inventory_open:
                for i, item in enumerate(inventory):
                    slot_x = 460 + (i % 4) * 90
                    slot_y = 150 + (i // 4) * 90
                    item_rect = pygame.Rect(slot_x, slot_y, 80, 80)

                    # 아이템 호버 시 설명
                    if item_rect.collidepoint(mouse_pos):
                        if item.name == "UV Light":
                            tooltip.draw(background,
                                         "켜진 UV Light" if uv_light_powered else "클릭하여 UV Light 선택",
                                         (mouse_x + 10, mouse_y))
                        elif item.name == "Battery" and uv_light_selected:
                            tooltip.draw(background, "클릭하여 UV Light에 장착", (mouse_x + 10, mouse_y))
                        else:
                            tooltip.draw(background, item.name, (mouse_x + 10, mouse_y))

        # 4. 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 자물쇠 버튼 클릭 체크
                if lock_zoomed and glow_fixed:
                    for btn in lock_buttons:
                        if btn['rect'].collidepoint(event.pos):
                            clicked_buttons.add(btn['id'])
                            click_sound.play()

                # 스토리 텍스트 클릭 처리
                if story_text_system.handle_click(event.pos):
                    if lock_opened:
                        current_screen = 8
                        screen_transition.start_transition()
                        surprise_sound.play()

                # 인벤토리 아이템 클릭 처리
                if inventory_open:
                    for i, item in enumerate(inventory):
                        slot_x = 460 + (i % 4) * 90
                        slot_y = 150 + (i // 4) * 90
                        item_rect = pygame.Rect(slot_x, slot_y, 80, 80)

                        if item_rect.collidepoint(event.pos):
                            if item.name == "UV Light" and not uv_light_powered:
                                uv_light_selected = not uv_light_selected
                                click_sound.play()
                            elif item.name == "Battery" and uv_light_selected:
                                uv_light_powered = True
                                uv_light_selected = False
                                inventory.remove(item)
                                click_sound.play()
                                story_text_system.set_text("UV 라이트에 건전지를 장착했다.", "권도현")

            if show_inventory_ui:
                handle_inventory_events(event)

        # 5. 스토리 텍스트 및 시스템 업데이트
        story_text_system.update(background)
        custom_cursor.update(is_hovering)

    elif current_screen == 8:
        background.blit(image_scene6, (0, 0))
        show_inventory_ui = True
        # 처음 진입시 대사 설정
        if not screen8_initialized:
            story_text_system.set_text("어...? 여기가 어디지...?", "권도현")
            story_text_system.add_text_to_queue("분명 교실에 있었는데... 갑자기 계단 입구로...", "권도현")
            story_text_system.add_text_to_queue("(당황스럽게 주위를 둘러보며) 뭐지... 이게 무슨 일이지?", "권도현")
            story_text_system.add_text_to_queue("아까부터 이상한 일이 자꾸 일어나는데...", "권도현")
            story_text_system.add_text_to_queue("이건 분명 평범한 상황이 아닌 것 같아.", "권도현")
            screen8_initialized = True
        # UI 요소 그리기 - 대화가 완료된 경우에만 화살표 표시
        if not story_text_system.is_visible:
            background.blit(ui_right, (x_pos_right, y_pos_right))
            # 오른쪽 화살표 호버 및 클릭 처리
            right_arrow_rect = pygame.Rect(x_pos_right, y_pos_right, size_right_width, size_right_height)
            if right_arrow_rect.collidepoint(mouse_pos):
                is_hovering = True
                tooltip.draw(background, "화장실로 이동", (mouse_x + 10, mouse_y))
                if mouse_buttons[0] and can_click():
                    click_sound.play()
                    current_screen = 9
        # 인벤토리 시스템 적용
        if show_inventory_ui:
            inventory_hovering = draw_inventory_system(background, mouse_pos, mouse_x, mouse_y)
            is_hovering = is_hovering or inventory_hovering
        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 스토리 텍스트 클릭 처리
                story_text_system.handle_click(event.pos)
                # 인벤토리 이벤트 처리
                if show_inventory_ui:
                    handle_inventory_events(event)
        # 스토리 텍스트 및 시스템 업데이트
        story_text_system.update(background)
        custom_cursor.update(is_hovering)

    elif current_screen == 9:

        # 배경 설정 (거울 줌인 여부에 따라)
        if not mirror_zoom:
            background.blit(image_scene7, (0, 0))
            show_inventory_ui = True

            # 처음 진입시 대사 설정
            if not screen9_initialized:
                story_text_system.set_text("저건 뭐지...?", "권도현")
                story_text_system.add_text_to_queue("가까이 가봐야겠다.", "권도현")
                screen9_initialized = True

            # 대사가 끝나면 거울 줌인
            if screen9_initialized and not story_text_system.is_visible and not mirror_zoom:
                mirror_zoom = True
                quiz_sound.play()
                story_text_system.set_text("거울에 희미하게 무슨 자국이 있는 것 같은데, 어떻게 해야할까?", "권도현")
        else:
            # 거울 줌인된 상태 - 레이어 순서대로 배치
            background.blit(image_scene7_quiz, (0, 0))
            background.blit(image_mirror, (275, 70))

            # 김 서림 효과 처리
            # current_screen == 9의 김 서림 효과 처리 부분만 수정
            # 거울 줌인된 상태의 이펙트 처리 부분

            if steam_start_time is not None:
                current_time = pygame.time.get_ticks()
                elapsed_time = (current_time - steam_start_time) / 1000  # 초 단위로 변환

                if not effects_completed:  # 아직 효과가 진행 중일 때
                    if elapsed_time <= 10:  # 첫 10초 동안 김서림 효과
                        # 거울의 김 서림 (0->255로 변화)
                        mirror_steam_alpha = min(255, int(elapsed_time * 25.5))  # 0에서 시작해서 255로
                        mirror_steam_surface = image_mirror_steam.convert_alpha()
                        mirror_steam_surface.set_alpha(mirror_steam_alpha)
                        background.blit(mirror_steam_surface, (355, 100))

                        # 전체 화면의 김 서림 (0->40%로 변화)
                        steam_alpha = min(102, int(elapsed_time * 10.2))  # 0에서 시작해서 102(40%)로
                        steam_surface = image_steam.convert_alpha()
                        steam_surface.set_alpha(steam_alpha)
                        background.blit(steam_surface, (0, 0))

                    if elapsed_time >= 10:  # 10초 후 숫자 표시 시작
                        if number_start_time is None:
                            number_start_time = current_time
                            solve_sound.play()  # 문제 해결 효과음 재생
                            story_text_system.set_text("어...? 뭔가 보이기 시작한다!", "권도현")
                            story_text_system.add_text_to_queue("5....2....3? 이건 또 무슨 의미일까..", "권?현")
                            story_text_system.add_text_to_queue("그러고보니... 너무 이상하다.. 자꾸만 이상한 곳에 오게되고...", "ㅇ도현")
                            story_text_system.add_text_to_queue("알 수 없는 문제들을 우연히 마주한다...", "권--")
                            story_text_system.add_text_to_queue("우진 선배는 어떻게 됐을까?", "권도?")
                            story_text_system.add_text_to_queue("나는 뭘 하다가 5호관에 다시 왔지?", "권??")
                            story_text_system.add_text_to_queue("이 다음은 어디로 가게 되는걸까?", "권도")
                            story_text_system.add_text_to_queue("나는 누구지?", "???")

                        if number_start_time is not None:
                            number_elapsed = (current_time - number_start_time) / 1000
                            if number_elapsed <= 3:  # 3초 동안 숫자 페이드 인
                                number_alpha = min(255, int(number_elapsed * 85))
                                number_surface = image_mirror_number.convert_alpha()
                                number_surface.set_alpha(number_alpha)
                                background.blit(number_surface, (365, 135))
                            else:
                                effects_completed = True  # 모든 효과가 완료됨

                else:  # 효과가 완료된 후 - 최종 상태 유지
                    # 완성된 거울 김서림 표시
                    mirror_steam_surface = image_mirror_steam.convert_alpha()
                    mirror_steam_surface.set_alpha(255)
                    background.blit(mirror_steam_surface, (355, 100))

                    # 완성된 전체 화면 김서림 표시
                    steam_surface = image_steam.convert_alpha()
                    steam_surface.set_alpha(102)  # 40% 불투명도
                    background.blit(steam_surface, (0, 0))

                    # 완성된 숫자 표시
                    number_surface = image_mirror_number.convert_alpha()
                    number_surface.set_alpha(255)
                    background.blit(number_surface, (365, 135))

            # UI 요소들은 항상 효과 위에 그리기
            background.blit(image_cold, (182, 338))
            background.blit(image_hot, (585, 338))
            background.blit(image_washstand, (330, 445))

            # 수도꼭지 클릭 영역 정의
            cold_water_rect = pygame.Rect(182, 338, 143, 262)  # 냉수
            hot_water_rect = pygame.Rect(585, 338, 143, 262)  # 온수

            # 마우스 호버 효과
            if cold_water_rect.collidepoint(mouse_pos):
                is_hovering = True
                tooltip.draw(background, "냉수 틀기", (mouse_x + 10, mouse_y))
            elif hot_water_rect.collidepoint(mouse_pos):
                is_hovering = True
                tooltip.draw(background, "온수 틀기", (mouse_x + 10, mouse_y))

            # 인벤토리 시스템 적용
        if show_inventory_ui:
            inventory_hovering = draw_inventory_system(background, mouse_pos, mouse_x, mouse_y)
            is_hovering = is_hovering or inventory_hovering

            # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mirror_zoom:
                    if cold_water_rect.collidepoint(event.pos):
                        story_text_system.set_text("이게 아닌 것 같다..", "권도현")
                    elif hot_water_rect.collidepoint(event.pos) and not hot_water_activated:
                        hot_water_activated = True
                        water_sound.play()
                        steam_start_time = pygame.time.get_ticks()
                        story_text_system.set_text("거울에 김이 서리기 시작했다..!", "권도현")
                story_text_system.handle_click(event.pos)

            if show_inventory_ui:
                handle_inventory_events(event)

        # 스토리 텍스트 및 시스템 업데이트
        story_text_system.update(background)
        custom_cursor.update(is_hovering)
    pygame.display.flip()