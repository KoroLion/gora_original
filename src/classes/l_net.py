"""!
@file Сеть
@brief Простая работа с сетью
"""
import asyncio


class LNet(object):
    """!
    @brief Класс для простой работы с сетью
    """
    def __init__(self, ip: str, port: int, timeout: float=0.5):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.loop = asyncio.new_event_loop()
        self.connected = False
        self.reader, self.writer = None, None

    def connect(self):
        """!
        @brief подключиться к серверу
        """
        async def tcp_init(loop):
            reader, writer = await asyncio.open_connection(self.ip, self.port, loop=loop)
            return reader, writer

        try:
            self.reader, self.writer = self.loop.run_until_complete(tcp_init(self.loop))
            self.connected = True
        except ConnectionError:
            print('Connection error!')

    def tcp_send(self, data: str) -> str:
        """!
        @brief отправить строку
        @param data отправляемая строка (str)
        @return ответ сервера (str)
        """
        if self.connected:
            async def tcp_client(message):
                message += '\n'
                self.writer.write(message.encode())

                # даём возможность буферу очиститься
                await self.writer.drain()

                recv = await self.reader.readline()

                return recv.decode()

            data = self.loop.run_until_complete(tcp_client(data))
            return data

    def disconnect(self):
        """!
        @brief отключиться от сервера
        """
        if self.connected:
            self.writer.close()
            self.loop.close()
            self.connected = False
