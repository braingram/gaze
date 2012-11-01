#!/usr/bin/env python

import numpy


def vel(t, v):
    return numpy.hstack(([numpy.nan], (v[1:] - v[:-1]) / (t[1:] - t[:-1])))


def velocity(gaze_data):
    """
    Returns
    -------

        h_vels : horizontal velocities
        v_vels : vertical velocities
    """
    ts = gaze_data['time']
    hs = gaze_data['gaze_h']
    vs = gaze_data['gaze_v']
    return vel(ts, hs), vel(ts, vs)


def acceleration(gaze_data):
    ts = gaze_data['time']
    hv, vv = velocity(gaze_data)
    return vel(ts, hv), vel(ts, vv)


def deviation(gaze_data, stat=numpy.mean):
    hc, vc = stat(gaze_data['gaze_h']), stat(gaze_data['gaze_v'])
    return gaze_data['gaze_h'] - hc, gaze_data['gaze_v'] - vc
