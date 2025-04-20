# -*- coding: utf-8 -*-

import unittest

from trac.ticket.model import Ticket


def insert_ticket(env, **kwargs):
    t = Ticket(env)
    for name in kwargs:
        t[name] = kwargs[name]
    return t.insert()


def test_suite():
    from . import api, web_ui
    modules = list(locals().values())
    suite = unittest.TestSuite()
    for module in modules:
        suite.addTest(module.test_suite())
    return suite
