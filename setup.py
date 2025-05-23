#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2010, Takashi Ito
# i18n and German translation by Steffen Hoffmann
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

from setuptools import find_packages, setup

extra = {}

try:
    from trac.util.dist import get_l10n_cmdclass
    cmdclass = get_l10n_cmdclass()
    if cmdclass:
        extra['cmdclass'] = cmdclass
        extractors = [
            ('**.py', 'python', None),
        ]
        extra['message_extractors'] = {'tracsubtickets': extractors}
# i18n is implemented to be optional here.
except ImportError:
    pass


setup(
    name='TracSubTickets',
    version='0.5.5',
    keywords='trac plugin ticket subticket',
    author='Takashi Ito',
    author_email='TakashiC.Ito@gmail.com',
    maintainer='Theodor Norup',
    maintainer_email='theodor.norup@gmail.com',
    url='https://github.com/trac-hacks/trac-subtickets-plugin',
    description='Trac Sub-Tickets Plugin',
    long_description="""
    This plugin for Trac 1.0 and later provides Sub-Tickets functionality.

    The association is done by adding parent tickets' number to a custom field.
    Checks ensure i.e. resolving of sub-tickets before closing the parent.
    Babel is required to display localized texts.
    """,
    license='BSD',

    classifiers=[
        'Framework :: Trac',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    packages=find_packages(exclude=['*.tests*']),
    package_data={
        'tracsubtickets': [
            'htdocs/css/*.css',
            'htdocs/js/*.js',
            'locale/*/LC_MESSAGES/*.mo',
        ],
    },
    entry_points={
        'trac.plugins': [
            'tracsubtickets.api = tracsubtickets.api',
            'tracsubtickets.web_ui = tracsubtickets.web_ui',
        ],
        'console_scripts': [
            'check-trac-subtickets = tracsubtickets.checker:main',
        ],
    },

    **extra
)
