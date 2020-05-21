from django.db import models
import boto3
import os
import logging


SQS_QUEUE_URL = os.environ.get('SQS_QUEUE_URL')

logger = logging.getLogger(__name__)


class Leads(models.Model):

    def insert_lead(self, MessageGroupId, email,
                    pop_size, incubation_stage_duration, symptomatic_stage_duration,
                    min_recovery_duration, max_recovery_duration, mortality_prob,
                    healthcare_capacity,
                    amt_has_app, efficiency):
        # mean_number_of_transmission_events_per_hour,
        sqs = boto3.client('sqs', region_name='eu-west-1')

        response = sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageGroupId=MessageGroupId,
            MessageDeduplicationId=MessageGroupId,
            MessageAttributes={
                'email': {
                    'DataType': 'String',
                    'StringValue': email
                },
                'pop_size': {
                    'DataType': 'Number',
                    'StringValue': pop_size
                },
                'incubation_stage_duration': {
                    'DataType': 'Number',
                    'StringValue': incubation_stage_duration
                },
                'symptomatic_stage_duration': {
                    'DataType': 'Number',
                    'StringValue': symptomatic_stage_duration
                },
                'min_recovery_duration': {
                    'DataType': 'Number',
                    'StringValue': min_recovery_duration
                },
                'max_recovery_duration': {
                    'DataType': 'Number',
                    'StringValue': max_recovery_duration
                },
                'mortality_prob': {
                    'DataType': 'Number',
                    'StringValue': mortality_prob
                },
                # 'mean_number_of_transmission_events_per_hour': {
                #     'DataType': 'Number',
                #     'StringValue': mean_number_of_transmission_events_per_hour
                # },
                'healthcare_capacity': {
                    'DataType': 'Number',
                    'StringValue': healthcare_capacity
                },
                'amt_has_app': {
                    'DataType': 'Number',
                    'StringValue': amt_has_app
                },
                'efficiency': {
                    'DataType': 'Number',
                    'StringValue': efficiency
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
