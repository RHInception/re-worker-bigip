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
import replugin.bigipworker.parser

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
        # Create valid in/outofrotation parameters dicts
        self.rotation_params_good = copy.deepcopy(_base_params)
        # Rotation commands require a list of hosts
        self.rotation_params_good['parameters'].update({
            'hosts': ['localhost'],
            'subcommand': 'InRotation'
        })

        self.inrotation_params_good = copy.deepcopy(_base_params)
        # Rotation commands require a list of hosts
        self.inrotation_params_good['parameters'].update({
            'hosts': ['localhost'],
            'subcommand': 'InRotation'
        })

        self.outofrotation_params_good = copy.deepcopy(_base_params)
        # Rotation commands require a list of hosts
        self.outofrotation_params_good['parameters'].update({
            'hosts': ['localhost'],
            'subcommand': 'OutOfRotation'
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
            'envs': ['testenvironment']
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

        self.parser = replugin.bigipworker.parser.parser

    ##################################################################
    # Subcommand tests
    def test_subcommand_invalid(self):
        """Invalid subcommands are caught and abort"""
        _params = self.subcommand_params_bad['parameters']
        with mock.patch('pika.SelectConnection'):
            worker = bigipworker.BigipWorker(
                MQ_CONF,
                logger=self.app_logger,
                output_dir='/tmp/logs/')

            with self.assertRaises(BigipWorkerError):
                worker.validate_inputs(_params)

    ##################################################################
    # Config sync tests
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

    def test_run_configsync_good(self):
        """Config sync works correctly

I'd write the negative test-case for this, but the argument validaton
that preceeds the actual bigip call should catch mistakes before the
call can be made.
        """
        _params = self.configsync_params_good['parameters']

        namespace = mock.Mock('argparse.Namespace')
        parser = mock.MagicMock('argparse.ArgumentParser').__call__()
        parser.parse_args.__call__().return_value = namespace

        with mock.patch('pika.SelectConnection'):
            worker = bigipworker.BigipWorker(
                MQ_CONF,
                logger=self.app_logger,
                output_dir='/tmp/logs/')

            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)
            worker.validate_inputs(_params)
            worker.config_sync(parser)

            parser.parse_args.assert_called_with(
                ['sync', '-e', _params['envs'][0]])

        # TODO: test with mocked out bigip classes a full call that
        # invokes the bigip sync function

    ##################################################################
    # Rotation tests
    def test_rotation_validation_good(self):
        """Good rotation params pass validation"""
        _params = self.rotation_params_good['parameters']
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
        _params = self.rotation_params_bad['parameters']
        with mock.patch('pika.SelectConnection'):
            worker = bigipworker.BigipWorker(
                MQ_CONF,
                logger=self.app_logger,
                output_dir='/tmp/logs/')

            with self.assertRaises(BigipWorkerError):
                worker.validate_inputs(_params)

    ##################################################################
    # In Rotation tests
    def test_run_inrotation_good(self):
        """InRotation works correctly"""
        _params = self.inrotation_params_good['parameters']
        namespace = mock.Mock('argparse.Namespace')
        parser = mock.MagicMock('argparse.ArgumentParser').__call__()
        parser.parse_args.__call__().return_value = namespace

        with mock.patch('pika.SelectConnection'):
            worker = bigipworker.BigipWorker(
                MQ_CONF,
                logger=self.app_logger,
                output_dir='/tmp/logs/')

            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)
            worker.validate_inputs(_params)

            worker.in_rotation(parser)

            parser.parse_args.assert_called_with(
                ['state', '-e', _params['hosts'][0]])

    ##################################################################
    # Out Of Rotation tests
    def test_run_outofrotation_good(self):
        """OutOfRotation works correctly"""
        _params = self.outofrotation_params_good['parameters']
        namespace = mock.Mock('argparse.Namespace')
        parser = mock.MagicMock('argparse.ArgumentParser').__call__()
        parser.parse_args.__call__().return_value = namespace

        with mock.patch('pika.SelectConnection'):
            worker = bigipworker.BigipWorker(
                MQ_CONF,
                logger=self.app_logger,
                output_dir='/tmp/logs/')

            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)
            worker.validate_inputs(_params)

            worker.out_of_rotation(parser)

            parser.parse_args.assert_called_with(
                ['state', '-d', _params['hosts'][0]])

    # ##################################################################
    # # Running the worker from the main process() entry-point
    # def test_process(self):
    #     param_methods = ['in_rotation', 'out_of_rotation', 'config_sync']
    #     for params in [
    #             self.inrotation_params_good,
    #             self.outofrotation_params_good,
    #             self.configsync_params_good]:

    #         with mock.patch('pika.SelectConnection'):
    #             worker = bigipworker.BigipWorker(
    #                 MQ_CONF,
    #                 logger=self.app_logger,
    #                 output_dir='/tmp/logs/')

    #             worker._on_open(self.connection)
    #             worker._on_channel_open(self.channel)

    #             method = param_methods.pop(0)
    #             with mock.patch.object(worker, method) as mocked_method:
    #                 worker.process(self.channel,
    #                                self.basic_deliver,
    #                                self.properties,
    #                                params,
    #                                self.app_logger)

    #                 print mocked_method.call_args
    #                 assert worker.subcommand == params['parameters']['subcommand']
    #                 assert mocked_method.call_count == 1
