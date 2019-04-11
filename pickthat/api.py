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
import getpass, json


class PickThisAPIError(Exception):
    """
    Generic error class.
    """
    pass


class API(object):

    def __init__(self, url=None, email=None, apikey=None):
        if url is None:
            self.url = 'http://pickthis.serveo.net/'
        else:
            self.url = url
        if not apikey:
            self.email = email
            self.password = getpass.getpass(prompt="Password")
            user_response = self.__login(self.email, self.password)

            self.user = json.loads(user_response.text)

        self.headers = {"Accept": "application/json"}

    def __api(self, endpoint, params):
        """
        Raw API call.
        """
        url = self.url.strip('/') + '/' + endpoint.strip('/')

        response = requests.get(url, headers=self.headers, params=params,
                                auth=(int(self.user["id"]), self.password))

        # if response.status_code != 200:
        #     raise PickThisAPIError('Server error.')

        return response.json()

    def __login(self, email, password):

        url = self.url.strip('/')

        resp = requests.post(url + "/login",
                            json={"email": email,
                                "password": password})
        
        return resp

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

    def experiments(self):
        """
        Fetch Categories.
        """

        endpoint = "/experiments"

        params = {
            'offset': 0, 
            'limit': 8, 
            'keyword': '',
            'sortby': '', 
            '&category': ''
        }

        data = self.__api(endpoint, params)

        return data

    def __upload_image(self, image_file):
        """
        Upload an image with path image_file.
        """

        endpoint = "/upload_image"

        # upload an image
        files = {"file":
                open(image_file,
                    'rb')}
        
        response = requests.post(self.url.strip("/") + endpoint,
                        files=files,
                        auth=(self.user["id"], self.password))

        if response.status_code != 200:
            raise PickThisAPIError('Error uploading image.')

        image_data = json.loads(response.text)
        return image_data

    def __update_image(self, image_id, image_meta):
        """
        Add meta data image_data to image with id image_id.
        """
        
        endpoint = '/image/' + str(image_id)

        response = requests.put(self.url.strip("/") + endpoint,
                        json=image_meta,
                        auth=(self.user["id"], self.password))

        if response.status_code != 200:
            raise PickThisAPIError('Error adding image meta data.')

        return response

    def create_experiment(self, image_path, image_data, exp_data):
        """
        Public method to upload an experiment and its corresponding
        image.
        Input:
            image_path(str): path to experiment image.
            image_data(dict): meta data of image.
            exp_data(dict): experiment data.

        Return:
            dict with {"id":experiment_id, "url":url_to_experiment}
        """
        
        endpoint = '/experiments/picking_challenge'

        image_resp = self.__upload_image(image_path)
        image_meta = self.__update_image(image_resp["id"], image_data)

        exp_data["image_id"] = image_resp["id"]
        exp_data["client_url"] = "localhost"
        
        response = requests.post(self.url.strip("/") + endpoint,
                        json=exp_data,
                        auth=(self.user["id"], self.password))

        if response.status_code != 200:
            raise PickThisAPIError('Error uploading experiment.')

        return json.loads(response.text)

    def categories(self):
        """
        Fetch Categories.
        """

        endpoint = "/categories"
        params = {}

        data = self.__api(endpoint, params)

        return data

