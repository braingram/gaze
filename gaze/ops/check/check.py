#!/usr/bin/env python

import logging

import numpy

import contracts

from ...utils import cursor

ERRORS = {
        # general: reserve 4 bits
        'none': 0,
        'error': 0b1,
        'unknown': 0b10,
        # up to: 0b1000

        # tracker codes: reserve 14 bits
        'tracker_unknown': 0b1 << 0 << 4,
        'distance': 0b1 << 1 << 4,
        'y_equator': 0b1 << 2 << 4,
        'y_topCR': 0b1 << 3 << 4,
        'pixels_per_mm': 0b1 << 4 << 4,
        'Rp': 0b1 << 5 << 4,
        'Rp_mm': 0b1 << 6 << 4,
        # up to: 0b1 << 13 << 4

        # gaze event codes: reserve 14 bits
        'gaze_h': 0b1 << 0 << 18,
        'gaze_v': 0b1 << 1 << 18,
        'cobra_timestamp': 0b1 << 2 << 18,
        'pupil_radius': 0b1 << 3 << 18,
        'calibration_status': 0b1 << 4 << 18,
        'pupil_x': 0b1 << 5 << 18,
        'pupil_y': 0b1 << 6 << 18,
        'cr_x': 0b1 << 7 << 18,
        'cr_y': 0b1 << 8 << 18,
        # up to: 0b1 << 13 << 18
        }

# shortcut for isnan: '<0|>=0' will pass for all numbers (and inf)
DICONTRACTS = {
        'distance': '>360,<400,<0|>=0',
        'y_equator': 'int,>0,<240',
        'y_topCR': 'float,>0,<240',
        'pixels_per_mm': 'float,>0,<30',
        'Rp': 'float,>10,<100',
        'Rp_mm': 'float,>0.5,<5.0',
        }

DGCONTRACTS = {  # TODO will these be tested against arrays or floats?
        'gaze_h': '>-180,<180,<0|>=0',
        'gaze_v': '>-180,<180,<0|>=0',
        'pupil_radius': '>0,<0|>=0',
        'cobra_timestamp': '<0|>=0',
        'pupil_x': '>0,<320,<0|>=0',  # TODO camera resolution?
        'pupil_y': '>0,<240,<0|>=0',
        'cr_x': '>0,<320,<0|>=0',
        'cr_y': '>0,<240,<0|>=0',
        'calibration_status': '=3,<0|>=0',
        }


def parse_error_bits(bits):
    if bits == 0:
        return ['none']
    m = 1
    maxval = max(ERRORS.values())
    rd = {v: k for k, v in ERRORS.iteritems()}
    errors = []
    while m < maxval:
        if (m & bits):
            if m in rd.keys():
                errors.append(rd[m])
            else:
                raise ValueError("Unknown error code: %i" % m)
        m = (m << 1)
    return errors


def test_check(check, datum):
    try:
        contracts.check(check, datum)
        return True
    except contracts.ContractNotRespected as E:
        #logging.warning("%r" % E)
        return False


def test_checks(checks, data):
    keys = data.keys() if hasattr(data, 'keys') else data.dtype.names
    r = 0
    for k, c in checks.iteritems():
        if (k not in keys) or (not test_check(c, data[k])):
            if k in ERRORS.keys():
                r |= ERRORS[k]
            else:
                r |= ERRORS['unknown']
                logging.warning('unknown error: %s' % k)
    return r


def check_info(info, checks):
    if (not hasattr(info, 'value')) or (not isinstance(info.value, dict)) or \
            ('calibration' not in info.value.keys()) or \
            (not isinstance(info.value['calibration'], dict)):
        return ERRORS['tracker_unknown']

    # run through checks
    return test_checks(checks, info.value['calibration'])


def check_gaze(gaze, checks):
    return test_checks(checks, gaze)


def check_validity(gaze, info, gaze_contracts=None, info_contracts=None):

    assert isinstance(gaze, numpy.ndarray)

    gaze_contracts = DGCONTRACTS if gaze_contracts is None else gaze_contracts
    info_contracts = DICONTRACTS if info_contracts is None else info_contracts

    ic = cursor.Cursor(sorted(info, key=lambda i: i.time))
    gc = cursor.Cursor(numpy.sort(gaze, order=['time']))

    errors = []
    # don't check info every time, only after advancing
    ie = check_info(ic.current(), info_contracts)
    while not gc.end():
        tg = gc.current()['time']
        # check if ic needs advancing
        while (not ic.end()) and (ic.peek().time < tg):
            ic.advance()
            # don't check info every time, only after advancing
            ie = check_info(ic.current(), info_contracts)
        e = ie
        # check if point is valid
        e |= check_gaze(gc.current(), gaze_contracts)
        # advance gaze cursor
        gc.advance()
        errors.append(e)
    return errors
