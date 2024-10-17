# -*- coding: utf-8 -*-
# Copyright (c) 2023 LEEP - University of Exeter (UK)
# Mattia C. Mancini (m.c.mancini@exeter.ac.uk), October 2024
"""
Testing of procedures for the utility functions
"""
import os

import pytest

from pyclms.core.utils import BNGError, osgrid2bbox, vector2bbox


def test_osgrid2bbox_10km_27700():
    """
    Test the conversion of an OS grid reference to a bounding
    box for a 10km grid square and EPSG:27700
    """
    bbox = osgrid2bbox("NT2755062950", "10km", 27700)
    expected = {
        "x_min": 320000,
        "x_max": 330000,
        "y_min": 660000,
        "y_max": 670000,
    }
    assert bbox["x_min"] == pytest.approx(expected["x_min"], rel=1e7)
    assert bbox["x_max"] == pytest.approx(expected["x_max"], rel=1e7)
    assert bbox["y_min"] == pytest.approx(expected["y_min"], rel=1e7)
    assert bbox["y_max"] == pytest.approx(expected["y_max"], rel=1e7)


def test_osgrid2bbox_10km_4326():
    """
    Test the conversion of an OS grid reference to a bounding
    box for a 10km grid square and EPSG:4326
    """
    bbox = osgrid2bbox("NT2755062950", "10km", 4326)
    expected = {
        "x_min": -3.2785726153830983,
        "x_max": -3.1215711005875786,
        "y_min": 55.826586088175084,
        "y_max": 55.91797307559743,
    }
    assert bbox["x_min"] == pytest.approx(expected["x_min"], rel=1e7)
    assert bbox["x_max"] == pytest.approx(expected["x_max"], rel=1e7)
    assert bbox["y_min"] == pytest.approx(expected["y_min"], rel=1e7)
    assert bbox["y_max"] == pytest.approx(expected["y_max"], rel=1e7)


def test_osgrid2bbox_100km_27700():
    """
    Test the conversion of an OS grid reference to a bounding
    box for a 100km grid square and EPSG:27700
    """
    bbox = osgrid2bbox("NT2755062950", "100km", 27700)
    expected = {
        "x_min": 300000,
        "x_max": 400000,
        "y_min": 600000,
        "y_max": 700000,
    }
    assert bbox["x_min"] == pytest.approx(expected["x_min"], rel=1e7)
    assert bbox["x_max"] == pytest.approx(expected["x_max"], rel=1e7)
    assert bbox["y_min"] == pytest.approx(expected["y_min"], rel=1e7)
    assert bbox["y_max"] == pytest.approx(expected["y_max"], rel=1e7)


def test_osgrid2bbox_100km_4326():
    """
    Test the conversion of an OS grid reference to a bounding
    box for a 100km grid square and EPSG:4326
    """
    bbox = osgrid2bbox("NT2755062950", "100km", 4326)
    expected = {
        "x_min": -3.575974937233206,
        "x_max": -2.001588131316519,
        "y_min": 55.28394104991955,
        "y_max": 56.192619048829656,
    }
    assert bbox["x_min"] == pytest.approx(expected["x_min"], rel=1e7)
    assert bbox["x_max"] == pytest.approx(expected["x_max"], rel=1e7)
    assert bbox["y_min"] == pytest.approx(expected["y_min"], rel=1e7)
    assert bbox["y_max"] == pytest.approx(expected["y_max"], rel=1e7)


def test_osgrid2bbox_1km_27700():
    """
    Test the conversion of an OS grid reference to a bounding
    box for a 100km grid square and EPSG:27700
    """
    bbox = osgrid2bbox("NT2755062950", "1km", 27700)
    expected = {
        "x_min": 327000,
        "x_max": 337000,
        "y_min": 662000,
        "y_max": 672000,
    }
    assert bbox["x_min"] == pytest.approx(expected["x_min"], rel=1e7)
    assert bbox["x_max"] == pytest.approx(expected["x_max"], rel=1e7)
    assert bbox["y_min"] == pytest.approx(expected["y_min"], rel=1e7)
    assert bbox["y_max"] == pytest.approx(expected["y_max"], rel=1e7)


def test_osgrid2bbox_1km_4326():
    """
    Test the conversion of an OS grid reference to a bounding
    box for a 100km grid square and EPSG:4326
    """
    bbox = osgrid2bbox("NT2755062950", "1km", 4326)
    expected = {
        "x_min": -3.1674005539013135,
        "x_max": -3.010059521476741,
        "y_min": 55.84566280459672,
        "y_max": 55.93690881266649,
    }
    assert bbox["x_min"] == pytest.approx(expected["x_min"], rel=1e7)
    assert bbox["x_max"] == pytest.approx(expected["x_max"], rel=1e7)
    assert bbox["y_min"] == pytest.approx(expected["y_min"], rel=1e7)
    assert bbox["y_max"] == pytest.approx(expected["y_max"], rel=1e7)


def test_osgrid2bbox_invalid_gridref():
    """Test for invalid grid reference input."""
    with pytest.raises(BNGError):
        osgrid2bbox("INVALID", "10km", 27700)


def test_osgrid2bbox_invalid_cellsize():
    """Test for invalid cell size input."""
    with pytest.raises(BNGError):
        osgrid2bbox("NT2755072950", "20km", 27700)


def assert_bbox_close(bbox1, bbox2, tolerance=1e-7):
    """Helper function to assert that two bounding boxes are close."""
    assert pytest.approx(bbox1["x_min"], bbox2["x_min"], rel_tol=tolerance)
    assert pytest.approx(bbox1["x_max"], bbox2["x_max"], rel_tol=tolerance)
    assert pytest.approx(bbox1["y_min"], bbox2["y_min"], rel_tol=tolerance)
    assert pytest.approx(bbox1["y_max"], bbox2["y_max"], rel_tol=tolerance)


def test_vector2bbox():
    """Test for vector2bbox function with different formats."""
    shp_file = ".tests/data/parcel.shp"
    geojson_file = ".tests/data/parcel.geojson"
    expected_bbox = {
        "x_min": -3.177028636693752,
        "x_max": -3.171157972148295,
        "y_min": 50.702596375442674,
        "y_max": 50.706616337507135,
    }
    if os.path.exists(shp_file):
        bbox_shp = vector2bbox(shp_file)
        assert_bbox_close(bbox_shp, expected_bbox)
    if os.path.exists(geojson_file):
        bbox_geojson = vector2bbox(geojson_file)
        assert_bbox_close(bbox_geojson, expected_bbox)
