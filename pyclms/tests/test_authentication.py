# -*- coding: utf-8 -*-
# Copyright (c) 2023 LEEP - University of Exeter (UK)
# Mattia C. Mancini (m.c.mancini@exeter.ac.uk), October 2024
"""
Tests for the procedures to authenticate users to the WEkEO HDA client.
"""

import os
from unittest import mock

import pytest

from pyclms.core.authenticator import AuthenticationError, ClientBuilder


class Configuration:
    """
    Mock the Configuration class from the WEkEO HDA client.
    """

    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password


def test_auth_success():
    """
    Test that the ClientBuilder class is correctly initialised with
    the user's username and password.
    """
    with mock.patch("hda.Configuration", Configuration), mock.patch(
        "hda.Client.__init__", return_value=None
    ) as mock_client_init, mock.patch(
        "hda.Client.token", new_callable=mock.PropertyMock
    ) as mock_token:

        mock_token.return_value = "mocked_token"
        client = ClientBuilder(user="test_user", password="test_password")
        mock_client_init.assert_called_once_with(config=mock.ANY)
        assert client.token == "mocked_token"


def test_auth_failure():
    """
    Test for authentication failure of the ClientBuilder class.
    """
    with mock.patch("hda.Configuration", Configuration), mock.patch(
        "hda.Client.__init__", return_value=None
    ), mock.patch(
        "hda.Client.token", new_callable=mock.PropertyMock
    ) as mock_token:
        mock_token.side_effect = Exception("Authentication failed")
        with pytest.raises(AuthenticationError):
            _ = ClientBuilder(user="test_user", password="test_password")


def test_env_var_setup():
    """
    Test that the ClientBuilder class sets and uses the environment
    variables correctly from user input.
    """
    with mock.patch("hda.Configuration", Configuration), mock.patch(
        "hda.Client.__init__", return_value=None
    ), mock.patch("builtins.input", return_value="mocked_user"), mock.patch(
        "getpass.getpass", return_value="mocked_password"
    ), mock.patch(
        "hda.Client.token", new_callable=mock.PropertyMock
    ) as mock_token, mock.patch(
        "os.getenv"
    ) as mock_getenv:
        mock_getenv.side_effect = lambda x: {
            "HDA_USER": "mocked_user",
            "HDA_PASSWORD": "mocked_password",
        }.get(x, None)
        mock_token.return_value = "mocked_token"
        client = ClientBuilder()
        assert os.getenv("HDA_USER") == "mocked_user"
        assert os.getenv("HDA_PASSWORD") == "mocked_password"
        assert client.token == "mocked_token"
