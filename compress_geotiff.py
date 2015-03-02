#-------------------------------------------------------------------------------
# Name:        compress_geotiff.py
# Version:     1.02
#
# Purpose:     This script uses gdal_translate to compress a geotiff using JPEG
#              compression and internally tiles the geotiff.
#
#              Overviews (Pyramids) will also be produced by gdaladdo
#              if specified.
#
# Author:      Ken Tong
#
# Created:     24/02/2015
#-------------------------------------------------------------------------------

import sys
import os
import subprocess
import ConfigParser


def _setup_gdal(config_file):
    """
       *** Function is meant for internal use***

        Function sets paths to gdallxx.dll, gdal/ogr executables, and creates
        gdal_data environment variable.

        Input:
        @config_file: configuration file (string)

        Output:
        @cmd_dict: a dictionary of to full path of gdal executables
    """
    config_file = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), r'config.ini')
    parser = ConfigParser.SafeConfigParser()
    parser.read(config_file)

    os.environ['PATH'] = ';'.join([parser.get('gdal_paths', 'bin_path'), parser.get('gdal_paths', 'exe_path')]) + ';' + os.environ['PATH']
    os.environ["GDAL_DATA"] = parser.get('gdal_paths', 'data_path')

    return {'gdal_translate': ' '.join([os.path.join(parser.get('gdal_paths', 'exe_path'), 'gdal_translate.exe'), r'-co COMPRESS=JPEG -co PHOTOMETRIC=YCBCR -co TILED=YES']),
            'gdaladdo':  ' '.join([os.path.join(parser.get('gdal_paths', 'exe_path'), 'gdaladdo.exe'), r'--config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r AVERAGE'])
           }


def get_output_filename(input_filename):
    """
        Function returns an anutomatically generated ouput filename with a
        '_jpeg' suffix right before the extension.

        Input:
        @input_filename: Full path to the input file (string)

        Output:
        Full path to the output file (string).
    """
    if os.path.isfile(input_filename):
        dirname = os.path.dirname(input_filename)
        output_filename = os.path.splitext(os.path.basename(input_filename))[0] +'_jpeg' +  os.path.splitext(os.path.basename(input_filename))[1]
        return os.path.join(dirname, output_filename)
    else:
        print 'Geotiff does not exist. Please double check the path entered.'
        sys.exit()


def compress_geotiff_to_jpeg(input_filename, create_overviews=False):
    """
        Function compresses and internally tiles the input geotiff. Optionally,
        overviews or pyramids will be generated if specified.

        Input:
        @input_filename: Full path to the input file (string)
        @overviews: Specifies if overviews are created (boolean) Default is False.
    """
    print 'Compressing and tiling geotiff...'
    output_filename = get_output_filename(input_filename)
    gdal_cmd_dict = _setup_gdal(config_filename)
    gdal_translate_exe = ' '.join([gdal_cmd_dict['gdal_translate'], input_filename, output_filename])
    subprocess.call(gdal_translate_exe)

    if create_overviews is True:
        print 'Overviews option found. Creating overviews...'
        gdaladdo_exe = ' '.join([gdal_cmd_dict['gdaladdo'], output_filename, '2 4 6 8 16'])
        subprocess.call(gdaladdo_exe)
    else:
        print 'Create overview option not found. Skip creating overviews.'

    if not type(create_overviews) is bool:
        if check_overviews_option(create_overviews):
            print 'Overviews option found. Creating overviews...'
            gdaladdo_exe = ' '.join([gdal_cmd_dict['gdaladdo'], output_filename, '2 4 6 8 16'])
            subprocess.call(gdaladdo_exe)
        else:
            print 'Create overview option invalid. Skip creating overviews.'


def check_overviews_option(option):
    """
        Checks to see if an overview option is specified.

        Input:
        @option: String to create overviews. Expect 'True' or 'true'. (string).

        Output:
        Option to create overviews. If 'True' or 'true' is found a Ture boolean
        is returned. 'False' will be returned for everything else (boolean).
    """
    if option.lower() == 'true':
        return True
    else:
        return False


def main():

    if sys.version[0:3] == '2.6':
        if len(sys.argv) < 2:
            print 'No GeoTiff specified. You must specify the full path to the geotiff.'
            sys.exit()

        if len(sys.argv) == 2:
            input_geotiff = sys.argv[1]
            compress_geotiff_to_jpeg(input_geotiff)

        if len(sys.argv) > 2:
            input_geotiff = sys.argv[1]
            overviews = sys.argv[2]
            compress_geotiff_to_jpeg(input_geotiff, overviews)

    if sys.version[0:3] == '2.7':
        import argparse
        parser = argparse.ArgumentParser(description='Compress Geotiff')
        parser.add_argument('-f', '--file', action='store', dest='input_geotiff',
                            required=True, help='Full path to Geotiff to compress.')
        parser.add_argument('-o', '--overviews', action='store_true', dest='overviews',
                            help='Add -o to create overviews.', default=False)
        args = parser.parse_args()
        compress_geotiff_to_jpeg(args.input_geotiff, args.overviews)

    print 'Geotiff compressed successfully.'


if __name__ == '__main__':
    sys.exit(main())