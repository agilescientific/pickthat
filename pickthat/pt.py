#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Various functions for heatmaps and other Pick This tricks.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""
import numpy as np
import json
import itertools
from io import StringIO

# For image manipulation
from PIL import Image
from .mmorph import dilate, sedisk


def interpolate(x_in, y_in):
    """
    For line interpretations.
    Connect the dots of each interpretation.
    """

    # Check difference in x and in y, so we can
    # interpolate in the direction with the most range

    x_range = np.arange(np.amin(x_in), np.amax(x_in)+1)
    y_range = np.arange(np.amin(y_in), np.amax(y_in)+1)

    if x_range.size >= y_range.size:
        x_out = x_range
        y_out = np.interp(x_out, x_in, y_in)
    else:
        y_out = y_range
        x_out = np.interp(y_out, y_in, x_in)

    return x_out.astype(int), y_out.astype(int)


def normalize(a, newmax):
    """
    Normalize the values of an
    array a to some new max.

    """
    normed = np.zeros_like(a)
    normed = (float(newmax) * a) / np.amax(a)
    return normed


def draw_pick_to_user_layer(user_layer, picks, img_obj):
    """
    This is where the magic happens.
    """
    w = img_obj.width
    h = img_obj.height
    pickstyle = img_obj.pickstyle

    if pickstyle == 'polygons':
        agg = np.append(picks, picks[0])
        picks = agg.reshape(picks.shape[0]+1, picks.shape[1])

    # Deal with the points
    if pickstyle != 'points':
        for i, _ in enumerate(picks[:-1]):

            xpair = picks[i:i+2, 0]

            if xpair[0] > xpair[1]:
                xpair = xpair[xpair[:].argsort()]
                xrev = True
            else:
                xrev = False

            ypair = picks[i:i+2, 1]

            if ypair[0] > ypair[1]:
                ypair = ypair[ypair[:].argsort()]
                yrev = True
            else:
                yrev = False

            # Do the interpolation
            x, y = interpolate(xpair, ypair)

            if xrev:  # then need to unreverse...
                x = x[::-1]
            if yrev:  # then need to unreverse...
                y = y[::-1]

            # Build up the image, accounting for pixels at
            # the edge, which have the wrong indices.
            x[x >= w] = w - 1
            y[y >= h] = h - 1
            user_layer[(y, x)] = 1.

    else:
        x, y = picks[:, 0], picks[:, 1]
        user_layer[(y, x)] = 1.

    return user_layer


def draw_all_picks_to_user_layer(user_layer, all_picks, img_obj):
    if all_picks[0].size == 3:
        # picks are tagged with their group
        # group indicates the feature, eg the line segment
        for group in itertools.groupby(all_picks, lambda x: x[2]):
            picks = np.array([p for p in group[1]])
            return draw_pick_to_user_layer(user_layer, picks, img_obj)
    else:
        return draw_pick_to_user_layer(user_layer, all_picks, img_obj)


def calculate_disk_radius(img_obj):
    w = img_obj.width
    h = img_obj.height
    avg = (w + h) / 2.
    if (img_obj.pickstyle == 'points'):
        n = np.ceil(avg / 150.).astype(int)
    else:
        n = np.ceil(avg / 300.).astype(int)
    return n


def create_user_heatmap_layer(img_obj, picks, cohort):
    w = img_obj.width
    h = img_obj.height

    # Make a new image for this interpretation.
    user_layer = np.zeros((h, w), dtype=np.float32)

    # Get the points.
    all_picks = np.array(json.loads(picks))

    if all_picks.size == 0:
        raise Exception

    user_layer = draw_all_picks_to_user_layer(user_layer, all_picks, img_obj)
    n = calculate_disk_radius(img_obj)

    # Dilate this image.
    return dilate(user_layer.astype(int), B=sedisk(r=n)), cohort


def convert_array_to_image(the_array):
    """
    Normalize the heatmap from 0-255 for making an image.
    More muted version: Subtract 1 first to normalize to
    the non-zero data only.
    """
    heatmap_norm = normalize(the_array, 255)
    alpha_norm = normalize(np.ones_like(heatmap_norm), 255)

    # Make the RGB channels.
    r = np.clip((2 * heatmap_norm), 0, 255)
    g = np.clip(((3 * heatmap_norm) - 255), 0, 255)
    b = np.clip(((3 * heatmap_norm) - 510), 0, 255)
    a = alpha_norm

    # Set everything corresponding to zero data to transparent.
    a[the_array == 0] = 0

    # Make the 4-channel image from an array.
    im = np.dstack([r, g, b, a])
    im_out = Image.fromarray(im.astype('uint8'), 'RGBA')
    return im_out


def array_to_png(the_array):
    im_out = convert_array_to_image(the_array)
    output = StringIO()
    im_out.save(output, 'png')
    return output.getvalue()


def generate_user_heatmap_layer(img_obj, user_data):
    try:
        user_layer, cohort = create_user_heatmap_layer(img_obj, user_data)
        the_png = array_to_png(user_layer)
        user_heatmap = Heatmap.all().ancestor(img_obj).filter("user_id =", user_data.user_id).get()
        if not user_heatmap:
            user_heatmap = Heatmap(stale=False, png=the_png,parent=img_obj, user_id=user_data.user_id, cohort=cohort)
        else:
            user_heatmap.stale = False
            user_heatmap.png = the_png
        user_heatmap.put()

    except HeatMapException:
        pass


def cache_composite_heatmap(img_obj, png, cohort):
    cached_heatmap = Heatmap.all().ancestor(img_obj).filter('user_id =', None)
    cached_heatmap = cached_heatmap.filter('cohort =', cohort)
    cached_heatmap = cached_heatmap.get()
    if not cached_heatmap:
        cached_heatmap = Heatmap(stale=False,
                                 png=png,
                                 parent=img_obj,
                                 user_id=None,
                                 cohort=cohort)
    else:
        cached_heatmap.stale = False
        cached_heatmap.png = png
    cached_heatmap.put()


def create_a_composite_png_from_layers(size, layers):
    """
    Creates a composite from layers, producing a blank image if
    there are no layers.
    """
    heatmap = np.zeros(size, dtype=np.float32)
    for layer in layers:
        try:
            im = np.asarray(Image.open(StringIO(layer.png)))[:, :, 0]
        except AttributeError:
            # Then it's an array if we're in the library
            im = layer
        heatmap += im  # layers are greyscale so just use one channel
    return array_to_png(heatmap)
