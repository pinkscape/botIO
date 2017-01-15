# !/usr/bin/env python3
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import bson, time
from PIL import Image
from . import Framework

current_milli_time = lambda: int(round(time.time() * 1000))



class BotIOChromeExtension(Framework.Framework, SimpleWebSocketServer):

    def __init__(self, host='', port=9999):
        self.host = host
        self.port = port
        SimpleWebSocketServer.__init__(self, host, port, BotIOChromeExtensionSocket, selectInterval=0.1)

    def _constructWebSocket(self, sock, address):
        ws = self.websocketclass(self, sock, address)
        ws.framework_wrapper = self
        return ws

    def serveforever(self):
        print("Listening forever... <3 ")
        super(BotIOChromeExtension, self).serveforever()

    def run(self, learningscheme, architecture, save_after_cycles):
        super().__init__(learningscheme, architecture, save_after_cycles)
        server = BotIOChromeExtension(self.host, self.port)
        server.serveforever()



class BotIOChromeExtensionSocket(WebSocket):


    # === #
    # API #
    # === #
    awaits_img = False
    msg = {}
    numkeys = 0
    def control(self, keys):
        self.sendMessage(bson.dumps({"keys": keys}))

    # fps
    fps = 0
    fps_counter = 0
    fps_smooth = 0.9
    fps_last_timestamp = current_milli_time()
    def updateFPS(self):
        self.fps_current_timestamp = current_milli_time()
        if self.fps_current_timestamp - self.fps_last_timestamp > 1000:
            self.fps_last_timestamp = self.fps_current_timestamp
            self.fps = self.fps_counter
            self.fps_counter=0
        self.fps_counter+=1

    # image size
    width = 0
    height = 0


    # ======================= #
    # Connection to Framework #
    # ======================= #
    def __init__(self, server, sock, address):
        super(self.__class__,self).__init__(server, sock, address)


    # ==================== #
    # Server-Communication #
    # ==================== #

    def handleMessage(self):
        if not self.awaits_img:
            self.msg = bson.loads(self.data)

        # answers
        if self.msg["state"] == "game_start":
            print("game (re)started")
            self.width = self.msg["width"]
            self.height = self.msg["height"]
            self.height = self.msg["numkeys"]
            self.control([])
        elif self.msg["state"] == "game_running":

            # message consists of two parts (game_info + img)
            if not self.awaits_img:
                self.awaits_img = True
                return
            self.awaits_img = False

            # get data
            score = self.msg["score"]
            interaction = self.msg["interaction"]
            img = Image.frombuffer( "RGBA", (self.width, self.height), self.data, "raw", "RGBA", 0, 1)

            # learn ( using the image, the current score and last used keys )
            keys = self.framework_wrapper.react(img,interaction,score)

            # recalc fps
            self.updateFPS()
            print("\rFPS:",self.fps, " Score:",score, end="")

            # use next keys
            self.control(keys)

        elif self.msg["state"] == "game_ended":

            # score = msg["score"]
            print("game ended")

    def handleConnected(self):
        print('Connection established to ', self.address)

    def handleClose(self):
        print('Connection closed.')

