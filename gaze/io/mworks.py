#!/usr/bin/env python
"""
There are several varieties of gaze data in mworks files including:

    1) gaze_h, gaze_v, cobra_timestamp, pupil_radius
    2) (see 1) + calibration_status, pupil_x/y, cr_x/y, tracker_info
"""

import numpy

from ..data import events


DDTYPE = numpy.dtype([
        ('time', 'u8'),
        ('gaze_h', 'f8'),
        ('gaze_v', 'f8'),
        ('cobra_timestamp', 'f8'),
        ('pupil_radius', 'f8'),
        ('calibration_status', 'f8'),
        ('pupil_x', 'f8'),
        ('pupil_y', 'f8'),
        ('cr_x', 'f8'),
        ('cr_y', 'f8'),
        ])

DINFO = 'tracker_info'


def read_gaze_as_array(df, dtype=None):
    """
    Parameters
    ----------
    df : pymworks.DataFile
        mworks datafile object to read from

    dtype : numpy.dtype
        dtype for gaze data containing names = mworks event names
        must also include 'time' (which will be filled with mworks time stamps)


    Returns
    -------
    gaze : numpy.array
        Array of gaze events with dtype = dtype
    """
    dtype = DDTYPE if dtype is None else dtype
    assert 'time' in dtype.names, "dtype.names must contain time"
    #keys = DKEYS.names() if keys is None else keys
    #info = DINFO if info is None else info
    c = df.codec

    # try to get keys
    evs = {}
    for event_name in dtype.names:
        if event_name in c.values() and event_name != 'time':
            evs[event_name] = df.get_events(event_name)

    # figure out number of events
    ns = [len(e) for e in evs.values()]
    assert len(ns), "No events found"
    assert all([ns[0] == n for n in ns[1:]]), \
            "found unequal number of events: %s" % \
            str([(k, len(v)) for k, v in evs.iteritems()])
    n = ns[0]
    gaze = numpy.empty(n, dtype=dtype)
    get_time = True
    for event_name in dtype.names:
        if event_name in evs.keys():
            gaze[event_name] = numpy.array([e.value for e in evs[event_name]])
            if get_time:
                gaze['time'] = numpy.array([e.time for e in evs[event_name]])
                get_time = False
        else:
            gaze[event_name] = numpy.nan

    return gaze


def read_info(df, name=None):
    name = DINFO if name is None else name
    if name not in df.codec.values():
        return []

    info = []
    for e in df.get_events(name):
        v = e.value if isinstance(e.value, dict) else {}
        info.append(events.Event(e.time, v))
    return info


def read(df):
    return read_gaze_as_array(df), read_info(df)
