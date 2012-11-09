#!/usr/bin/env python

from copy import deepcopy
import numpy


def check(gd, trials, max_dev=5., min_points=10., raw=True, copy=False):
    """
    gd : gaze data

    trials : list of trials
        trials must have a 'time' (start) and 'duration'
    """
    # for each trial
    # - check if there are enough points (if not, eyes='unknown')
    # - check if max_dev exceeded (if so, eyes='saccade')
    # - else (eyes='fixated')
    if copy:
        ntrials = deepcopy(trials)
    else:
        ntrials = trials[:]
    for (ti, trial) in enumerate(trials):
        start = trial['time']
        end = trial['time'] + trial['duration']
        cgd = gd[(gd['time'] >= start) & (gd['time'] < end)]
        if len(cgd) < min_points:
            state = 'unknown'
        else:
            # test deviation
            mh = numpy.mean(cgd['gaze_h'])
            mv = numpy.mean(cgd['gaze_v'])
            d = numpy.sqrt((cgd['gaze_h'] - mh) ** 2. + \
                    (cgd['gaze_v'] - mv) ** 2.)
            if numpy.any(d > max_dev):
                state = 'saccade'
            else:
                state = 'fixate'
        gaze = dict(state=state)
        if raw:
            gaze['h'] = cgd['gaze_h']
            gaze['v'] = cgd['gaze_v']
            gaze['mh'] = numpy.mean(cgd['gaze_h'])
            gaze['mv'] = numpy.mean(cgd['gaze_v'])
        ntrials[ti]['gaze'] = gaze
    return ntrials
