#!/usr/bin/env python


import numpy

DGF = [('calibration_status', numpy.equal, 3),
       ('gaze_h', numpy.greater, -180),
       ('gaze_h', numpy.less, 180),
       ('gaze_v', numpy.greater, -180),
       ('gaze_v', numpy.less, 180),
       ('pupil_radius', numpy.greater, 0.15),
       ('pupil_radius', numpy.less, 1.3),  # Block 1969 [0.2, 1.2]
       ('pupil_x', numpy.greater, 0),
       ('pupil_x', numpy.less, 320),
       ('pupil_y', numpy.greater, 0),
       ('pupil_y', numpy.less, 240),
       ('cr_x', numpy.greater, 0),
       ('cr_x', numpy.less, 320),
       ('cr_y', numpy.greater, 0),
       ('cr_y', numpy.less, 240),
       ]


def filter_gaze(gdata, filters=None, mask=False):
    if filters is None:
        filters = DGF
    m = numpy.ones(gdata.size, dtype=bool)
    for f in filters:
        m = numpy.logical_and(m, f[1](gdata[f[0]], *f[2:]))
    if mask:
        return m
    return gdata[m]
