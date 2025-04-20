# -*- coding: utf-8 -*-

import unittest

from trac.core import Component, implements
from trac.db.api import DatabaseManager
from trac.test import EnvironmentStub
from trac.ticket.model import Ticket
from trac.util.text import to_utf8
try:
    from trac.notification.api import IEmailSender
except ImportError:
    from trac.notification import IEmailSender
import trac.ticket.web_ui
del trac.ticket.web_ui

from .. import db_default
from ..api import SubTicketsSystem
from . import insert_ticket


class EmailSenderStub(Component):

    implements(IEmailSender)

    def __init__(self):
        self.history = []

    def send(self, from_addr, recipients, message):
        self.history.append((from_addr, recipients, message))


class SubTicketsSystemTestCase(unittest.TestCase):

    def setUp(self):
        self.env = env = EnvironmentStub(
                default_data=True, enable=['trac.*', EmailSenderStub])
        self.config = config = env.config
        config.set('ticket-custom', 'parents', 'text')
        config.set('notification', 'email_sender', 'EmailSenderStub')
        config.set('notification', 'smtp_always_cc', 'cc@example.org')
        config.set('notification', 'smtp_enabled', 'enabled')
        for cls in (SubTicketsSystem,):
            env.enable_component(cls)
        SubTicketsSystem(env).environment_created()

    def tearDown(self):
        DatabaseManager(self.env).drop_tables(db_default.tables)
        self.env.reset_db()

    def test_db_version(self):
        with self.env.db_query as db:
            rows = db("SELECT value FROM {0} WHERE name=%s"
                      .format(db.quote('system')), [db_default.name])
        self.assertEqual([(str(db_default.version),)], rows)

    def test_subtickets(self):
        with self.env.db_transaction:
            insert_ticket(self.env, type='defect', summary=u'tíckët 1',
                    reporter='alice', owner='bob')
            insert_ticket(self.env, type='defect', summary=u'tíckët 1.1',
                    reporter='bob', owner='bob', parents='1')
            insert_ticket(self.env, type='defect', summary=u'tíckët 1.2',
                    reporter='alice', owner='bob', parents='1')
        self.assertEqual([(1, 2), (1, 3)], self._fetch_subtickets())
        comments = self._fetch_comments(1)
        emails = self._get_email_history()
        self.assertEqual('bob', comments[-2][1])
        expected = u'Add a subticket #2 (tíckët 1.1).'
        self.assertEqual(expected, comments[-2][4])
        self.assertIn('cc@example.org', emails[-2][1])
        self.assertIn(to_utf8(expected), emails[-2][2])
        self.assertEqual('alice', comments[-1][1])
        expected = u'Add a subticket #3 (tíckët 1.2).'
        self.assertEqual(expected, comments[-1][4])
        self.assertIn(to_utf8(expected), emails[-1][2])

        with self.env.db_transaction:
            insert_ticket(self.env, type='defect', summary=u'tíckët 2',
                    reporter='alice', owner='bob')
            tkt = Ticket(self.env, 2)
            tkt['parents'] = '4 1'
            tkt.save_changes('bob')
        self.assertEqual([(1, 2), (1, 3), (4, 2)],
                         self._fetch_subtickets())
        comments = self._fetch_comments(4)
        emails = self._get_email_history()
        self.assertEqual('bob', comments[-1][1])
        expected = u'Add a subticket #2 (tíckët 1.1).'
        self.assertEqual(expected, comments[-1][4])
        self.assertIn(to_utf8(expected), emails[-1][2])

        with self.env.db_transaction:
            tkt = Ticket(self.env, 2)
            tkt['parents'] = str(4)
            tkt.save_changes('alice')
        self.assertEqual([(1, 3), (4, 2)],
                         self._fetch_subtickets())
        comments = self._fetch_comments(1)
        emails = self._get_email_history()
        self.assertEqual('alice', comments[-1][1])
        expected = u'Remove a subticket #2 (tíckët 1.1).'
        self.assertEqual(expected, comments[-1][4])
        self.assertIn(to_utf8(expected), emails[-1][2])

        Ticket(self.env, 3).delete()
        self.assertEqual([(4, 2)], self._fetch_subtickets())

        Ticket(self.env, 4).delete()
        self.assertEqual([(4, 2)], self._fetch_subtickets())

    def _fetch_subtickets(self):
        return self.env.db_query('SELECT parent, child FROM subtickets '
                                 'ORDER BY parent, child')

    def _fetch_comments(self, id_):
        t = Ticket(self.env, id_)
        return [item for item in t.get_changelog() if item[2] == 'comment']

    def _get_email_history(self):
        return EmailSenderStub(self.env).history


def test_suite():
    suite = unittest.TestSuite()
    load = unittest.defaultTestLoader.loadTestsFromTestCase
    for testcase in [SubTicketsSystemTestCase]:
        suite.addTest(load(testcase))
    return suite
