# Copyright (c) 2015 Ansible, Inc.
# All Rights Reserved.

from django.conf import settings
from django.core.management.base import BaseCommand
from kombu import Connection, Exchange, Queue

from awx.main.dispatch.worker import AWXConsumer, CallbackBrokerWorker


class Command(BaseCommand):
    '''
    Save Job Callback receiver (see awx.plugins.callbacks.job_event_callback)
    Runs as a management command and receives job save events.  It then hands
    them off to worker processors (see Worker) which writes them to the database
    '''
    help = 'Launch the job callback receiver'

    def handle(self, *arg, **options):
        with Connection(settings.BROKER_URL) as conn:
            try:
                AWXConsumer(
                    conn,
                    CallbackBrokerWorker(),
                    [
                        Queue(
                            settings.CALLBACK_QUEUE,
                            Exchange(settings.CALLBACK_QUEUE, type='direct'),
                            routing_key=settings.CALLBACK_QUEUE
                        )
                    ],
                ).run()
            except KeyboardInterrupt:
                print('Terminating Callback Receiver')
