#!/usr/bin/env python
# coding: utf8

import time
from datetime import datetime
from KotoFaucet.kotorpc import KotoRPC, KotoRPCException, KOTO
import logging

logging.basicConfig(format = '%(asctime)s %(name)s: %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

rpcuser = "kotorpcuser"
rpcpass = "kotorpcpass"
rpc = KotoRPC(rpcuser, rpcpass, testnet=True)

zaddr = "zto5xuxcYqohanWqG2KuM2nHP44hzbVLMKHxW44NojpYEqrjWAKX3vm13hWFrPKwvVsLpBaEqRjJpQobsrVAtPbqq66QxeK"
kaddr = "kmH8CnidTZZ7FKsdztWdgviLDa3AXyvUzfM"

#shieldしてope
def shield_koto(zaddr, fee = KOTO.DEFAULT_FEE):
    try:
        r = rpc.z_shieldcoinbase("*", zaddr, fee)
        opid = r["opid"]
        amount = r["shieldingValue"]

        logger.info("shielding %f koto" % amount)
        logger.info("  opid=%s" % opid)

        while True:
            s = rpc.z_getoperationstatus([opid])[0]
            logger.debug("unshield_koto: status=%s", s["status"])
            if s["status"] == "success":
                break
            elif s["status"] != "executing" and s["status"] != "queued":
                logger.warning("unknown status: %s" % s["status"])
                return -1
            time.sleep(10)
        
        #z_getoperationresultを呼び出して、kotod内のstatusを消す
        s = rpc.z_getoperationresult([opid])[0]

        logger.info("shielding done")
        logger.info("  txid=%s" % s["result"]["txid"])

        return amount - s["params"]["fee"]

    except KotoRPCException as e:
        logger.error("ERROR: %s", e)
    
    return -1

# unshieldしてoperationが終わるまで待つ。
# amountのFeeはzaddrから引かれるのであらかじめ引いておくこと
def unshield_koto(zaddr, kaddr, amount, fee = KOTO.DEFAULT_FEE):
    try:
        opid = rpc.z_sendmany(zaddr, [{"address": kaddr, "amount": amount}], fee = fee)
        logger.info("unshielding %f koto" % amount)
        logger.info("  opid=%s" % opid)

        while True:
            s = rpc.z_getoperationstatus([opid])[0]
            logger.debug("unshield_koto: status=%s", s["status"])
            if s["status"] == "success":
                break
            elif s["status"] != "executing" and s["status"] != "queued":
                logger.warning("unknown status: %s" % s["status"])
                return False
            time.sleep(10)

        #z_getoperationresultを呼び出して、kotod内のstatusを消す
        s = rpc.z_getoperationresult([opid])[0]

        logger.info("unshielding done")
        logger.info("  txid=%s" % s["result"]["txid"])

        return True

    except KotoRPCException as e:
        logger.error("ERROR: %s", e)
    
    return False

#addrの残高がamount以上になるまで待つ。
#  amount以上になったらTrue
#  timeout(デフォルト120秒)立つとFalse
#  mincoinfを指定すると、指定したConfirm以上の残高のみ表示
def waitbalance(addr, amount, minconf = 1, timeout = 600):
    if timeout / 60 < minconf:
        timeout = (minconf + 1) * 60
    
    t = time.time()
    b = rpc.z_getbalance(addr, minconf)
    logger.debug("balance: %s / %s", b, amount)

    while b < amount:
        # timeout ?
        if t + timeout < time.time():
            return False
        
        time.sleep(10)
        b = rpc.z_getbalance(addr, minconf)
        logger.debug("balance: %s / %s", b, amount)
    
    return True

while True:
    logger.info("> start shielding")
    amount = shield_koto(zaddr)
    logger.info("> result=%f" % amount)
    if amount > 0:
        logger.info("> waiting confirm")
        r = waitbalance(zaddr, amount, minconf=3)
        logger.info("waitbalance: %s", r)
        amount = rpc.z_getbalance(zaddr, minconf=3)
        logger.info("> start unshielding: amount = %s", amount)
        r = unshield_koto(zaddr, kaddr, amount - KOTO.DEFAULT_FEE)
        logger.info("unshield_koto: %s", r)
    logger.info("> finished")
    time.sleep(1200)
