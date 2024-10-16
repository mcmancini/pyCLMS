# -*- coding: utf-8 -*-
# Copyright (c) 2023 LEEP, University of Exeter (UK)
# Mattia Mancini (m.c.mancini@exeter.ac.uk), September 2024
# =========================================================
"""
Utility functions
=================


Functions defined here:
-----------------------

lonlat2osgrid(coords, figs)
    converts a lon-lat pair to an OS grid code

osgrid2bbox(gridref, os_cellsize)
    Convert British National Grid references to OSGB36 numeric
    coordinates of the bounding box of the 1km, 10km grid or 100km grid
    squares.

vector2bbox(vector_file)
    Retrieves the coordinates of the bounding box of an input vector
    file. This can be a shapefile or a GeoJSON file.
"""

import re
import geopandas as gpd

from pyproj import Transformer


class BNGError(Exception):
    """Exception raised by OSgrid coordinate conversion functions"""


def _init_regions_and_offsets():
    # Region codes for 100 km grid squares.
    regions = [
        ["HL", "HM", "HN", "HO", "HP", "JL", "JM"],
        ["HQ", "HR", "HS", "HT", "HU", "JQ", "JR"],
        ["HV", "HW", "HX", "HY", "HZ", "JV", "JW"],
        ["NA", "NB", "NC", "ND", "NE", "OA", "OB"],
        ["NF", "NG", "NH", "NJ", "NK", "OF", "OG"],
        ["NL", "NM", "NN", "NO", "NP", "OL", "OM"],
        ["NQ", "NR", "NS", "NT", "NU", "OQ", "OR"],
        ["NV", "NW", "NX", "NY", "NZ", "OV", "OW"],
        ["SA", "SB", "SC", "SD", "SE", "TA", "TB"],
        ["SF", "SG", "SH", "SJ", "SK", "TF", "TG"],
        ["SL", "SM", "SN", "SO", "SP", "TL", "TM"],
        ["SQ", "SR", "SS", "ST", "SU", "TQ", "TR"],
        ["SV", "SW", "SX", "SY", "SZ", "TV", "TW"],
    ]

    # Transpose so that index corresponds to offset
    regions = list(zip(*regions[::-1]))

    # Create mapping to access offsets from region codes
    offset_map = {}
    for i, row in enumerate(regions):
        for j, region in enumerate(row):
            offset_map[region] = (1e5 * i, 1e5 * j)

    return regions, offset_map


_, _offset_map = _init_regions_and_offsets()


