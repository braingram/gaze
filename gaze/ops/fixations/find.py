#!/usr/bin/env python


import numpy


def test_for_fixation(gd, max_dev):
    t = gd['time']
    h = gd['gaze_h']
    v = gd['gaze_v']
    mh = numpy.mean(h)
    mv = numpy.mean(v)
    d = numpy.sqrt((mh - h) ** 2. + (mv - v) ** 2.)
    if any(d > max_dev):
        return None
    return (t[0], t[-1], mh, mv)


def find(gd, min_time=0.1, max_dev=1., min_points=2):
    t = gd['time'] / 1E6
    i = 0
    s = 0
    while i < len(gd):
        if t[i] - t[s] >= min_time:
            if i - s >= min_points:
                f = test_for_fixation(gd[s:i], max_dev)
                if f is not None:
                    yield f
            s += 1
        i += 1
