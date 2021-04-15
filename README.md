An open-source project with the purpose of building a REST API for using GIMX over http. This is quite useful for projects that want to use GIMX over network, such as an android app for controlling a remote GIMX device. This project is built under python-flask.

## Installation

Clone the repository:
```
git clone https://github.com/Lucashsmello/GIMX-WebAPI.git
```
or download [lastest release](/../../releases/latest) (installer.tar.gz) and unpack it.

Open a terminal in the downloaded repository folder and install requirements:
```
sudo apt install python3 python3-pip
python3 -m pip install -U pip setuptools
pip3 install -r requirements.txt
```
Finally run install.sh specifying an arbitrary directory to install with option `--install-dir`:
```
./install.sh --install-dir /path/to/gimx-webapi/releases/
```
**Note:** if you already have installed gimx, or you did not downloaded the released package, consider installing with option `--dont-install-gimx`:
```bash
./install.sh --install-dir /path/to/gimx-webapi/releases/ --dont-install-gimx
```
Run `./install.sh --help` for more help.

You can test if it is working by acessing `IP:PORT/gimx/api/v1/version` (Ex: [http://localhost:51916/gimx/api/v1/version](http://localhost:51916/gimx/api/v1/version)) or running
```bash
curl http://localhost:51916/gimx/api/v1/version
```
It must show your installed version.

To uninstall, run with `--uninstall` as an option:
```
./install.sh --uninstall
```

See documentation at [doc/webapi.md](doc/webapi.md).

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=9HSBCLLHHDMAY&item_name=Development+of+GIMX+Web+API,+GIMX+Android+and+improvement+of+GIMX+Mouse2Axis+translation&currency_code=BRL&source=url)
