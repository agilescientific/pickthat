#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
An object to hold a Pick This image.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""
import requests
import json
from io import BytesIO

from PIL import Image as PImage

from . import pt


class Image(object):
    def __init__(self, data):
        """
        Just set up as a basic dictionary-style object for now.

        """
        self.__dict__ = dict(data)
        for k, v in data.items():
            if k and v:
                setattr(self, k, v)

    def image(self):
        """
        Fetch the image as a PIL Image object.

        No parameters.

        """
        r = requests.get(self.link)
        return PImage.open(BytesIO(r.content))

    def heatmap(self, picks, cohort=None):
        """
        Generate a heatmap for this image from some picks.

        TODO: This should probably be part of an Experiment object.

        """
        layers = []
        for pick in picks:
            p = json.dumps(pick.picks)
            layer, _cohort = pt.create_user_heatmap_layer(self, p, pick.cohort)
            if (not cohort) or (cohort == _cohort):
                layers.append(layer)
        return pt.convert_array_to_image(sum(layers))

    def composite(self, picks, cohort=None):
        pass
