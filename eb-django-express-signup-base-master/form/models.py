from django.db import models
import boto3
import os
import logging


SQS_QUEUE_URL = os.environ['SQS_QUEUE_URL']

logger = logging.getLogger(__name__)


class Leads(models.Model):

    def insert_lead(self, MessageGroupId, id, pop_size, lockdownFlag):

        sqs = boto3.client('sqs', region_name='eu-west-1')

        response = sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageGroupId=MessageGroupId,
            MessageDeduplicationId=MessageGroupId,
            MessageAttributes={
                'id': {
                    'DataType': 'Number',
                    'StringValue': id
                },
                'pop_size': {
                    'DataType': 'Number',
                    'StringValue': pop_size
                } ,
                'lockdownFlag': {
                    'DataType': 'String',
                    'StringValue': lockdownFlag
                }
            },
            MessageBody=(
                'simulation setting'
            )
        )
        try:
            pass
        except Exception as e:
            logger.error(
                'Error adding item to sqs: ' + (e.fmt if hasattr(e, 'fmt') else '') + ','.join(e.args))
            return 403
        status = response['ResponseMetadata']['HTTPStatusCode']
        if status == 200:
            if 'Attributes' in response:
                logger.error('Existing item updated to database.')
                return 409
            logger.error('New item added to database.')
        else:
            logger.error('Unknown error inserting item to database.')

        return status
