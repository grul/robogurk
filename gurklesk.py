#!/usr/bin/env python3
import sys
import socket
import time
import select
import traceback

from threading import Thread

from modules import titles, twitter, lunch

from config import *


class GurkLesk:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((SERVER, PORT))

        self.socket.send(bytes('USER %s %s %s %s\r\n' % (NICK, NICK, NICK, NICK), 'utf-8'))
        self.socket.send(bytes('NICK %s\r\n' % NICK, 'utf-8'))

        self.privmsg_listeners = []
        self.message_queue = []

    def main_loop(self):
        lines_received = 0
        readbuffer = ''
        last_message_sent = time.time()
        while True:
            tmp_buffer = readbuffer
            try:
                ready = select.select([self.socket], [], [], 1)
                if ready[0]:
                    readbuffer += self.socket.recv(1024).decode('utf-8')
            except KeyboardInterrupt:
                traceback.print_exc(file=sys.stdout)
                sys.exit(0)
            except:
                traceback.print_exc(file=sys.stdout)
                readbuffer = tmp_buffer
            # readbuffer = readbuffer + self.socket.recv(1024).decode('UTF-8')
            temp = str.split(readbuffer, '\n')
            readbuffer = temp.pop()

            for line in temp:
                line = line.strip()
                split_line = str.split(line)
                print(line)
                lines_received += 1
                if lines_received == 33:
                    self.socket.send(bytes('JOIN %s\r\n' % CHANNEL, 'UTF-8'))

                if(split_line[0] == 'PING'):
                    self.socket.send(bytes('PONG %s\r\n' % split_line[1], 'UTF-8'))
                if(split_line[1] == 'PRIVMSG'):
                    sender = ''
                    for char in split_line[0]:
                        if (char == '!'):
                            break
                        if (char != ':'):
                            sender += char
                    size = len(split_line)
                    i = 3
                    message = ''
                    while(i < size):
                        message += split_line[i] + ' '
                        i += 1
                    channel = ''
                    if split_line[2].startswith('#'):
                        channel = split_line[2]
                    if message.startswith(':'):
                        message = message[1:]
                    for listener in self.privmsg_listeners:
                        listener(sender, channel, message)
            if last_message_sent < (time.time() -2):
                last_message_sent = time.time()
                self.send_message()

    def queue_message(self, sender, message):
        self.message_queue.append((sender, message))

    def send_message(self):
        if len(self.message_queue) > 0:
            sender, message = self.message_queue.pop(0)
            self.socket.send(bytes('PRIVMSG %s :%s \r\n' % (sender, message), 'UTF-8'))

    def add_privmsg_listener(self, privmsg_listener):
        self.privmsg_listeners.append(privmsg_listener)

if __name__ == '__main__':
    gl = GurkLesk()
    titles_ = titles.Titles(gl)
    lunch_ = lunch.Lunch(gl)
    if twitter.has_config():
        thread = Thread(target=twitter.RoboStreamListener, args=(gl, CHANNEL))
        thread.start()
    gl.main_loop()


