# COINS - Continuity in Street Networks
This repository contains the source code of the COINS tool that allows to deduce natural continuity of street network. For continuity of streets, the deflection angle between adjacent segments are computed, the user can provide the desired angle threshold. Segments will only be considered a part of the same street if the deflection angle is above the threshold (defaults to zero). Please find details in the paper.<br/>

The image below shows the input street network data from the OSM, and its corresponding output from the COINS tool. For visualisation purpose, classification (natural breaks 'Jenks') was done on the length of the street strokes in the resulting shapefile.<br/>
<img src="Images/Input.png" height="250" width="250">
<img src="Images/Output.png" height="250" width="250">

There are three ways of accessing the tool, the first and fastest one is through Python's momepy package, find details here [[link]](https://docs.momepy.org/en/latest/api/momepy.COINS.html). Second way is the Python script version, which can be found here [[link]](/PythonTool). Third way of accessing is the QGIS plugin, source code and details are here [[link]](/QGISplugin).<br/>

**Suggested citation**<br/>
Tripathy, P., Rao, P., Balakrishnan, K., & Malladi, T. (2021). An open-source tool to extract natural continuity and hierarchy of urban street networks. _Environment and Planning B: Urban Analytics and City Science_, 48(8), 2188-2205. [http://dx.doi.org/10.1177/2399808320967680](http://dx.doi.org/10.1177/2399808320967680)<br/>

**Bibtext entry:**
```tex
@article{tripathy2021,
  title={An open-source tool to extract natural continuity and hierarchy of urban street networks},
  author={Tripathy, Pratyush and Rao, Pooja and Balakrishnan, Krishnachandran and Malladi, Teja},
  journal={Environment and Planning B: Urban Analytics and City Science},
  volume = {48},
  number = {8},
  pages = {2188-2205},
  year = {2021},
  doi={10.1177/2399808320967680},
  URL = {https://doi.org/10.1177/2399808320967680}
}
```

**Affiliation**<br/>
Geospatial Lab, Indian Institute for Human Settlements, Bengaluru - 560080, India<br/>

**Funding**<br/>
This work was completed with support from the PEAK Urban programme, funded by UKRI’s Global Challenge Research Fund, Grant Ref: ES/P011055/1

**Updates after the paper (12 September 2021)**<br/>
COINS has been integrated into the [momepy Python package](http://docs.momepy.org/en/latest/generated/momepy.COINS.html). Leveraging efficiency of Geopandas, COINS has become much more faster than the version reported in the paper. The back-end algorithm remains the same as described in the paper.
