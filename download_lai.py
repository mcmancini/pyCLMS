# -*- coding: utf-8 -*-
# Copyright (c) 2023 LEEP - University of Exeter (UK)
# Mattia C. Mancini (m.c.mancini@exeter.ac.uk), October 2024
"""
Procedures to download LAI data from the WEkEO HDA client.
"""

from pyclms.core.authenticator import ClientBuilder
from pyclms.core.utils import osgrid2bbox

client = ClientBuilder()

DATASET = "EO:EEA:DAT:CLMS_HRVPP_VI"
OSCODE = "NT2755072950"
bbox = osgrid2bbox(gridref=OSCODE, os_cellsize="10km", epsg=4326)
query = {
    "dataset_id": DATASET,
    "productType": "QFLAG2",
    "itemsPerPage": 200,
    "startIndex": 0,
    "start": "2020-01-01T00:00:00.000Z",
    "end": "2020-01-31T00:00:00.000Z",
    "bbox": [
        bbox["x_min"],
        bbox["y_min"],
        bbox["x_max"],
        bbox["y_max"],
    ]
}

matches = client.search(query)
print(matches)
