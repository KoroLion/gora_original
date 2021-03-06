"""!
@file Клиент
@brief Главный файл клиента
"""

import pygame
import math
import asyncio
from threading import Thread
from time import sleep, time

import configparser

try:
    import ujson as json
except ModuleNotFoundError:
    import json

from classes.pgu import gui

from classes.network_constants import *
from classes.helper_types import Size, Point
from classes.constants import FORM_WIDTH, FORM_HEIGHT, FPS

from classes.resources import Resources
from classes.core import Core
from classes.game import Game
from classes.game_object import Robot
from classes.gui_block import GuiPanel
from classes.texture import Texture

DEFAULT_PORT = 22000
TRACKING_CAMERA = True
MAX_CONNECT_ATTEMPTS = 3

CENTER_POS = Point(FORM_WIDTH / 2, FORM_HEIGHT / 2)

CONFIG_FILE = 'config.conf'


def get_angle(pl_pos: Point, size: Size, m_pos: Point) -> float:
    """!
    @brief Возращает угол между мышью и объектом

    @param pl_pos: Point(координаты игрока)
    @param size: Size(helper_types)
    @param m_pos: Point(координаты мыши)
    @return: float(градус поворота)
    """
    x = pl_pos.x + size.width / 2 - m_pos.x
    y = pl_pos.y + size.height / 2 - m_pos.y
    if x == 0:
        if y >= 0:
            return 90
        else:
            return 270
    else:
        angle = math.degrees(math.atan(y / x))
        if x > 0:
            return 180 - angle
        else:
            return -angle


class Client(object):
    """!
    @brief данные для взаимодействия потоков и основные функции для работы с сетью
    """

    def __init__(self):
        self.commands = []
        self.angle = 0
        self.id = None
        self.transport = None
        self.protocol = None
        self.loop = asyncio.get_event_loop()
        self.input = True

        self.login = ''
        self.skin = None
        self.ip = ''
        self.port = DEFAULT_PORT
        self.ping_send_time = time()
        self.ping = 0

    def connect(self):
        con = self.loop.create_datagram_endpoint(
            lambda: UdpClientProtocol(self.loop),
            remote_addr=(client.ip, client.port))

        if not self.connected():
            try:
                self.transport, self.protocol = self.loop.run_until_complete(con)
                return not self.transport.is_closing()
            except BaseException:
                print('#ERROR: Socket error!')
                return False
        else:
            return True

    def send(self, to_send):
        if self.connected():
            data = json.dumps(to_send)
            self.transport.sendto(data.encode())
            return True

        return False

    def disconnect(self):
        if self.connected():
            data = json.dumps([DISCONNECT])
            self.transport.sendto(data.encode())
            self.transport.close()
            return True

        return False

    def connected(self):
        if self.transport:
            return not self.transport.is_closing()

        return False


def main():
    """!
    @brief Поток отображения клиента
    """
    player = None
    while not main_form.terminated:
        for event in pygame.event.get():
            main_form.gui_events(event)

            if event.type == pygame.QUIT:
                main_form.terminate()

            elif client.connected():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        client.disconnect()
                    if client.input:
                        if event.key == pygame.K_w:
                            client.send([BUTTON_DOWN, B_GO_TOP])
                        if event.key == pygame.K_s:
                            client.send([BUTTON_DOWN, B_GO_BOTTOM])
                        if event.key == pygame.K_a:
                            client.send([BUTTON_DOWN, B_GO_LEFT])
                        if event.key == pygame.K_d:
                            client.send([BUTTON_DOWN, B_GO_RIGHT])

                elif event.type == pygame.KEYUP:
                    if client.input:
                        if event.key == pygame.K_w:
                            client.send([BUTTON_UP, B_GO_TOP])
                        if event.key == pygame.K_s:
                            client.send([BUTTON_UP, B_GO_BOTTOM])
                        if event.key == pygame.K_a:
                            client.send([BUTTON_UP, B_GO_LEFT])
                        if event.key == pygame.K_d:
                            client.send([BUTTON_UP, B_GO_RIGHT])
                elif event.type == pygame.MOUSEMOTION:
                    if client.input:
                        client.send([ANGLE, client.angle])

        if game.players.get(client.id):
            # получаем объект игрока (который играет с этого клиента =) )
            player = game.players.get(client.id)

            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = Point(mouse_pos[0], mouse_pos[1])

            if TRACKING_CAMERA:
                client.angle = get_angle(CENTER_POS, player.size, mouse_pos)
            else:
                client.angle = get_angle(player.position, player.size, mouse_pos)

        res.update()
        game.update()
        if player:
            main_form.update(camera_mode=TRACKING_CAMERA, point=player.position)
        else:
            main_form.update(camera_mode=TRACKING_CAMERA, point=Point(0, 0))

    client.disconnect()


