# -*- coding: utf-8 -*-
#
# Copyright (c) 2010, Takashi Ito
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the authors nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import re

import pkg_resources

from trac.config import BoolOption
from trac.core import Component, implements
from trac.db import DatabaseManager
from trac.env import IEnvironmentSetupParticipant
from trac.resource import ResourceNotFound
from trac.ticket.api import ITicketChangeListener, ITicketManipulator
from trac.ticket.model import Ticket
from trac.util.text import exception_to_unicode
from trac.util.translation import domain_functions
try:
    TicketNotifyEmail = None
    from trac.notification.api import NotificationSystem
    from trac.ticket.notification import TicketChangeEvent
except ImportError:
    NotificationSystem = TicketChangeEvent = None
    from trac.ticket.notification import TicketNotifyEmail

import db_default


NUMBERS_RE = re.compile(r'\d+', re.U)

# i18n support for plugins, available since Trac r7705
# use _, tag_ and N_ as usual, e.g. _("this is a message text")
_, tag_, N_, add_domain = domain_functions('tracsubtickets',
                                           '_', 'tag_', 'N_', 'add_domain')


class SubTicketsSystem(Component):

    implements(IEnvironmentSetupParticipant,
               ITicketChangeListener,
               ITicketManipulator)

    opt_no_modif_w_p_c = BoolOption(
        'subtickets', 'no_modif_when_parent_closed', default='false',
        doc=_("""If `True`, any modification of a child whose parent is `closed`
        will be blocked. If `False`, status changes will be blocked as
        controlled by the setting of `skip_closure_validation`.

        For compatibility with plugin versions prior to 0.5 that blocked
        any modification unconditionally.
        """))

    def __init__(self):
        self._version = None
        self.ui = None
        # bind the 'traccsubtickets' catalog to the locale directory
        try:
            locale_dir = pkg_resources.resource_filename(__name__, 'locale')
        except KeyError:
            pass
        else:
            add_domain(self.env.path, locale_dir)

    # IEnvironmentSetupParticipant methods

    def environment_created(self):
        self.found_db_version = 0
        self.upgrade_environment()

    def environment_needs_upgrade(self, db=None):
        with self.env.db_query as db:
            for value, in db("""
                    SELECT value FROM system WHERE name=%s
                    """, (db_default.name,)):
                self.found_db_version = int(value)
                if self.found_db_version < db_default.version:
                    return True
                break
            else:
                self.found_db_version = 0
                return True

            # check the custom field
            if 'parents' not in self.config['ticket-custom']:
                return True

            return False

    def upgrade_environment(self, db=None):
        db_manager = DatabaseManager(self.env).get_connector()[0]

        # update the version
        with self.env.db_transaction as db:
            old_data = {}  # {table.name: (cols, rows)}
            cursor = db.cursor()
            if not self.found_db_version:
                cursor.execute("""
                    INSERT INTO system (name, value) VALUES (%s, %s)
                    """, (db_default.name, db_default.version))
            else:
                cursor.execute("""
                    UPDATE system SET value=%s WHERE name=%s
                    """, (db_default.version, db_default.name))

                for table in db_default.tables:
                    cursor.execute("""
                        SELECT * FROM """ + table.name)
                    cols = [x[0] for x in cursor.description]
                    rows = cursor.fetchall()
                    old_data[table.name] = (cols, rows)
                    cursor.execute("""
                        DROP TABLE """ + table.name)

            # insert the default table
            for table in db_default.tables:
                for sql in db_manager.to_sql(table):
                    cursor.execute(sql)

                # add old data
                if table.name in old_data:
                    cols, rows = old_data[table.name]
                    sql = """
                        INSERT INTO %s (%s) VALUES (%s)
                        """ % (table.name, ','.join(cols),
                               ','.join(['%s'] * len(cols)))
                    for row in rows:
                        cursor.execute(sql, row)

            # add the custom field
            cfield = self.config['ticket-custom']
            if 'parents' not in cfield:
                cfield.set('parents', 'text')
                cfield.set('parents.label', 'Parent Tickets')
                self.config.save()

    # ITicketChangeListener methods

    def ticket_created(self, ticket):
        self.ticket_changed(ticket, '', ticket['reporter'], {'parents': ''})

    def ticket_changed(self, ticket, comment, author, old_values):
        if 'parents' not in old_values:
            return

        old_parents = old_values.get('parents', '') or ''
        old_parents = set(NUMBERS_RE.findall(old_parents))
        new_parents = set(NUMBERS_RE.findall(ticket['parents'] or ''))

        if new_parents == old_parents:
            return

        with self.env.db_transaction as db:
            # remove old parents
            for parent in old_parents - new_parents:
                db("""
                    DELETE FROM subtickets WHERE parent=%s AND child=%s
                    """, (parent, ticket.id))
                # add a comment to old parent
                xticket = Ticket(self.env, parent)
                xticket.save_changes(
                    author,
                    _('Remove a subticket #%(id)s (%(summary)s).',
                      id=ticket.id, summary=ticket['summary']))
                self.send_notification(xticket, author)

            # add new parents
            for parent in new_parents - old_parents:
                db("""
                    INSERT INTO subtickets VALUES(%s, %s)
                    """, (parent, ticket.id))
                # add a comment to new parent
                xticket = Ticket(self.env, parent)
                xticket.save_changes(author, _('Add a subticket #%s (%s).') % (
                    ticket.id, ticket['summary']))
                self.send_notification(xticket, author)

    def ticket_deleted(self, ticket):
        with self.env.db_transaction as db:
            cursor = db.cursor()
            # TODO: check if there's any child ticket
            cursor.execute("""
                DELETE FROM subtickets WHERE child=%s
                """, (ticket.id, ))

    # ITicketManipulator methods

    def prepare_ticket(self, req, ticket, fields, actions):
        pass

    def validate_ticket(self, req, ticket):
        try:
            invalid_ids = set()
            _ids = set(NUMBERS_RE.findall(ticket['parents'] or ''))
            myid = str(ticket.id)
            for id in _ids:
                if id == myid:
                    invalid_ids.add(id)
                    yield 'parents', _("A ticket cannot be a parent of itself")
                else:
                    # check if the id exists
                    tkt_id = self.env.db_query("""
                        SELECT id FROM ticket WHERE id=%s
                        """, (id, ))
                    if not tkt_id:
                        invalid_ids.add(id)
                        yield 'parents', _("Ticket #%(id)s does not exist",
                                           id=id)

            # circularity check function
            def _check_parents(id, all_parents):
                all_parents = all_parents + [id]
                errors = []
                parents = self.env.db_query("""
                    SELECT parent FROM subtickets WHERE child=%s
                    """, (id, ))
                for x in [int(x[0]) for x in parents]:
                    if x in all_parents:
                        invalid_ids.add(x)
                        error = ' > '.join(
                            '#%s' % n for n in all_parents + [x])
                        errors.append(('parents', _('Circularity error: %(e)s',
                                                    e=error)))
                    else:
                        errors += _check_parents(x, all_parents)
                return errors

            for x in [i for i in _ids if i not in invalid_ids]:
                # Refuse modification if parent closed
                # or if parentship is to be made circular
                try:
                    parent = Ticket(self.env, x)
                    if parent and parent['status'] == 'closed' \
                       and self.opt_no_modif_w_p_c:
                        invalid_ids.add(x)
                        yield None, _("""Cannot modify ticket because
                            parent ticket #%(id)s is closed.
                            Comments allowed, though.""",
                                      id=x)
                    # check circularity
                    all_parents = ticket.id and [ticket.id] or []
                    for error in _check_parents(int(x), all_parents):
                        yield error
                except ResourceNotFound:
                    invalid_ids.add(x)

            valid_ids = _ids.difference(invalid_ids)
            ticket['parents'] = valid_ids and ', '.join(
                sorted(valid_ids, key=lambda x: int(x))) or ''
        except Exception:
            import traceback
            self.log.error(traceback.format_exc())
            yield 'parents', _('Not a valid list of ticket IDs.')

    def send_notification(self, ticket, author):
        if TicketNotifyEmail:
            tn = TicketNotifyEmail(self.env)
            tn.notify(ticket, newticket=False, modtime=ticket['changetime'])
        else:
            event = TicketChangeEvent('changed', ticket, ticket['changetime'],
                                      author)
            try:
                NotificationSystem(self.env).notify(event)
            except Exception as e:
                self.log.error("Failure sending notification on change to "
                               "ticket #%s: %s",
                               ticket.id, exception_to_unicode(e))
