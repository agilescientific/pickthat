#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The Pick This web API interface.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""
import requests

from .user import User
from .pick import Pick
from .image import Image as Img


class PickThisAPIError(Exception):
    """
    Generic error class.
    """
    pass


class API(object):

    def __init__(self, url=None):
        if url is None:
            self.url = 'http://dev.pick-this.appspot.com/'
        else:
            self.url = url
        self.headers = {"Accept": "application/json"}

    def __api(self, endpoint, params):
        """
        Raw API call.
        """
        url = self.url.strip('/') + '/' + endpoint.strip('/')
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            raise PickThisAPIError('Server error.')

        return response.json()

    def picks(self, image_id=None, user=None):
        """
        Fetch picks belonging to an image or to a user.
        """
        endpoint = "api/picks"

        if image_id is not None:
            params = {'image_key': image_id,
                      'all': 1}
        else:
            raise NotImplementedError

        all_data = self.__api(endpoint, params)

        results = []
        for data in all_data:
            results.append(Pick(data))
        return results

    def users(self, user_id=None):
        """
        Fetch a user or users.
        """
        endpoint = "api/users"

        params = {}

        if user_id is not None:
            params['user_id'] = user_id
        else:
            params = {'all': 1}

        all_data = self.__api(endpoint, params)

        results = []
        for data in all_data:
            results.append(User(data))
        return results

    def images(self, image_id=None, user=None):
        """
        Fetch data about one or all images.
        """
        endpoint = "api/images"

        params = {}

        if image_id is not None:
            params['image_id'] = image_id
        else:
            params['all'] = 1

        if user is not None:
            raise NotImplementedError

        all_data = self.__api(endpoint, params)

        results = []
        for data in all_data:
            results.append(Img(data))
        return results

