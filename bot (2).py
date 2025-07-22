from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
import asyncio
from PySide6 import QtCore
from PySide6.QtCore import *
from PySide6.QtWidgets import * # QApplication, QMainWindow, QLabel, QWidget, QPushButton, QGridLayout
from PySide6.QtGui import *
import sys
import sqlite3
import random
import os
from dotenv import load_dotenv

load_dotenv()

con = sqlite3.connect("meteorlite.db")

def sql_table(con):
    cursorObj = con.cursor()
    # Add the missing closing parenthesis:
    cursorObj.execute("CREATE TABLE if not exists user(id integer PRIMARY KEY, username text, color text)")
    con.commit()

def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

class Thread(QThread):
    # """
    # Worker thread
    # """
    result = Signal(str)

    @Slot()
    def run(self):
        print("Thread Start")
        while True:
            asyncio.run(run())

class MainWindow(QMainWindow):
    chatMessage = Signal(str, str, int)
    adjustScroll = Signal(bool)
    outgoingChat = Signal(str)
    def __init__(self):
        super().__init__()
        self.twitchThread = Thread(parent=self)
        self.twitchThread.start()

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setFixedSize(300, 500)
        self.setGeometry(500, 500, 500, 500)

        self.scroll = QScrollArea()             
        self.widget = QWidget()                 
        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(5,0,5,5)
        self.widget.setLayout(self.vbox)

        self.topvbox = QVBoxLayout()
        self.bottomvbox = QHBoxLayout()
        
        self.vbox.addLayout(self.topvbox)
        self.vbox.addLayout(self.bottomvbox)
    

        self.spacer = QSpacerItem(0,0,QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.topvbox.addSpacerItem(self.spacer)

        
        self.scrollBar = self.scroll.verticalScrollBar()

        #Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)
        self.setCentralWidget(self.scroll)

        self.button = QPushButton("Enter")
        self.button.clicked.connect(self.post)
        

        self.enterField = QLineEdit("Enter text here...")
        self.bottomvbox.addWidget(self.enterField)
        self.bottomvbox.addWidget(self.button)

        self.chatMessage.connect(self.test)
        self.adjustScroll.connect(self.scrollRefresh)
        self.scrollBar.rangeChanged.connect(self.scrollRefresh)
    
    def test(self, message, name, time):
        print(f"SIGNAL RECIEVED, {message}")
        
        for i in range(1):
            r = int(random.randint(0,255))
            g = int(random.randint(0,255))
            b = int(random.randint(0,255))
            color = rgb_to_hex(r,g,b)
            
            
        self.object = QLabel(f"<font color='{color}'>{name}</font> - {message}")
  
        self.object.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.object.setAlignment(Qt.AlignTop)
        self.object.setWordWrap(True)
        self.object.setFixedWidth(self.width() - self.width()/10)
        self.object.setContentsMargins(5,0,5,5)
        self.topvbox.addWidget(self.object)


    def scrollRefresh(self):
        self.scrollBar.setValue(self.scrollBar.maximum())

    def post(self):
        """Handle button click to send chat message"""
        message = self.enterField.text()
        if message and message.strip() and message != "Enter text here...":
            # Clear the input field
            self.enterField.clear()
            
            # TODO: Implement actual message sending to Twitch
            # For now, just display it locally as a test
            self.chatMessage.emit(message, "You", 0)
            print(f"Would send to Twitch: {message}")

USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]

APP_ID = os.getenv('TWITCH_APP_ID')
APP_SECRET = os.getenv('TWITCH_APP_SECRET')
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL')

# this will be called when the event READY is triggered, which will be on bot start
async def on_ready(ready_event: EventData):
    print('Bot is ready for work, joining channels')
    # join our target channel, if you want to join multiple, either call join for each individually
    # or even better pass a list of channels as the argument
    await ready_event.chat.join_room(TARGET_CHANNEL)
    # you can do other bot initialization things in here


# this will be called whenever a message in a channel was send by either the bot OR another user
async def on_message(msg: ChatMessage):
    print(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')
    w.chatMessage.emit(msg.text, msg.user.name, msg.sent_timestamp)
    
    


# this will be called whenever someone subscribes to a channel
async def on_sub(sub: ChatSub):
    print(f'New subscription in {sub.room.name}:\n'
          f'  Type: {sub.sub_plan}\n'
          f'  Message: {sub.sub_message}')


# this will be called whenever the !reply command is issued
async def test_command(cmd: ChatCommand):
    if len(cmd.parameter) == 0:
        await cmd.reply('you did not tell me what to reply with')
    else:
        await cmd.reply(f'{cmd.user.name}: {cmd.parameter}')


# this is where we set up the bot
async def run():

    # set up twitch api instance and add user authentication with some scopes
    twitch = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(twitch, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

    # create chat instance
    chat = await Chat(twitch)

    # register the handlers for the events you want

    # listen to when the bot is done starting up and ready to join channels
    chat.register_event(ChatEvent.READY, on_ready)
    # listen to chat messages
    chat.register_event(ChatEvent.MESSAGE, on_message)
    # listen to channel subscriptions
    chat.register_event(ChatEvent.SUB, on_sub)

    # there are more events, you can view them all in this documentation

    # you can directly register commands and their handlers, this will register the !reply command
    chat.register_command('reply', test_command)

    # we are done with our setup, lets start this bot up!
    chat.start()
    
    # lets run till we press enter in the console
    try:
        input('press ENTER to stop\n')
    finally:
        # now we can close the chat bot and the twitch api client
        chat.stop()
        await twitch.close()
    
    
# asyncio.run(run())

app = QApplication(sys.argv)
w = MainWindow()
w.show() # Windows are hidden by default
# Starts the event loop
app.exec()
# Only need one per application

