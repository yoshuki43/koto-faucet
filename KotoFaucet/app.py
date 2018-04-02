# coding: utf8
import sys
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

# DEBUG出ないときのログ出力設定
if not app.debug:
    app.logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d, pid=%(process)d/tid=%(thread)d]')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

app.logger.info("app is ready.")

# KOTO RPC
rpc = KotoRPC(app.config['KOTO_RPC_USER'], app.config['KOTO_RPC_PASSWORD'], testnet = app.config['KOTO_RPC_TESTNET'])
app.logger.info("kotod rpc object created.")

# 残高を計算してみる
balance = rpc.getbalance()
app.logger.info("balance = %s", balance)
