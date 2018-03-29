# coding: utf8
import logging
from flask import Flask
from flask_wtf.csrf import CSRFProtect

from .kotorpc import KotoRPC
from .config import init_config
from .database import init_db

import model

csrf = CSRFProtect()
def create_app():
    app = Flask(__name__)
    init_config(app)
    init_db(app)
    csrf.init_app(app)

    return app

app = create_app()
app.app_context().push()

rpc = KotoRPC(app.config['KOTO_RPC_USER'], app.config['KOTO_RPC_PASSWORD'], testnet = app.config['KOTO_RPC_TESTNET'])

balance = rpc.getbalance()
app.logger.info("balance = %s", balance)
