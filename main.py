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


## READ THE CSV
with open(os.path.join(TEMP_FOLDER_NAME, VACANT_PROPERTY_CSV_FILENAME), 'rb') as csvfile:
  reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
  csvData = list(reader)
  csvDict = {int(item['HANDLE']): item for item in csvData}

  # BlankRow for items where there is no match in the CSV:
  blankRow = csvData[0].copy()
  for key in blankRow:
    blankRow[key] = None

  ## WRITE THE SHAPEFILE
  utils.mkdir_p(SHAPEFILE_PATH_MODIFIED)
  # COPY PRJ FILE FROM EXISTING SHAPEFILE SINCE PYSHP DOES NOT HAVE THIS FUNCTIONALITY (https://github.com/GeospatialPython/pyshp/issues/158)
  shutil.copyfile("{0}.prj".format(os.path.join(SHAPEFILE_PATH_ORIGINAL, SHAPEFILE_NAME)), "{0}.prj".format(os.path.join(SHAPEFILE_PATH_MODIFIED, SHAPEFILE_NAME)))
  w = shapefile.Writer(os.path.join(SHAPEFILE_PATH_MODIFIED, SHAPEFILE_NAME), shapeType=sf.shapeType)
  # w.fields = sf.fields

  # add all fields from CSV:
  # for key in csvData[0].keys():
  #   w.field(key, 'C')
  
  # Only Expose some of the fields from the CSV for now:
  #  HANDLE, VB_Final, and VL_Final: (for field types see https://github.com/GeospatialPython/pyshp#reading-records)
  w.field('HANDLE', 'N', 15)
  w.field('SITEADDR', 'C', 50)
  w.field('OwnerCat', 'C', 7)
  w.field('Owner', 'C', 50)
  w.field('NHD_NAME', 'C', 50)
  w.field('VB_Final', 'N', 1)
  w.field('VL_Final', 'N', 1)
  w.field('Acres', 'N', 5, 5)

  # JOIN DATA FROM CSV ONTO SHAPEFILE:
  records = sf.shapeRecords()
  # IMPORTANT - when doing full file use iterShapeRecords
  # for feature in sf.iterShapeRecords():
  log.info("records: {0}".format(len(records)))
  for i, feature in enumerate(records):
    geom = feature.shape.__geo_interface__
    atr = dict(zip(fields, feature.record))

    
    if(int(atr['HANDLE']) in csvDict):
      item = csvDict[int(atr['HANDLE'])]
      log.info("{0}% complete.".format(str(round((float(i)/len(records)) * 100, 2))))
      w.shape(geom)
      # w.record(**item) # This adds ALL the columns of the csv to the shapefile
      w.record(HANDLE=item['HANDLE'],SITEADDR=item['SITEADDR'],OwnerCat=item['OwnerCat'],Owner=item['Owner'],NHD_NAME=item['NHD_NAME'],VB_Final=item['VB_Final'],VL_Final=item['VL_Final'],Acres=item['Acres'])

    # else:
    #   w.shape(geom)
    #   w.record(**blankRow)

  w.close()