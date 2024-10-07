# -*- coding: utf-8 -*-
# Copyright (c) 2023 LEEP - University of Exeter (UK)
# Mattia C. Mancini (m.c.mancini@exeter.ac.uk), October 2024
"""
Procedures to deal with the authentication of users to the
WEkEO HDA client.
"""

import getpass
import os

from hda import Client


class AuthenticationError(Exception):
    """
    An exception to raise when there is an error in the authentication.
    """

    _MESSAGE = (
        "Authentication failed. Please check "
        "the username and password entered."
    )

    def __init__(self):
        self.message = self._MESSAGE
        super().__init__(self.message)


class ClientBuilder(Client):
    """
    A class to build the configuration file for the WEkEO HDA client.
    This works as follows:

    """

    _USERPATH = os.path.expanduser("~")
    _CONFIGFILE = os.path.join(_USERPATH, ".hdarc")
    _URL = "https://wekeo-broker.apps.mercator.dpi.wekeo.eu/databroker"

    def __init__(self, user: str = None, password: str = None):
        self._build_config(user=user, password=password)
        super().__init__()

    def _build_config(self, user: str = None, password: str = None) -> Client:
        """
        Build the configuration file for the WEkEO HDA client.
        """
        configfile = self._CONFIGFILE
        if user is None and password is None:
            if not os.path.isfile(configfile):
                user = input("Enter your username: ")
                password = getpass.getpass("Enter your password: ")
                config = [
                    f"url: {self._URL}",
                    f"user: {user}",
                    f"password: {password}",
                ]
                with open(configfile, "w", encoding="utf-8") as fp:
                    fp.write("\n".join(config))
        if user is not None and password is not None:
            config = [
                f"url: {self._URL}",
                f"user: {user}",
                f"password: {password}",
            ]
            with open(configfile, "w", encoding="utf-8") as fp:
                fp.write("\n".join(config))

        client = self._validate_client(
            client=Client(), configfile=self._CONFIGFILE
        )
        return client

    @staticmethod
    def _validate_client(client: Client, configfile) -> Client:
        """
        Validate the client.
        """
        try:
            _ = client.token
            return client
        except Exception as e:
            if os.path.exists(configfile):
                os.remove(configfile)
            raise AuthenticationError() from e
