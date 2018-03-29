# coding: utf8

from flask import Flask, render_template, session, request
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, FloatField, validators
from sqlalchemy import desc

from .app import app, rpc, balance
from .database import db
import model

class FaucetForm(FlaskForm):
    address = StringField(u'送信先アドレス', validators=[validators.DataRequired()])
    amount = FloatField(u'送信量(Koto)', validators=[validators.DataRequired(), validators.NumberRange(min=0.01, max=100)])
    recaptcha = RecaptchaField()

@app.route('/', methods=('GET', 'POST'))
def index():
    msg = ""
    accepted = False
    form = FaucetForm()
    if form.validate_on_submit():
        amount = round(form.amount.data, 8)
        if rpc.checkaddr(form.address.data) and amount > 0:
            q = model.Queue(form.address.data, amount)
            db.session.add(q)
            db.session.commit()
            msg = "Successful Queued!"
            accepted = True
        else:
            form.address.errors = ["invalid address format or amount!"]
    
    queue = model.Queue.query.order_by(desc(model.Queue.id)).limit(30).all()
    return render_template('index.html', 
        title="Koto Testnet Faucet", 
        form=form, 
        accepted=accepted,
        msg=msg, 
        queue=queue, 
        label=model.QUEUE_STATE.LABEL,
        balance=balance)

