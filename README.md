# MGE-host-associations

Scripts for data processing and figure generation to reproduce the results of the manuscript focused on mobile genetic elements and their hosts.

## Dependencies
### Python/Python3
openpyxl (python3 -m pip install openpyxl)
pandas  
os  
csv  
glob  

### R
library(vegan)  
library(ggplot2)  

### `multiple-column-stats.py`




### `multiple-column-stats.py`
Summarizes ARG profiles by category.

**Usage:**
```bash
python3 multiple-column-stats.py
Please enter the folder path containing data files: ARG-identification
Please enter output folder path (press Enter to use default '/MultiColumn_Stats'): 
Please enter column names to analyze (comma-separated) (press Enter to use default 'Type,location,rank'):
```
**Input directory:**
- `ARG-identification`

**Output directories:**
- `MultiColumn_Stats/location_Stats`
- `MultiColumn_Stats/rank_Stats`
- `MultiColumn_Stats/Type_Stats`


## Script Descriptions and Quick Run

### `Summary_ARG_host.py`

Summarizes ARG host abundance at different taxonomic levels.

**Usage:**
```bash
python3 summary_ARG_host.py
```

**Input directory:**
- `0-ARG-host-info`

**Output directories:**
- `1-amr-host-summary`
- `2-combine-all-sample-taxa`
- `3-summarize-di-taxa`




 


