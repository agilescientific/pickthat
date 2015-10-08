#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The Pick This web API interface.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""
import requests


class PickThisAPIError(Exception):
    """
    Generic error class.
    """
    pass


class API(object):

    def __init__(self):
        # Could eventually allow any server
        self.url = 'http://dev.pick-this.appspot.com'
        self.headers = {"Accept": "application/json"}

    def __api(self, endpoint, params):
        """
        Raw API call.
        """
        url = self.url + '/' + endpoint
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            raise PickThisAPIError('Server error.')

        return response.json()

    def picks(self, image_id=None, user=None):
        """
        Fetch picks belonging to an image or to a user.
        """
        endpoint = "update_pick"  # TODO change this.
        if image_id is not None:
            params = {'image_key': image_id, 'all': 1}
            all_data = self.__api(endpoint, params)
        else:
            raise NotImplementedError

        return all_data

        # results = []
        # for data in all_data:
        #     results.append(Pick(data))
        # return results

    def users(self, user=None):
        """
        Fetch a user or users.
        """
        endpoint = "users_api"
        if user is not None:
            raise NotImplementedError
        else:
            params = {'all': 1}
            try:
                return self.__api(endpoint, params)
            except ValueError:
                raise PickThisAPIError('API error.')

    def images(self, image_id=None, user=None):
        """
        Fetch data about one or all images.
        """
        endpoint = "image_api"
        if image_id is not None:
            params = {'image_key': image_id}
            return self.__api(endpoint, params)
        elif user is not None:
            raise NotImplementedError
        else:
            params = {'all': 1}
            try:
                return self.__api(endpoint, params)
            except ValueError:
                raise PickThisAPIError('API error.')