def osgrid2bbox(gridref, os_cellsize, epsg):
    """
    Convert British National Grid references to OSGB36 numeric coordinates
    of the bounding box of the 1km, 10km grid or 100km grid squares in a
    specified CRS.
    Grid references can be 2, 4, 6, 8 or 10 figures.

    :param gridref: str - BNG grid reference
    :param os_cellsize: str - '1km1, '10km' or '100km'
    :param epsg: int - EPSG code for the desired CRS

    :returns coords: dictionary {xmin, xmax, ymin, ymax}

    Examples:

    Single value
    >>> osgrid2bbox('NT2755062950', '10km', 27700)
    {'xmin': 320000, 'xmax': 330000, 'ymin': 660000, 'ymax': 670000}
    >>> osgrid2bbox('NT2755062950', '100km', 27700)
    {'xmin': 300000, 'xmax':400000, 'ymin': 600000, 'ymax': 700000}
    >>> osgrid2bbox('NT2755062950', '1km', 27700)
    {'xmin': 327000, 'xmax':328000, 'ymin': 662000, 'ymax': 663000}

    For multiple values, use Python's zip function and list comprehension
    >>> gridrefs = ['HU431392', 'SJ637560', 'TV374354']
    >>> [osgrid2bbox(g, '10km') for g in gridrefs]
    >>> [{'xmin': 440000, 'xmax': 450000, 'ymin': 1130000, 'ymax': 1140000},
        {'xmin': 360000, 'xmax': 370000, 'ymin': 330000, 'ymax': 340000},
        {'xmin': 530000, 'xmax': 540000, 'ymin': 70000, 'ymax': 80000}]
    """
    # Validate input
    bad_input_message = (
        f"Valid gridref inputs are 2 characters and none, "
        f"2, 4, 6, 8 or 10-fig references as strings "
        f'e.g. "NN123321", or lists/tuples/arrays of strings. '
        f"[{gridref}]"
    )

    gridref = gridref.upper()
    if os_cellsize in ["1km", "10km"]:
        try:
            pattern = r"^([A-Z]{2})(\d{2}|\d{4}|\d{6}|\d{8}|\d{10})$"
            match = re.match(pattern, gridref)
            # Extract data from gridref
            region, coords = match.groups()
        except (TypeError, AttributeError) as exc:
            # Non-string values will throw error
            raise BNGError(bad_input_message) from exc
    elif os_cellsize == "100km":
        try:
            pattern = r"^([A-Z]{2})"
            match = re.match(pattern, gridref)
            # Extract data from gridref
            region = match.groups()[0]
        except (TypeError, AttributeError) as exc:
            raise BNGError(bad_input_message) from exc
    else:
        raise BNGError(
            "Invalid argument 'os_cellsize' supplied: "
            "values can only be '10km' or '100km'"
        )

    # Get offset from region
    try:
        _offset_map[region]
    except KeyError as exc:
        raise BNGError(f"Invalid grid square code: {region}") from exc

    rescaling = {
        "1km": {"coord_len": 2, "scale_factor": 1e3},
        "10km": {"coord_len": 1, "scale_factor": 1e4},
    }

    if os_cellsize == "100km":
        x_min = int(_offset_map[region][0])
        y_min = int(_offset_map[region][1])
        x_max = int(_offset_map[region][0] + 1e5)
        y_max = int(_offset_map[region][1] + 1e5)
    elif os_cellsize in ["1km", "10km"]:
        coord_len = rescaling[os_cellsize]["coord_len"]
        scale_factor = rescaling[os_cellsize]["scale_factor"]
        easting = int(coords[0:coord_len])
        northing = int(
            coords[int(len(coords) / 2) : int(len(coords) / 2) + coord_len]
        )
        x_min = int(easting * scale_factor + _offset_map[region][0])
        y_min = int(northing * scale_factor + _offset_map[region][1])
        x_max = int(easting * scale_factor + _offset_map[region][0] + 1e4)
        y_max = int(northing * scale_factor + _offset_map[region][1] + 1e4)
    else:
        raise BNGError(
            "Invalid argument 'os_cellsize' "
            "supplied: values can only be '10km' or '100km'"
        )

    bbox_27700 = {"xmin": x_min, "xmax": x_max, "ymin": y_min, "ymax": y_max}

    transformer = Transformer.from_crs(27700, epsg, always_xy=True)
    # pylint: disable=E0633
    min_lon, min_lat = transformer.transform(
        bbox_27700["xmin"], bbox_27700["ymin"]
    )
    max_lon, max_lat = transformer.transform(
        bbox_27700["xmax"], bbox_27700["ymax"]
    )
    # pylint: enable=E0633
    bbox = {
        "x_min": min_lon,
        "x_max": max_lon,
        "y_min": min_lat,
        "y_max": max_lat,
    }
    return bbox


def vector2bbox(vector_file):
    """
    Retrieves the coordinates of the bounding box of an input vector
    file. This can be a variety of spatial vector files such as
    shapefiles, geoJSON, KML, GPKG, GML DXF, etc.
    """
    gdf = gpd.read_file(vector_file)
    bbox = gdf.total_bounds
    return {
        "x_min": float(bbox[0]),
        "x_max": float(bbox[2]),
        "y_min": float(bbox[1]),
        "y_max": float(bbox[3]),
    }
