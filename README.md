# VPN

A 'VPN' developed to follow [these instructions](http://courses.ece.ubc.ca/cpen442/assignments/vpn.html "CPEN 442").

[Export this file to PDF](EXPORT.md)

## Setup

How to setup on `Ubuntu 14.04.3 LTS` with default `Python 2.7.6` (out of date, but default)

```
chmod +x setup.sh
./setup.sh
```

## Ongoing Development

Packages are to be installed in the virtualenv `vpnenv` which can be activated through `source vpnenv/bin/activate`.

If you install a pip package, make sure to `python pip_freeze.py` which dumps your installed packages to `PIP_REQUIREMENTS.txt` and also runs a `git add` on that file.

If you want to install all the requirements, run `pip install -r PIP_REQUIREMENTS.txt`.

## How the VPN works

#### How the data is actually sent/received, and protected
  
  Answer goes here.

#### Mutual authentication and key establishment protocols

 * Protocols:
 * Why we chose them, and the computation performed by each side at each step in the protocol(s):

#### Derivation of encryption and integrity-protection keys from the shared secret value

 * If we were implementing this VPN as a real-world product for sale, what algorithms, modulus sizes, encryption key size, and integrity key size would we use?

#### Program details

 * Explanation of what language the software is written in:
 * Size of the program (lines of code; size of the executable):
 * Modules or major architectural components of your program (along with inputs, outputs, and functionality for each):
  * We used the Twisted framework for our chat functionality.  It allows us to use boilerplate functionality to create a versatile asyncronous two way chat server.
  * We modified a boilerplate echo server to only allow one connection and function as either a client or server depending on which had already been opened on the target `address:port` pair.
