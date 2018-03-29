# koto-faucet

## Installation

(1) prepare
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

(3) create db and starat flask app
```
python initdb.py
./start.sh
```

(4) access http://localhost:5000/

