import shapefile
import urllib
import os
import shutil
import zipfile
import logging
import utils
import csv

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger("main")

## CONSTANTS
TEMP_FOLDER_NAME = "tmp"
VACANT_PROPERTY_CSV_URL = "https://www.stlvacancy.com/uploads/8/7/1/3/87139164/finalvacantall_20180707.csv"
VACANT_PROPERTY_CSV_FILENAME = "VACANT_PROPERTY_CSV.csv"
STL_PARCEL_SHAPEFILE_URL = "https://www.stlouis-mo.gov/data/upload/data-files/prcl_shape.zip"
STL_PARCEL_SHAPEFILE_FILENAME = "PARCEL_SHAPE.zip"
SHAPEFILE_NAME = "prcl"
SHAPEFILE_PATH_ORIGINAL = os.path.join(TEMP_FOLDER_NAME, SHAPEFILE_NAME, "original")
SHAPEFILE_PATH_MODIFIED = os.path.join(TEMP_FOLDER_NAME, SHAPEFILE_NAME, "modified")

## DOWNLOAD THE FILES
log.info("Downloading files ...")
if os.path.exists(TEMP_FOLDER_NAME) and os.path.isdir(TEMP_FOLDER_NAME):
  shutil.rmtree(TEMP_FOLDER_NAME)
os.mkdir(TEMP_FOLDER_NAME)
urllib.urlretrieve(VACANT_PROPERTY_CSV_URL, os.path.join(TEMP_FOLDER_NAME, VACANT_PROPERTY_CSV_FILENAME))
urllib.urlretrieve(STL_PARCEL_SHAPEFILE_URL, os.path.join(TEMP_FOLDER_NAME, STL_PARCEL_SHAPEFILE_FILENAME))

## Unzip the shapefile
log.info("Unzipping shapefile ...")

utils.mkdir_p(SHAPEFILE_PATH_ORIGINAL)
with zipfile.ZipFile(os.path.join(TEMP_FOLDER_NAME, STL_PARCEL_SHAPEFILE_FILENAME), 'r') as zip_ref:
    zip_ref.extractall(SHAPEFILE_PATH_ORIGINAL)





sf = shapefile.Reader(os.path.join(SHAPEFILE_PATH_ORIGINAL, SHAPEFILE_NAME))

if sf.shapeType != shapefile.POLYGON:
  log.error("NOT A POLYGON")

log.info("Number of features in shapefile: {0}".format(len(sf)))

fields = [field[0] for field in sf.fields[1:]]
log.info(fields)

# records = sf.shapeRecords()
# for feature in records[:10]:
#     geom = feature.shape.__geo_interface__
#     atr = dict(zip(fields, feature.record))
#     print geom, atr


## READ THE CSV
with open(os.path.join(TEMP_FOLDER_NAME, VACANT_PROPERTY_CSV_FILENAME), 'rb') as csvfile:
  reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
  csvData = list(reader)

  ## WRITE THE SHAPEFILE
  utils.mkdir_p(SHAPEFILE_PATH_MODIFIED)
  # TODO - COPY PRJ FILE FROM EXISTING SHAPEFILE SINCE PYSHP DOES NOT HAVE THIS FUNCTIONALITY (https://github.com/GeospatialPython/pyshp/issues/158)
  shutil.copyfile("{0}.prj".format(os.path.join(SHAPEFILE_PATH_ORIGINAL, SHAPEFILE_NAME)), "{0}.prj".format(os.path.join(SHAPEFILE_PATH_MODIFIED, SHAPEFILE_NAME)))
  w = shapefile.Writer(os.path.join(SHAPEFILE_PATH_MODIFIED, SHAPEFILE_NAME), shapeType=sf.shapeType)
  w.fields = sf.fields
  for key in csvData[0].keys():
    w.field(key, 'C')
  # TODO - add all fields from CSV
  # TODO - join data
  log.info(w.fields)

  records = sf.shapeRecords()
  # IMPORTANT - when doing full file use iterShapeRecords
  for feature in records[:40]:
      geom = feature.shape.__geo_interface__
      atr = dict(zip(fields, feature.record))
      # w.null()
      w.shape(geom)

      print "working on --- {0}".format(atr['HANDLE'])
      
      for row in csvData:
        # print "row.handle: {0}".format(row['HANDLE'])
        # print "atr.handle: {0}".format(atr['HANDLE'])
        if(int(row['HANDLE']) == int(atr['HANDLE'])):
          # we found the item in the csv - bail
          print "FOUND ROW:"
          item = row
          print item
          w.record(**item)
          break

  w.close()

# shutil.rmtree(TEMP_FOLDER_NAME)