#!/bin/bash
. /usr/local/bin/virtualenvwrapper.sh
export WORKON_HOME=~/.virtualenvs
workon koto-faucet
uwsgi --ini uwsgi.ini
