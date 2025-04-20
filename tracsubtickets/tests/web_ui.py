# -*- coding: utf-8 -*-

import unittest

from trac.db.api import DatabaseManager
from trac.test import EnvironmentStub, MockRequest
from trac.ticket.web_ui import TicketModule
from trac.web.main import RequestDispatcher

from .. import db_default
from ..api import SubTicketsSystem
from ..web_ui import SubTicketsModule
from . import insert_ticket


class SubTicketsModuleTestCase(unittest.TestCase):

    def setUp(self):
        self.env = env = EnvironmentStub(default_data=True, enable=['trac.*'])
        self.config = config = env.config
        config.set('ticket-custom', 'parents', 'text')
        for cls in (SubTicketsSystem, SubTicketsModule):
            env.enable_component(cls)
        SubTicketsSystem(env).environment_created()

    def tearDown(self):
        DatabaseManager(self.env).drop_tables(db_default.tables)
        self.env.reset_db()

    def test_ticket_view(self):
        with self.env.db_transaction:
            insert_ticket(self.env, type='defect', summary=u'tíckët 1',
                    reporter='alice', owner='bob')
            insert_ticket(self.env, type='defect', summary=u'tíckët 1.1',
                    reporter='bob', owner='bob', parents='1')
            insert_ticket(self.env, type='defect', summary=u'tíckët 1.2',
                    reporter='alice', owner='bob', parents='1')

        req = MockRequest(self.env, path_info='/ticket/1')
        rv = self._dispatch(req)
        div = req.chrome['script_data'].get('subtickets_div')
        self.assertRegex(div, u'<td[^>]*><a[^>]*>#2</a>: tíckët 1\\.1</td>')
        self.assertRegex(div, u'<td[^>]*><a[^>]*>#3</a>: tíckët 1\\.2</td>')

    def _dispatch(self, req):
        dispatcher = RequestDispatcher(self.env)
        handler = TicketModule(self.env)
        self.assertTrue(handler.match_request(req))
        handler = dispatcher._pre_process_request(req, handler)
        rv = handler.process_request(req)
        rv = dispatcher._post_process_request(req, *rv)
        return rv


def test_suite():
    suite = unittest.TestSuite()
    load = unittest.defaultTestLoader.loadTestsFromTestCase
    for testcase in [SubTicketsModuleTestCase]:
        if not hasattr(testcase, 'assertRegex'):
            testcase.assertRegex = testcase.assertRegexpMatches
        suite.addTest(load(testcase))
    return suite
