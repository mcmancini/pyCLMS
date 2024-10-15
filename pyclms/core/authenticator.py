# -*- coding: utf-8 -*-
# Copyright (c) 2023 LEEP - University of Exeter (UK)
# Mattia C. Mancini (m.c.mancini@exeter.ac.uk), October 2024
"""
Procedures to deal with the authentication of users to the
WEkEO HDA client.
"""

import getpass
import os

from hda import Client, Configuration


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
    Initialising an instance of this class will prompt the user to
    enter their username and password and store them as environment
    variables, unless username and password are passed as arguments.
    These will be used to authenticate the user to the
    WEkEO HDA client, which will then returned as an instance of the
    ClientBuilder class, which is a child of the hda.Client class,
    and can be used to search for datasets and download data.

    Parameters
    ----------
    user : str (optional)
        The username of the user.
    password : str (optional)
        The password of the user.

    """

    def __init__(self, user: str = None, password: str = None):
        config = self._build_config(user=user, password=password)
        super().__init__(config=config)
        self._validate_client(client=self)

    def _build_config(self, user: str = None, password: str = None) -> Client:
        """
        Request and store the user's username and password as environment
        variables.
        """
        if user is None and password is None:
            if (
                os.getenv("HDA_USER") is not None
                and os.getenv("HDA_PASSWORD") is not None
            ):
                user = os.getenv("HDA_USER")
                password = os.getenv("HDA_PASSWORD")
            else:
                user = input("Enter your username: ")
                password = getpass.getpass("Enter your password: ")
                os.environ["HDA_USER"] = user
                os.environ["HDA_PASSWORD"] = password
        else:
            os.environ["HDA_USER"] = user
            os.environ["HDA_PASSWORD"] = password

        config = Configuration(user=user, password=password)
        return config

    @staticmethod
    def _validate_client(client: Client) -> Client:
        """
        Method to validate the client and check for authentication errors.
        """
        try:
            _ = client.token
            return client
        except Exception as e:
            os.environ.pop("HDA_USER")
            os.environ.pop("HDA_PASSWORD")
            raise AuthenticationError() from e
