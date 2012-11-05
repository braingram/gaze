#!/usr/bin/env python

import numpy

from .. import ops

# TODO: should I 'crater' data around errors?
# so an error at 2 would remove, 1, 2, 3, etc...?
# scipy.ndimage.morphology.binary_erosion (on good)
# or
# scipy.ndimage.morphology.binary_dilation (on errors)

DDEVTHRESH = 30.
DVELTHRESH = 1000.
DACCELTHRESH = 1000.


def by_deviation_mask(gaze_data, thresh=None):
    thresh = DDEVTHRESH if thresh is None else thresh
    h, v = ops.deviation(gaze_data)
    return (numpy.abs(h) < thresh) & (numpy.abs(v) < thresh)


def by_deviation(gaze_data, thresh=None):
    return gaze_data[by_deviation_mask(gaze_data, thresh)]


def by_velocity_mask(gaze_data, thresh=None):
    thresh = DVELTHRESH if thresh is None else thresh
    h, v = ops.velocity(gaze_data)
    # finite & sub-threshold: nan < 100 == False
    return (numpy.abs(h) < thresh) & (numpy.abs(v) < thresh)


def by_velocity(gaze_data, thresh=None):
    return gaze_data[by_velocity_mask(gaze_data, thresh)]


def by_acceleration_mask(gaze_data, thresh=None):
    thresh = DACCELTHRESH if thresh is None else thresh
    h, v = ops.acceleration(gaze_data)
    # finite & sub-threshold
    good = (numpy.abs(h) < thresh) & (numpy.abs(v) < thresh)
    return numpy.array([False, ] + list(good[1:] & good[:-1]))


def by_acceleration(gaze_data, thresh=None):
    return gaze_data[by_acceleration_mask(gaze_data, thresh)]


def constrain_mask(gaze_data, at=None, dt=None):
    return by_acceleration_mask(gaze_data, at) & \
            by_deviation_mask(gaze_data, dt)


def constrain(gaze_data, **kwargs):
    return gaze_data[constrain_mask(gaze_data, **kwargs)]
