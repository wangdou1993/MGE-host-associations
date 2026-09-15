# MGE-host-associations

Scripts for data processing and figure generation to reproduce the results of the manuscript focused on mobile genetic elements and their hosts.

## Dependencies
### Python
pandas  
os  
csv  
glob  

### R
library(vegan)  
library(ggplot2)  

## Script Descriptions and Quick Run

### `Summary_ARG_host.py`

Summarizes ARG host abundance at different taxonomic levels.

**Usage:**
```bash
python summary_ARG_host.py
```

**Input directory:**
- `0-ARG-host-info`

**Output directories:**
- `1-amr-host-summary`
- `2-combine-all-sample-taxa`
- `3-summarize-di-taxa`


