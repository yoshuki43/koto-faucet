# koto-faucet

## Installation

(1) prepare

nginx + python-dev
```
sudo apt-get install nginx
sudo apt-get install python-dev
```

(options)virtualenvwapper
```
sudo pip install virtualenvwapper
vi ~/.bashrc
----
#add this
source /usr/local/bin/virtualenvwrapper.sh
export WORKON_HOME=~/.virtualenvs
----
source ~/.bashrc
mkvirtualenv koto-faucet
workon koto-faucet
```

clone this repo.
```
git clone https://github.com/yoshuki43/koto-faucet
cd koto-faucet
pip install -r requirements.txt
```

(2) edit config.py
```
cp KotoFaucet/config.py-sample KotoFaucet/config.py
vi KotoFaucet/config.py
```
edit:
* SECRET_KEY
* KOTO_RPC_USER
* KOTO_RPC_PASSWORD
* RECAPTCHA_PUBLIC_KEY
* RECAPTCHA_PRIVATE_KEY

(3) create db

```
python initdb.py
```

(4) starat flask app

```
./start.sh
   or
./start_uwsgi.sh (this require virtualenvwapper/nginx settings)
```

(5) access http://localhost:5000/ (for start.sh)

## systemd

(1) edit misc/koto-faucet.service
(2) sudo cp misc/koto-faucet.service /etc/systemd/system/
(3) sudo systemctl daemon-reload
(4) sudo systemctl start koto-faucet.service

## nginx

vi /etc/nginx/site-enabled/default
```
service {
      :
    location ~ ^/faucet/(.*)$ {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/koto-faucet.sock;
        uwsgi_param SCRIPT_NAME /faucet;
        uwsgi_param PATH_INFO /$1;
    }
}
```

access http://localhost/faucet/