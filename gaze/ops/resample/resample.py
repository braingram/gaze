#!/usr/bin/env python

import math

import numpy


def resample(gd, max_dt=0.1 * 1E6, sf=100. / 1E6):
    mintime = gd['time'].min()
    maxtime = gd['time'].max()
    n = int(math.ceil((maxtime - mintime) * sf))
    print "N:", n
    thv = numpy.empty(n, dtype=[('time', numpy.uint64), \
            ('h', float), ('v', float)])
    thv['time'] = numpy.linspace(mintime, maxtime, n)
    thv['h'] = numpy.nan
    thv['v'] = numpy.nan
    for i in xrange(len(gd) - 1):
        cgd = gd[i]
        ngd = gd[i + 1]
        # find thv points that fall between (inclusive)
        # cgd['time'] and ngd['time']
        #thvm = (thv[notsetmask]['time'] >= cgd['time']) & \
        #        (thv[notsetmask]['time'] <= ngd['time'])
        thvm = (thv['time'] >= cgd['time']) & \
                (thv['time'] <= ngd['time'])
        if not numpy.sum(thvm):
            continue
        #thvm = numpy.where(thvm)[0]
        # process gd[i] to gd[i+1]
        if (ngd['time'] - cgd['time']) > max_dt:
            thv['h'][thvm] = numpy.nan
            thv['v'][thvm] = numpy.nan
            # TODO what about exact matches?
        else:
            #thv['h'][thvm] = cgd['gaze_h']
            #thv['v'][thvm] = cgd['gaze_v']
            nm = numpy.sum(thvm)
            thv['h'][thvm] = numpy.linspace(cgd['gaze_h'], ngd['gaze_h'], nm)
            thv['v'][thvm] = numpy.linspace(cgd['gaze_v'], ngd['gaze_v'], nm)
    thv['h'][-1] = ngd['gaze_h']
    thv['v'][-1] = ngd['gaze_v']
    return thv
