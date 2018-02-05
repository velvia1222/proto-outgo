# proto-outgo
二人の債務を記録し、任意のタイミングで精算するアプリ。<br>
現状raspberry pi上でスタンドアロンで稼働しているが、いずれWEBでも使えるようにしたい。
- プラットフォーム：raspberry pi3
- 言語：python3
- GUIライブラリ：kivy
- DB：sqlite

## インストール
### raspbianのインストールと基本設定
```
# raspbianイメージ書き込み
sudo dd bs=1M if=~/Desktop/2016-02-26-raspbian-jessie-lite.img of=/dev/sdb

# プライベートIP固定化
vim /etc/dhcpcd.conf
interface eth0
static ip_address=192.168.0.XXX/24
static routers=192.168.0.1
static domain_name_servers=192.168.0.1

# 初期設定
sudo raspi-config
# SDカード使用領域拡張、ロケール設定、ssh有効化等

# アップデート
sudo apt update
sudo apt upgrade
sudo apt dist-upgrade

# rootパスワード設定
sudo passwd root
# ユーザーを追加
sudo adduser XXX
sudo gpasswd -a XXX sudo
# コンソールログインに変更
sudo raspi-config
# 再起動して新ユーザーでログイン。再起動しないとpiユーザーのプロセスが残って削除できない
sudo reboot
# piユーザーを削除
sudo userdel -r pi
# sshでrootでのログインを禁止
sudo vim /etc/ssh/sshd_config
PermitRootLogin no

# ホスト名変更
vim /etc/hostname
vim /etc/hosts
```

### タッチパネル設定
- LCD35-showをSFTPで任意のディレクトリへコピー
```
# タッチパネルを270°回転して有効化
sudo ./LCD35-show 270
```

### cython、kivyに必要なライブラリをインストール
```
sudo apt install build-essential curl libavformat-dev libbz2-dev libncurses5-dev libncursesw5-dev libportmidi-dev libreadline-dev libsdl-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev libsqlite3-dev libssh-dev libssl-dev libswscale-dev llvm make wget xz-utils zlib1g-dev libgl1-mesa-dev libgles2-mesa-dev fonts-ipafont
```

### python設定
```
# pyenvインストール
git clone https://github.com/yyuu/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc
pyenv install 3.4.7
pyenv global 3.4.7

# venv設定
mkdir ~/.venv
pyvenv ~/.venv/outgo
. ~/.venv/outgo/bin/activate

# Pythonのライブラリをインストール
pip3 install -r ~/projects/proto-outgo/requirements.txt
```

### DB（sqlite）作成
```
~/projects/proto-outgo/create_sqlite.py
```

### proto-outgo起動
```
~/projects/proto-outgo/start.sh
```
