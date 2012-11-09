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


def to_array(f):
    return numpy.array(f, \
            dtype=[('start', int), ('end', int), ('h', float), ('v', float)])


def find(gd, min_time=0.1 * 1E6, max_dev=3., min_points=10):
    fixations = []
    i = 0
    while i + min_points < len(gd):
        e = i + min_points
        while gd[e]['time'] - gd[i]['time'] < min_time:
            e += 1
            if e == len(gd):
                return to_array(fixations)
        ## check for fixation
        #if e - i < min_points:
        #    # continue with no fixation
        #    i += 1
        #    print 'min points failed'
        #    continue
        f = test_for_fixation(gd[i:e], max_dev)
        pf = f
        while f is not None:
            pf = f
            e += 1
            if e == len(gd):
                fixations.append(pf)
                return to_array(fixations)
            f = test_for_fixation(gd[i:e], max_dev)
        if pf is not None:
            fixations.append(pf)
        i = e
    return to_array(fixations)
