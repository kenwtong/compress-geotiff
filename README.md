# Compress GeoTiff

A Python script implementing Paul Ramsey's post [GeoTiff Compression for Dummies](http://blog.cleverelephant.ca/2015/02/geotiff-compression-for-dummies.html).


## Dependencies

- Python 2.7
- The [GDAL/OGR](http://trac.osgeo.org/gdal/wiki/DownloadingGdalBinaries) binaries are required.


## Setup

Download compress_geotiff.py and config.ini. Edit config.ini with the paths to your GDAL/OGR installation.


## Usage

### Python 2.7

Run the compress_geotiff.py script from your prompt, with -f or --file flag specifying the path to the Geotiff and optionally include -o or --overviews if you want to create overviews.

`python compress_geotiff.py  -f <full path to geotiff> [-o (optional)]`

Run `compress_geotiff.py -h` for help with the arguments.