class UdpClientProtocol(asyncio.DatagramProtocol):
    """!
    @brief "обёртка" над сокетами для удобной работы с сетью
    """
    def __init__(self, loop):
        self.loop = loop
        self.transport = None

    def connection_made(self, transport):
        addr = transport.get_extra_info('peername')
        print('Successfully connected to {}:{}!'.format(addr[0], addr[1]))

        self.transport = transport
        data = json.dumps([CONNECT, client.login, client.skin])
        self.transport.sendto(data.encode())

    def datagram_received(self, data, addr):
        data = data.decode()
        data = json.loads(data)
        command = data[0]

        if command == DATA:
            players = data[1]

            # собираем ID сервера
            visible_pids = []
            for player in players:
                visible_pids.append(player[J_ID])

            # собираем ID клиента
            client_pids = []
            for pid in game.players:
                client_pids.append(pid)

            # удаляем лишние объекты игроков на клиенте (которые отключились)
            for pid in client_pids:
                if not pid in visible_pids:
                    game.players.pop(pid)

            for player in players:
                pid = player[J_ID]

                if not game.players.get(pid):
                    if player[J_SKIN] == SKIN_BLUE:
                        skin = Texture("images/robots/textures/robot_blue.png")
                    elif player[J_SKIN] == SKIN_ORANGE:
                        skin = Texture("images/robots/textures/robot_orange.png")
                    else:
                        skin = Texture("images/robots/textures/robot_green.png")

                    new_player = {pid: Robot(Point(0, 0), skin, angle=0)}
                    new_player[pid].texture.set_size(Size(30, 30))
                    game.players.update(new_player)

                game.players[pid].position = Point(player[J_POSITION_X], player[J_POSITION_Y])
                game.players[pid].texture.set_angle(player[J_ANGLE])
        elif command == ID:
            client.id = data[1]
        elif command == KICK:
            info_label.set_text('You have been kicked from the server!')
            client.disconnect()
        elif command == MESSAGE:
            chat_area.value += '{}: {}'.format(data[2], data[1]) + '\n'
        elif command == PING:
            client.ping = round((time() - client.ping_send_time) * 1000)  # мс

    def error_received(self, exc):
        print('Error received:', exc)
        print('Closing connection...')
        self.transport.close()

    def connection_lost(self, exc):
        print('Connection closed!')


async def disconnect_check():
    """!
    @brief проверка необходимости отключения + пинг сервера
    """
    # периодически проверяем: не нужно ли отключиться
    while client.connected():
        client.ping_send_time = time()
        client.send([PING])
        ping_label.value = '{} ms'.format(client.ping)
        await asyncio.sleep(1)

    game_gui_panel.visible = False
    auth_panel.visible = True


def send_message():
    if len(message_input.value) > 0:
        client.send([MESSAGE, message_input.value])
        message_input.value = ''


def connect():
    """!
    @brief подключение к серверу
    """
    send_button.connect(gui.CLICK, send_message)
    client.login = login_input.value
    client.skin = skin_select.value
    # проверяем корректность заполнения полей
    if ':' in addr_input.value:
        addr = addr_input.value.split(':', 1)
    else:
        addr = [addr_input.value, DEFAULT_PORT]
    if len(addr[0]) == 0:
        info_label.set_text('Please, specify the address of the server!')
        return False
    if addr[0] == 'localhost':
        addr[0] = '127.0.0.1'
    client.ip, client.port = addr[0], addr[1]

    if len(client.login) < 3:
        info_label.set_text('Your login is too short!')
        return False
    if not client.skin:
        info_label.set_text('You have not selected a skin!')
        return False

    # пытаемся подключиться
    c_attempts = 0
    print('Trying to connect...')
    info_text = 'Connecting to {}:{}'.format(client.ip, client.port)
    info_label.set_text(info_text)
    while not client.connect() and c_attempts < MAX_CONNECT_ATTEMPTS:
        info_label.set_text(info_text)
        print('Connection attempt failed!')
        sleep(2)
        print('Trying to connect...')
        c_attempts += 1
        info_text += '.'

    if client.connected():
        auth_panel.visible = False
        game_gui_panel.visible = True
        client.loop.run_until_complete(disconnect_check())
    else:
        print('Server {}:{} is unavailable!'.format(client.ip, client.port))
        info_label.set_text('Server {}:{} is unavailable!'.format(client.ip, client.port))


