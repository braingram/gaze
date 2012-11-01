#!/usr/bin/env python

import numpy

from .. import ops


def by_deviation(gaze_data, thresh=30.):
    h, v = ops.deviation(gaze_data)
    good = (numpy.abs(h) < thresh) & (numpy.abs(v) < thresh)
    return gaze_data[good]


def by_velocity(gaze_data, thresh=1000.):
    h, v = ops.velocity(gaze_data)
    # finite & sub-threshold: nan < 100 == False
    good = (numpy.abs(h) < thresh) & (numpy.abs(v) < thresh)
    return gaze_data[good]


def by_acceleration(gaze_data, thresh=1000.):
    h, v = ops.acceleration(gaze_data)
    # finite & sub-threshold
    good = (numpy.abs(h) < thresh) & (numpy.abs(v) < thresh)
    good = good[1:] & good[:-1]
    return gaze_data[good]


def constrain(gaze_data, at=1000., dt=30.):
    return by_acceleration(by_deviation(gaze_data, dt), at)
