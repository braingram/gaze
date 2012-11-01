#!/usr/bin/env python

import logging

import numpy

import contracts


# make sure we have a version of contracts that supports numpy type checking
def _test_contracts():
    try:
        contracts.check('=0', numpy.arange(1, dtype=numpy.int8)[0])
    except:
        raise ImportError( \
                "Invalid contracts[%s], does not support numpy types" \
                % contracts.__version__)
_test_contracts()

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
        'y_topCR_ref': 0b1 << 3 << 4,
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
        'distance': '>360,<400,(<0|>=0)',
        'y_equator': '>0,<240',
        'y_topCR_ref': 'float,>0,<240',
        'pixels_per_mm': 'float,>0,<50',  # range?
        'Rp': 'float,>10,<100',
        # Block 1969, Lashley 1932 [d:5.51,6.35]
        # this is for eye diameter, the pupil is closer to the center
        'Rp_mm': 'float,>0.5,<4.0',
        }

DGCONTRACTS = {  # TODO will these be tested against arrays or floats?
        'gaze_h': '>-180,<180,(<0|>=0)',
        'gaze_v': '>-180,<180,(<0|>=0)',
        'pupil_radius': '>0.15,<1.3,(<0|>=0)',  # Block 1969 [0.2,1.2]
        'cobra_timestamp': '(<0|>=0)',
        'pupil_x': '>0,<320,(<0|>=0)',  # TODO camera resolution?
        'pupil_y': '>0,<240,(<0|>=0)',
        'cr_x': '>0,<320,(<0|>=0)',
        'cr_y': '>0,<240,(<0|>=0)',
        'calibration_status': '=3,(<0|>=0)',
        }


def parse_error_bits(bits):
    if bits == 0:
        return []
    m = 1
    maxval = max(ERRORS.values())
    rd = {v: k for k, v in ERRORS.iteritems()}
    errors = []
    while m <= maxval:
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


def get_emask():
    r = 0
    for e in ERRORS:
        r |= ERRORS[e]
    return r


def get_info_emask():
    # bits 5 through 18 (inclusive)
    return ((2 ** 18 - 1) ^ (2 ** 4 - 1)) & get_emask()


def get_data_emask():
    # bits 19 through 18 (inclusive)
    return ((2 ** 32 - 1) ^ (2 ** 18 - 1)) & get_emask()


def find_minimum_error_mask(gaze, info, \
        gaze_contracts=None, info_contracts=None):
    """
    Find the 'minimum' expected error for this session.
    This is an attempt to sort out how much info is 'potentially'
    available during the session and an attempt to determine
    what version of the eyetracker was used to generate this data.
    This may differ from the actual mimimum error.

    if the error mask is 0, than the most up-to-date version
    of the eyetracker was used and valid points should have error == 0
    """
    assert isinstance(gaze, numpy.ndarray)

    gaze_contracts = DGCONTRACTS if gaze_contracts is None else gaze_contracts
    info_contracts = DICONTRACTS if info_contracts is None else info_contracts
    emask = 0
    if not len(info):  # NO info is available
        emask |= get_info_emask()
    if not len(gaze):  # NO data is available
        emask |= get_data_emask()
    # old sessions had:
    # only gaze_h, gaze_v
    # h, v, pr, ts

    # if gaze data is missing a value it will all be nan
    for k in gaze_contracts.keys():
        if numpy.sum(numpy.isnan(gaze[k])) == gaze.size:
            emask |= ERRORS[k]

    # what info is present?
    found_info = {}
    for i in info:
        d = i.value.get('calibration', {})
        for k in info_contracts.keys():
            if k in d:
                found_info[k] = 1

    # if some piece of info is missing in ALL info events...
    for k in info_contracts.keys():
        if k not in found_info:
            # add to emask
            emask |= ERRORS[k]

    return emask
