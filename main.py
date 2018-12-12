import shapefile
import urllib
import os
import shutil
import zipfile
import logging

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger("main")

## CONSTANTS
TEMP_FOLDER_NAME = "tmp"
VACANT_PROPERTY_CSV_URL = "https://www.stlvacancy.com/uploads/8/7/1/3/87139164/finalvacantall_20180707.csv"
VACANT_PROPERTY_CSV_FILENAME = "VACANT_PROPERTY_CSV.csv"
STL_PARCEL_SHAPEFILE_URL = "https://www.stlouis-mo.gov/data/upload/data-files/prcl_shape.zip"
STL_PARCEL_SHAPEFILE_FILENAME = "PARCEL_SHAPE.zip"
SHAPEFILE_NAME = "prcl"

## DOWNLOAD THE FILES
log.info("Downloading files ...")
os.mkdir(TEMP_FOLDER_NAME)
urllib.urlretrieve(VACANT_PROPERTY_CSV_URL, os.path.join(TEMP_FOLDER_NAME, VACANT_PROPERTY_CSV_FILENAME))
urllib.urlretrieve(STL_PARCEL_SHAPEFILE_URL, os.path.join(TEMP_FOLDER_NAME, STL_PARCEL_SHAPEFILE_FILENAME))

## Unzip the shapefile
log.info("Unzipping shapefile ...")
with zipfile.ZipFile(os.path.join(TEMP_FOLDER_NAME, STL_PARCEL_SHAPEFILE_FILENAME), 'r') as zip_ref:
    zip_ref.extractall(TEMP_FOLDER_NAME)

sf = shapefile.Reader(os.path.join(TEMP_FOLDER_NAME, SHAPEFILE_NAME))

if sf.shapeType != shapefile.POLYGON:
  log.error("NOT A POLYGON")

log.info("Number of features in shapefile: {0}".format(len(sf)))
log.info(sf.fields)

w = shapefile.Writer(os.path.join(TEMP_FOLDER_NAME, SHAPEFILE_NAME))
w.fields = sf.fields
w.field('TEXT', 'C')
# TODO - add all fields from CSV
# TODO - join data
log.info(w.fields)
w.close()

# shutil.rmtree(TEMP_FOLDER_NAME)