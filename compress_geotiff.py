#-------------------------------------------------------------------------------
# Name:        compress_geotiff.py
# Version:     1.04
#
# Purpose:     This script uses gdal_translate to compress a geotiff using JPEG
#              compression.
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
import argparse

config_filename =  r'config.ini'


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
    config_file = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), config_file)
    parser = ConfigParser.SafeConfigParser()
    parser.read(config_file)

    os.environ['PATH'] = ';'.join([parser.get('gdal_paths', 'bin_path'), parser.get('gdal_paths', 'exe_path')]) + ';' + os.environ['PATH']
    os.environ["GDAL_DATA"] = parser.get('gdal_paths', 'data_path')

    return {'gdalwarp': ' '.join([os.path.join(parser.get('gdal_paths', 'exe_path'), 'gdalwarp.exe'), r'-of VRT -srcnodata 0 -dstnodata none -dstalpha -co TILED=YES']),
            'gdal_translate_vrt': ' '.join([os.path.join(parser.get('gdal_paths', 'exe_path'), 'gdal_translate.exe'), r'-of VRT -b 1 -b 2 -b 3 -mask 4 -co ALPHA=YES -co photometric=RGB -co INTERLEAVE=PIXEL -co TILED=YES --config GDAL_TIFF_INTERNAL_MASK YES']),
            'gdal_translate': ' '.join([os.path.join(parser.get('gdal_paths', 'exe_path'), 'gdal_translate.exe'), r'-co ALPHA=YES -co COMPRESS=JPEG -co PHOTOMETRIC=YCBCR -co TILED=YES --config GDAL_TIFF_INTERNAL_MASK YES']),
            'gdaladdo':  ' '.join([os.path.join(parser.get('gdal_paths', 'exe_path'), 'gdaladdo.exe'), r'--config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r AVERAGE'])
           }


def _get_vrt_filename(input_filename, vrt_filename):
    """
        *** Function is meant for internal use***

        Function returns an anutomatically generated temporary filename for
        VRT files.

        Input:
        @input_filename: Full path to the input file. Used to get the working
        directory. (string)
        @vrt_filename: Name of VRT

        Output:
        Full path to the output VRT file (string).
    """
    if os.path.isfile(input_filename):
        dirname = os.path.dirname(input_filename)
        output_filename = '.'.join([vrt_filename, 'vrt'])
        return os.path.join(dirname, output_filename)


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
        print 'GeoTiff does not exist. Please double check the path entered.'
        sys.exit()


def compress_geotiff_to_jpeg(input_filename, create_overviews=False):
    """
        Function compresses and internally tiles the input geotiff. Optionally,
        overviews or pyramids will be generated if specified.

        Input:
        @input_filename: Full path to the input file (string)
        @overviews: Specifies if overviews are created (boolean) Default is False.
    """
    try:
        print 'Compressing and tiling GeoTiff...'
        output_filename = get_output_filename(input_filename)
        gdal_cmd_dict = _setup_gdal(config_filename)
        alpha_vrt = _get_vrt_filename(input_filename, 'alpha')
        mask_vrt = _get_vrt_filename(input_filename, 'mask')
        gdalwarp_exe = ' '.join([gdal_cmd_dict['gdalwarp'], input_filename, alpha_vrt])
        subprocess.call(gdalwarp_exe)
        gdal_translate_vrt_exe = ' '.join([gdal_cmd_dict['gdal_translate_vrt'], alpha_vrt, mask_vrt])
        subprocess.call(gdal_translate_vrt_exe)
        gdal_translate_exe = ' '.join([gdal_cmd_dict['gdal_translate'], mask_vrt, output_filename])
        subprocess.call(gdal_translate_exe)

        if create_overviews is True:
            print 'Overviews option found. Creating overviews...'
            gdaladdo_exe = ' '.join([gdal_cmd_dict['gdaladdo'], output_filename, '2 4 6 8 16'])
            subprocess.call(gdaladdo_exe)
        else:
            print 'Create overview option not found.'

    except Exception as e:
        print 'Error: {0}'.format(str(e))

    finally:
        print 'Cleaning up temporary files...'
        os.remove(alpha_vrt)
        os.remove(mask_vrt)
        print 'Done.'


def main():
    parser = argparse.ArgumentParser(description='Compress GeoTiff')
    parser.add_argument('-f', '--file', action='store', dest='input_geotiff',
                        required=True, help='Full path to Geotiff to compress.')
    parser.add_argument('-o', '--overviews', action='store_true', dest='overviews',
                        help='Add -o to create overviews.', default=False)
    args = parser.parse_args()
    compress_geotiff_to_jpeg(args.input_geotiff, args.overviews)


if __name__ == '__main__':
    sys.exit(main())