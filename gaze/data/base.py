#!/usr/bin/env python


class Gaze(object):
    """
    at a minimum need:
        h : h gaze angle
        v : v gaze angle
        t : time

    each data point may also include 'meta' data
        ts : timestamp
        pr : pupil radius
        cs : calibration status
        px : pupil x
        py : pupil y
        cx : corneal reflection x
        cy : corneal reflection y
        ti : tracker info : (less frequent)
    """
    def __init__(self):
        pass

    def get_h(self):
        pass

    def get_v(self):
        pass
