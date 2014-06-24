#!/usr/bin/env python
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
F5 BigIP Load balancer
"""

from reworker.worker import Worker


class BigipWorkerError(Exception):
    """
    Base exception class for BigipWorker errors.
    """
    pass


class BigipWorker(Worker):
    """
    Worker to manipulate nodes and balancers in F5 BigIP devices.
    """

    def process(self, channel, basic_deliver, properties, body, output):
        """
        Frob the things

        `Params Required`:
            * foo: bar
        """
        # Ack the original message
        self.ack(basic_deliver)
        corr_id = str(properties.correlation_id)
        # Notify we are starting
        self.send(
            properties.reply_to, corr_id, {'status': 'started'}, exchange='')

        try:
            try:
                params = body['parameters']
            except KeyError:
                raise BigipWorkerError(
                    'Parameters dictionary not passed to BigIPWorker.'
                    ' Nothing to do!')

            self.app_logger.info('Success for bigip')
            self.send(
                properties.reply_to,
                corr_id,
                {'status': 'completed', 'data': params['seconds']},
                exchange=''
            )
            # Notify on result. Not required but nice to do.
            self.notify(
                'BigipWorker Executed Successfully',
                'BigipWorker successfully executed bigip(%s). See logs.',
                'completed',
                corr_id)
        except BigipWorkerError, fwe:
            # If a BigipWorkerError happens send a failure, notify and log
            # the info for review.
            self.app_logger.error('Failure: %s' % fwe)

            self.send(
                properties.reply_to,
                corr_id,
                {'status': 'failed'},
                exchange=''
            )
            self.notify(
                'BigipWorker Failed',
                str(fwe),
                'failed',
                corr_id)
            output.error(str(fwe))


def main():  # pragma: no cover
    from reworker.worker import runner
    runner(BigipWorker)


if __name__ == '__main__':  # pragma: no cover
    main()
