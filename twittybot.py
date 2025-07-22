import os
from dotenv import load_dotenv
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

# Load environment variables
load_dotenv()

APP_ID = os.getenv('TWITCH_APP_ID')
APP_SECRET = os.getenv('TWITCH_APP_SECRET')
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL')

if not APP_ID or not APP_SECRET or not TARGET_CHANNEL:
    print("Error: Missing required environment variables!")
    print("Please check your .env file contains:")
    print("TWITCH_APP_ID=your_app_id")
    print("TWITCH_APP_SECRET=your_secret") 
    print("TARGET_CHANNEL=your_channel")
    exit(1)

USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]

con = sqlite3.connect("meteorlite.db")

def sql_table(con):
    cursorObj = con.cursor()
    cursorObj.execute("CREATE TABLE if not exists user(id integer PRIMARY KEY, username text, color text)")
    con.commit()

def sql_insert(con, userData):
    cursorObj = con.cursor()
    cursorObj.execute('INSERT INTO user(id, name, ipv4, latitude, longitude, gridX, gridY, office, date, time) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', userData)
    con.commit()

def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

class MainWindow(QMainWindow):
    chatMessage = Signal(str, str, float)
    adjustScroll = Signal(bool)
    outgoingChat = Signal(str)
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setFixedSize(300, 500)
        self.setGeometry(500, 500, 500, 500)

        self.scroll = QScrollArea()             
        self.widget = QWidget()
        self.setWindowTitle("Twitch Panel")              
        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(5,0,5,5)
        self.widget.setLayout(self.vbox)

        self.topvbox = QVBoxLayout()
        self.bottomvbox = QHBoxLayout()
        
        self.vbox.addLayout(self.topvbox)
        self.vbox.addLayout(self.bottomvbox)
    
        self.spacer = QSpacerItem(0,0,QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.topvbox.addSpacerItem(self.spacer)

        self.indicatorButton = QPushButton()
        self.indicatorButton.setStyleSheet("background-color : red")
        self.bottomvbox.addWidget(self.indicatorButton)
        self.indicatorButton.setEnabled(False)

        self.scrollBar = self.scroll.verticalScrollBar()

        #Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)
        self.setCentralWidget(self.scroll)

        self.chatButton = QPushButton("Chat")
        self.chatButton.clicked.connect(self.post)

        self.enterField = QLineEdit("")
        self.bottomvbox.addWidget(self.enterField)

        self.bottomvbox.addWidget(self.chatButton)

        self.chatMessage.connect(self.test)
        self.adjustScroll.connect(self.scrollRefresh)
        self.scrollBar.rangeChanged.connect(self.scrollRefresh)

        self.twitchThread = QThread(self)
        self.worker = TwitchWorker()
        self.worker.moveToThread(self.twitchThread)
        self.twitchThread.started.connect(self.worker.signalToRun)
        self.twitchThread.start()
        
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

    def post(self):
        asyncio.run(self.worker.chat.send_message(TARGET_CHANNEL, self.enterField.text()))
        self.enterField.setText("")

    def scrollRefresh(self):
        self.scrollBar.setValue(self.scrollBar.maximum())
    

class TwitchWorker(QtCore.QObject):
    sendBees = Signal(str)
    def __init__(self, parent=None):
        super(TwitchWorker, self).__init__(parent)
        self.sendBees.connect(self.greenlight)
    
    def greenlight(self):
        w.indicatorButton.setStyleSheet("background-color: green")

    async def sendMsg(self):
        await self.chat.send_message(TARGET_CHANNEL, "hey")
        
    def signalToRun(self):
        asyncio.run(self.run())
        

    # this will be called whenever the !reply command is issued
    async def test_command(self, cmd: ChatCommand):
        await cmd.reply('success')

    # this will be called when the event READY is triggered, which will be on bot start
    async def on_ready(self, ready_event: EventData):
        print('Bot is ready for work, joining channels')
        # join our target channel, if you want to join multiple, either call join for each individually
        # or even better pass a list of channels as the argument
        await ready_event.chat.join_room(TARGET_CHANNEL)
        # you can do other bot initialization things in here

    # this will be called whenever a message in a channel was send by either the bot OR another user
    async def on_message(self, msg: ChatMessage):
        # print(f'in {msg.room.name}, {msg.user.name} said: {msg.text} at {msg.sent_timestamp}')
        w.chatMessage.emit(msg.text, msg.user.name, msg.sent_timestamp)

    # this will be called whenever someone subscribes to a channel
    async def on_sub(self, sub: ChatSub):
        print(f'New subscription in {sub.room.name}:\n'
            f'  Type: {sub.sub_plan}\n'
            f'  Message: {sub.sub_message}')

    # this is where we set up the bot
    async def run(self):

        # set up twitch api instance and add user authentication with some scopes
        twitch = await Twitch(APP_ID, APP_SECRET)
        auth = UserAuthenticator(twitch, USER_SCOPE)
        token, refresh_token = await auth.authenticate()
        await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

        # create chat instance
        self.chat = await Chat(twitch)

        # register the handlers for the events you want

        # listen to when the bot is done starting up and ready to join channels
        self.chat.register_event(ChatEvent.READY, self.on_ready)
        # listen to chat messages
        self.chat.register_event(ChatEvent.MESSAGE, self.on_message)
        # listen to channel subscriptions
        self.chat.register_event(ChatEvent.SUB, self.on_sub)

        # there are more events, you can view them all in this documentation

        # you can directly register commands and their handlers, this will register the !reply command
        self.chat.register_command('reply', self.test_command)

        # we are done with our setup, lets start this bot up!
        self.chat.start()

        self.sendBees.emit("")
        
        # lets run till we press enter in the console
        try:
            input('press ENTER to stop\n')
        finally:
            # now we can close the chat bot and the twitch api client
            self.chat.stop()
            await twitch.close()
    

app = QApplication(sys.argv)
w = MainWindow()
w.show() # Windows are hidden by default
# Starts the event loop
app.exec()
# Only need one per application