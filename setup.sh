sudo apt-get update
sudo apt-get -y install python-kivy
sudo apt-get -y install python-virtualenv
sudo apt-get -y install python-dev
virtualenv —system-site-packages vpnenv
source vpnenv/bin/activate
pip install -r PIP_REQUIREMENTS.txt
