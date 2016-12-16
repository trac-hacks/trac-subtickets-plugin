import pkg_resources

min_trac_version = '1.0'

pkg_resources.require('Trac >= %s' % min_trac_version)
