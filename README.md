# Mapnik render tiles

## Dependencies

..to build latest Mapnik from pypi.

### Debian Wheezy

```
apt-get install g++ cpp libicu-dev libicu48 python-dev libboost-system-dev libboost-filesystem-dev libboost-iostreams-dev libboost-thread-dev libboost-python-dev libboost-program-options-dev libboost-regex-dev libxml2 libxml2-dev libfreetype6 libfreetype6-dev libjpeg8 libjpeg8-dev libpng12-0 libpng12-dev libtiff5 libtiff5-dev libltdl7 libltdl-dev libproj0 libproj-dev libcairo2 libcairo2-dev python-cairo python-cairo-dev libcairomm-1.0-1 libcairomm-1.0-dev ttf-dejavu ttf-dejavu-core ttf-dejavu-extra ttf-unifont postgresql postgresql-server-dev-9.1 postgresql-contrib libgdal1-dev python-gdal postgresql-9.1-postgis libsqlite3-dev subversion build-essential python-nose libmapnik-dev
```

### Debian Jessie

libicu48 has been superseded by libicu52

```
apt-get install g++ cpp libicu-dev libicu52 python-dev libboost-system-dev libboost-filesystem-dev libboost-iostreams-dev libboost-thread-dev libboost-python-dev libboost-program-options-dev libboost-regex-dev libxml2 libxml2-dev libfreetype6 libfreetype6-dev libjpeg8 libjpeg8-dev libpng12-0 libpng12-dev libtiff5 libtiff5-dev libltdl7 libltdl-dev libproj0 libproj-dev libcairo2 libcairo2-dev python-cairo python-cairo-dev libcairomm-1.0-1 libcairomm-1.0-dev ttf-dejavu ttf-dejavu-core ttf-dejavu-extra ttf-unifont postgresql postgresql-server-dev-9.1 postgresql-contrib libgdal1-dev python-gdal postgresql-9.1-postgis libsqlite3-dev subversion build-essential python-nose libmapnik-dev
```

## Install app

```
virtualenv .venv2.7
source .venv2.7/bin/activate
pip install -r requirements.txt
```

## Run app

```
python tileserver.py
```

Visit http://127.0.0.1:5000.