def connect_action():
    """!
    @brief создание и запуск потока, работающего с сетью
    """
    net = Thread(target=connect)
    net.daemon = True
    net.start()


def save_settings():
    """!
    @brief сохранение настроек
    """
    config = configparser.ConfigParser({})
    config.add_section('main_settings')

    config.set('main_settings', 'address', addr_input.value)
    config.set('main_settings', 'login', login_input.value)
    config.set('main_settings', 'skin', str(skin_select.value))

    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)


def load_settings():
    """!
    @brief загрузка настроек
    """
    config = configparser.ConfigParser({})
    config.read(CONFIG_FILE)

    try:
        addr_input.value = config.get('main_settings', 'address')
        login_input.value = config.get('main_settings', 'login')
        skin_select.value = int(config.get('main_settings', 'skin'))
    except BaseException:
        print('#ERROR: Config reading error!')


def auth_panel_init():
    """!
    @brief сборка панели авторизации
    """
    addr_label = gui.Label('Адрес: ')

    title_label = gui.Label('GORA')
    title_label.set_font(pygame.font.SysFont('Tahoma', 30))
    login_button = gui.Button('Присоединиться', width=140, height=40)

    skin_select.add('Синий', SKIN_BLUE)
    skin_select.add('Зелёный', SKIN_GREEN)
    skin_select.add('Оранжевый', SKIN_ORANGE)
    skin_label = gui.Label('Скин:')

    login_button.connect(gui.CLICK, connect_action)
    login_label = gui.Label('Логин: ')
    password_label = gui.Label('Пароль: ')

    form.tr()
    form.td(title_label, colspan=2)
    form.tr()
    form.td(info_label, colspan=2)
    form.tr()
    form.td(addr_label)
    form.td(addr_input)
    form.tr()
    form.td(login_label)
    form.td(login_input)
    form.tr()
    form.td(password_label)
    form.td(password_input)
    form.tr()
    form.td(skin_label)
    form.td(skin_select)
    form.tr()
    form.td(login_button, colspan=2)


def message_input_focus():
    client.input = False


def message_input_blur():
    client.input = True


if __name__ == "__main__":
    pygame.init()

    client = Client()

    res = Resources(sounds_volume=0.5)

    main_form = Core("GORA alpha 0.3", Size(FORM_WIDTH, FORM_HEIGHT), res.background, FPS * 1)
    game = Game(res)
    main_form.add_object(game)

    # создаём панель входа
    auth_gui = gui.Desktop(theme=gui.Theme('gora_theme'))
    form = gui.Table(height=250, width=320)  # todo: Возможно лучше использовать gui.Form?

    info_label = gui.Label('')
    addr_input = gui.Input(width=140, height=20)
    login_input = gui.Input(width=140, height=20)
    password_input = gui.Input(width=140, height=20)
    skin_select = gui.Select(width=152)

    auth_panel_init()
    auth_panel = GuiPanel(main_form.surface.get_size(), auth_gui, form)
    main_form.add_gui(auth_panel)

    # создаём панель игрового интерфейса (карта, чат)
    game_gui_app = gui.Desktop(theme=gui.Theme('gora_theme'))
    chat_area = gui.TextArea(width=300, height=150)
    chat_area.editable = False
    message_input = gui.Input(width=199)
    message_input.connect(gui.FOCUS, message_input_focus)
    message_input.connect(gui.BLUR, message_input_blur)
    send_button = gui.Button('Отправить', height=25)
    ping_label = gui.Label('0 мс                  ', width=100)

    game_gui_container = gui.Container(width=main_form.surface.get_size()[0], height=main_form.surface.get_size()[1])
    game_gui_container.add(chat_area, 0, 0)
    game_gui_container.add(message_input, 0, 155)
    game_gui_container.add(send_button, 210, 155)
    game_gui_container.add(ping_label, 2, 2)
    game_gui_panel = GuiPanel(main_form.surface.get_size(), game_gui_app, game_gui_container,
                              background_c=pygame.Color("#00000000"))
    main_form.add_gui(game_gui_panel)
    game_gui_panel.visible = False

    load_settings()

    main()

    save_settings()
