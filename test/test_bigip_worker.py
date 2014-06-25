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
"""
Unittests for the BigIP Worker
"""

import pika
import mock
import copy

from . import TestCase
from replugin import bigipworker
from replugin.bigipworker import BigipWorkerError

MQ_CONF = {
    'server': '127.0.0.1',
    'port': 5672,
    'vhost': '/',
    'user': 'guest',
    'password': 'guest',
}

_base_params = {
    'dynamic': {},
    'group': 'test',
    'notify': {},
    'parameters': {
        'command': 'bigip'
    }
}

class TestBigipWorker(TestCase):

    def setUp(self):
        ##############################################################
        # Parameters dict where the subcommand is invalid
        self.subcommand_params_bad = copy.deepcopy(_base_params)
        self.subcommand_params_bad['parameters'].update({
            'subcommand': 'invalidsubcommand'
        })

        ##############################################################
        # Create a valid in/outofrotation parameters dict
        self.rotation_params_good = copy.deepcopy(_base_params)
        # Rotation commands require a list of hosts
        self.rotation_params_good['parameters'].update({
            'hosts': ['localhost'],
            'subcommand': 'InRotation'
        })

        ##############################################################
        # Create an invalid in/outofrotation parameters dict
        self.rotation_params_bad = copy.deepcopy(_base_params)
        # Rotation command without the required 'hosts' parameter
        self.rotation_params_bad['parameters'].update({
            'subcommand': 'InRotation'
        })

        ##############################################################
        # Create a valid configsync parameters dict
        self.configsync_params_good = copy.deepcopy(_base_params)
        # Sync command with the required environments (envs)
        self.configsync_params_good['parameters'].update({
            'subcommand': 'ConfigSync',
            'envs': ['qa']
        })

        ##############################################################
        # Create an invalid configsync parameters dict
        self.configsync_params_bad = copy.deepcopy(_base_params)
        # Sync command WITHOUT the required environments (envs)
        self.configsync_params_bad['parameters'].update({
            'subcommand': 'ConfigSync'
        })

        ##############################################################
        # Other random stuff
        self.channel = mock.MagicMock('pika.spec.Channel')
        self.channel.basic_consume = mock.Mock('basic_consume')
        self.channel.basic_ack = mock.Mock('basic_ack')
        self.channel.basic_publish = mock.Mock('basic_publish')

        self.basic_deliver = mock.MagicMock()
        self.basic_deliver.delivery_tag = 123

        self.properties = mock.MagicMock(
            'pika.spec.BasicProperties',
            correlation_id=123,
            reply_to='me')

        self.app_logger = mock.MagicMock('logging.Logger').__call__()
        self.logger = mock.MagicMock('logging.Logger').__call__()
        self.connection = mock.MagicMock('pika.SelectConnection')

    def test_subcommand_invalid(self):
        """Invalid subcommands are caught and abort"""
        _params = self.subcommand_params_bad['parameters']
        with mock.patch('pika.SelectConnection'):
            worker = bigipworker.BigipWorker(
                MQ_CONF,
                logger=self.app_logger,
                output_dir='/tmp/logs/')

            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)

            with self.assertRaises(BigipWorkerError):
                worker.validate_inputs(_params)

    def test_configsync_validation_good(self):
        """Good configsync params pass validation"""
        _params = self.configsync_params_good['parameters']
        with mock.patch('pika.SelectConnection'):
            worker = bigipworker.BigipWorker(
                MQ_CONF,
                logger=self.app_logger,
                output_dir='/tmp/logs/')

            result = worker.validate_inputs(_params)
            assert result == True
            assert worker.subcommand == _params['subcommand']
            assert worker.envs == _params['envs']

    def test_configsync_validation_bad(self):
        """Bad configsync params are caught and abort"""
        _params = self.configsync_params_bad['parameters']
        with mock.patch('pika.SelectConnection'):
            worker = bigipworker.BigipWorker(
                MQ_CONF,
                logger=self.app_logger,
                output_dir='/tmp/logs/')

            with self.assertRaises(BigipWorkerError):
                worker.validate_inputs(_params)

    def test_rotation_validation_good(self):
        """Good rotation params pass validation"""
        _params =  self.rotation_params_good['parameters']
        with mock.patch('pika.SelectConnection'):
            worker = bigipworker.BigipWorker(
                MQ_CONF,
                logger=self.app_logger,
                output_dir='/tmp/logs/')

            result = worker.validate_inputs(_params)
            assert result == True
            assert worker.subcommand == _params['subcommand']
            assert worker.hosts == _params['hosts']

    def test_rotation_validation_bad(self):
        """Bad rotation params are caught and abort"""
        _params =  self.rotation_params_bad['parameters']
        with mock.patch('pika.SelectConnection'):
            worker = bigipworker.BigipWorker(
                MQ_CONF,
                logger=self.app_logger,
                output_dir='/tmp/logs/')

            with self.assertRaises(BigipWorkerError):
                worker.validate_inputs(_params)
