# Copyright (C) 2014 SEE AUTHORS FILE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""F5 BigIP Load balancer.

The BigIP python package stores its parser in /bin/bigip. This is
basically a small copy of that arg parser (with unused bits removed)
so we can call the bigip entry-point functions properly.
"""

import argparse
import BigIP

parser = argparse.ArgumentParser()
BigIP.parser = parser
parser.add_argument('-v', action='count')
subparsers = parser.add_subparsers(title='Commands', dest='command')

parser_state = subparsers.add_parser('state')
parser_state.add_argument('-e', metavar='host', nargs='+', default=[], dest='enabled_hosts')
parser_state.add_argument('-d', metavar='host', nargs='+', default=[], dest='disabled_hosts')
parser_state.set_defaults(func=BigIP.state)

parser_sync = subparsers.add_parser('sync')
parser_sync.add_argument('-e', metavar='envs', nargs='+', default=[], dest='environments')
parser_sync.set_defaults(func=BigIP.sync)

parser_show = subparsers.add_parser('show')
parser_show.add_argument('hosts', metavar='host', nargs='+')
parser_show.set_defaults(func=BigIP.show)
parser_show.set_defaults(func=BigIP.show)
