# STL Process Vacant Parcels

## Installation

1. Install Python 2.x
2. [Install pip](https://pip.pypa.io/en/stable/installing/)
3. `pip install pyshp`
4. `pip install requests`

## Run

1. Open terminal, type `python main.py`

## Notes

Arcade

```
var both = $feature["VL_Final"] == 2 && $feature["VB_Final"] == 2;
var VLOnly = $feature["VL_Final"] == 2 && $feature["VB_Final"] == 2;
var VBOnly = $feature["VL_Final"] == 1 && $feature["VB_Final"] == 2;
var neither = $feature["VL_Final"] == 1 && $feature["VB_Final"] == 1;

IIF(both, "RED", IIF(VLOnly, "ORANGE", IIF(VBOnly, "PURPLE", "GRAY")))
// if(both) {
//     return "RED";
// } else if (VLOnly) {
//     return "ORANGE";
// } else if (VBOnly) {
//     return "PURPLE";
// } else {
//     return "GRAY";
// }
```
