About
============

The Political Memory is a tool build by [la Quadrature du Net](http://lqdn.fr).
This repository is the [Quadrature du Net instance](https://memopol.lqdn.fr/) to track the European Parliament.
If you want to setup your own instance, you must follow the installation instructions of the [memopol-core](https://gitorious.org/memopol-core).

Installation for development
============================

Memopol with lqdn's customization is little bit more complex to install than a normal django project, but not that much more complicated.

Debian and debian-based
-----------------------

Install the base python virtualenv tools (on Ubuntu you have to enable universe):

    sudo apt-get install python-setuptools python-dev libxml2-dev libxslt1-dev libfreetype6-dev libpng12-dev python-pip libatlas-base-dev g++ mercurial git libtidy-dev imagemagick ruby-sass
    sudo pip install virtualenv

Archlinux
---------

Install the following to have the tools on Archlinux (please note that you may have to adapt the following install procedure):

    pacman -S python2 libxml2 libxslt freetype2 python-lxml python2-pip python2-virtualenv libpng mercurial git imagemagick tidyhtml ruby-sass

Fedora
------

Install the following to have the tools on Fedora (please note that you may have to adapt the following install procedure):

    yum install python-setuptools python-devel libxml2-devel libxslt-devel freetype freetype-devel libpng libpng-devel python-lxml python-pip atlas-devel g++ mercurial git imagemagick rubygem-sass

    pip-python install virtualenv


Python dependencies
-------------------

In a directory:

    git clone git://gitorious.org/memopol2-0/memopol2-0.git
    git clone git://gitorious.org/memopol2-0/memopol-core.git
    cd memopol2-0
    ln -s ../memopol-core/memopol .
    virtualenv ve
    source ve/bin/activate
    pip install -r requirements-dev.txt
    pip install numpy
    pip install -r ../memopol-core/requirements.txt
    python manage.py init

And you should be done.

To enter the virtualenv
    source ve/bin/activate

To quit the virtualenv
    deactivate

Run the server
--------------

    python manage.py runserver

Your application is available on http://localhost:8000/

And you're done, but you might want to take a look at the next section
depending on what you want to dev.

You can find more informations on how to use memopol in the memopol-core [README.md](https://gitorious.org/memopol2-0/memopol-core/blobs/master/README.md)

Licence
=======

The Political Memory is licenced under aGPLv3+. The original idea is from [gibus](http://gibus.sedrati-dinet.net/).
