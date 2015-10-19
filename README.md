# VPN

## Setup

How to setup on `Ubuntu 14.04.3 LTS`

```
chmod +x setup.sh
./setup.sh
```

## Ongoing Development

Packages are to be installed in the virtualenv `vpnenv` which can be activated through `source vpnenv/bin/activate`.

If you install a pip package, make sure to `pip freeze > PIP_REQUIREMENTS.txt` and add to git.

If you want to install all the requirements, run `pip install -r PIP_REQUIREMENTS.txt`.
