#!/usr/bin/env python

import datautils.grouping

import pymworks
import pymworks.events

import gaze.io.mworks
import gaze.ops.check.check
import gaze.ops.check.trials
import gaze.opts.clean.constrain

fn = 'test.mwk'

# open file
df = pymworks.open_file(fn)

# read gaze data & info (g = 2 tuple)
g = gaze.io.mworks.read(df)

# find valid gaze data
c = gaze.ops.check.check.check_validity(*g)
#min_error_mask = gaze.ops.check.check.find_minimum_error_mask(*g)

# remove invalid data
cg = g[0][c == 0]

# remove data outside of 'reasonable' bounds
ccg = gaze.ops.clean.constrain.constrain(cg)

# read trial data
trials = pymworks.events.to_stims(df.get_events('#stimDisplayUpdate'))

# use checked & cleaned data to label trials
trials = gaze.ops.check.trials.check(ccg, trials)

gtrials = datautils.grouping.group(trials, key=lambda x: x['gaze']['state'])

print "Total number of trials :", len(trials)
print "Trials by state"
for g in sorted(gtrials.keys()):
    print "\t%s : %i" % (g, len(gtrials[g]))
