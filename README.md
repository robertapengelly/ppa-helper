# ppa-helper
A helper program for adding ppa's in ubuntu.

A program writen in python to make adding/updating ppa source's easier on Ubuntu distros.
The program will try using your distro for the given ppa's and fallback to the latest version before your distro if not available.

Usage:

* Open terminal (Ctrl + Alt + T)
```bash
* sudo apt-get install git
* In newer versions of make and/or older versions of python may not be intalled by default so run:
    sudo apt-get install make python
* git clone https://github.com/robertapengelly/ppa-helper.git
* cd ppa-helper
* make install

* Adding sources:
    ppa-helper --add "ppa:notepadqq-team/notepadqq ppa:otto-kesselgulasch/gimp"

* Updating sources:
    ppa-helper --update "ppa:notepadqq-team/notepadqq ppa:otto-kesselgulasch/gimp"
  
  Alternativly you can run ppa-helper --update to update all existing sources within the
  sources.list.d directory.
```
