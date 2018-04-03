# coding: utf8

import logging

from KotoFaucet.app import app
from KotoFaucet.sender import SenderThread
import KotoFaucet.view

if __name__ == '__main__':
    #app.logger.setLevel(logging.DEBUG)
    #sender = SenderThread()
    #sender.start()
    app.run()
