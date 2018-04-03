#!/bin/bash
. /usr/local/bin/virtualenvwrapper.sh
export WORKON_HOME=~/.virtualenvs
workon koto-faucet
python shielder.py >> shielder.log 2>&1
