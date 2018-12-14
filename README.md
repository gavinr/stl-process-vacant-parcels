# STL Vacant Parcels

This script is used to merge the CSV of Vacant Parcels generated from the [STL Vacancy Project](https://www.stlvacancy.com/methods.html) and the official [City of St. Louis Parcels Shapefile](https://www.stlouis-mo.gov/data/parcels.cfm) to enable mapping and visualization fo the data.

## The Map

[![screenshot](https://i.imgur.com/4Ehkqb8.png)](http://arcgis.com/apps/webappviewer/index.html?id=45e326c1532e4e87a3c2cdbea911dc7a)

## The Script

### Installation

1. Install Python 2.x
2. [Install pip](https://pip.pypa.io/en/stable/installing/)
3. `pip install pyshp`
4. `pip install requests`

### Run

1. Open terminal, type `python main.py`

This will download the required data, generate the Shapefile, and save that Shapefile out to `tmp/prcl/modified`. You can then use this file in geospatial software like ArcGIS Pro or zip it up and upload it to a geospatial platform like ArcGIS Online.

### Notes

Arcade Expression used in the ArcGIS Web Map:

```
if($feature.VB_Final == 2) {
    return "Vacant Building - Certain";
} else if($feature.VB_Final == 1) {
    return "Vacant Building - Probable";
} else if($feature.VL_Final == 2) {
    return "Vacant Lot - Certain";
} else if($feature.VL_Final == 1) {
    return "Vacant Lot - Probable";
} else {
    return "Other";
}
```

