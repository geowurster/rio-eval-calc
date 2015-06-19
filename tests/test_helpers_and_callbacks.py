from collections import OrderedDict

import affine
import click
import pytest

import rio_eval_calc.core


def test_cb_bbox():

    good = (-1, -1, 1, 1)
    bad = (-1, 10, 1, 1)
    assert rio_eval_calc.core._cb_bbox(None, None, None) == None
    assert rio_eval_calc.core._cb_bbox(None, None, good) == good
    with pytest.raises(click.BadParameter):
        rio_eval_calc.core._cb_bbox(None, None, bad)


def test_cb_name():

    values = ('a=something', 'b=other', 'C=as:dfasdf=asdfasdfa')
    expected = OrderedDict((
        ('a', 'something'),
        ('b', 'other'),
        ('C', 'as:dfasdf=asdfasdfa')
    ))
    assert rio_eval_calc.core._cb_name(None, None, None) == {}
    assert rio_eval_calc.core._cb_name(None, None, values) == expected
    with pytest.raises(click.BadParameter):
        rio_eval_calc.core._cb_name(None, None, ('no-equals'))
    with pytest.raises(click.BadParameter):
        rio_eval_calc.core._cb_name(None, None, ('2=var-not-a-letter'))


def window_filter():
    aff = affine.Affine(1, 0.0, -180,
                        0.0, -1, 90)
    bbox = (-180, -90, 180, 90)
    in_windows = [
        ((85, 95), (175, 185)),  # Center
        ((-10, 10), (-10, 10)),  # UL
        ((-10, 10), (200, 210)),  # UR
        ((200, 210), (-10, 10)),  # LL
        ((200, 210), (200, 210))  # LR
    ]
    out_windows = [
        ((-20, -10), (-20, -10)),  # URL
        ((-20, -10), (200, 210)),  # UR
        ((200, 210), (-10, -20)),  # LL
        ((200, 210), (200, 210))  # LR
    ]
    assert len(list(rio_eval_calc.core.window_filter(in_windows, bbox, aff))) == len(in_windows)
    assert len(list(rio_eval_calc.core.window_filter(out_windows, bbox, aff))) == 0
