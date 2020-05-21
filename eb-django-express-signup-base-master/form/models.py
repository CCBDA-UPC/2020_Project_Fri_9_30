from django.db import models
import boto3
import os
import logging


SQS_QUEUE_URL = os.environ.get('SQS_QUEUE_URL')

logger = logging.getLogger(__name__)


class Leads(models.Model):

    def insert_lead(self, email,
                    pop_size, incubation_stage_duration, symptomatic_stage_duration,
                    min_fighting_duration, max_fighting_duration, mortality_probability,
                    mean_number_of_transmission_events_per_hour,
                    app_installed_probability, contact_tracing_compliance):
        # mean_number_of_transmission_events_per_hour,
        userID = 'simulation'
        # userID = str(np.random.randint(1,1000))
        sqs = boto3.client('sqs', region_name='eu-west-1')

        response = sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageGroupId=userID,
            MessageDeduplicationId=userID,
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
                'min_fighting_duration': {
                    'DataType': 'Number',
                    'StringValue': min_fighting_duration
                },
                'max_fighting_duration': {
                    'DataType': 'Number',
                    'StringValue': max_fighting_duration
                },
                'mortality_probability': {
                    'DataType': 'Number',
                    'StringValue': mortality_probability
                },
                'mean_number_of_transmission_events_per_hour': {
                    'DataType': 'Number',
                    'StringValue': mean_number_of_transmission_events_per_hour
                },
                'app_installed_probability': {
                    'DataType': 'Number',
                    'StringValue': app_installed_probability
                },
                'contact_tracing_compliance': {
                    'DataType': 'Number',
                    'StringValue': contact_tracing_compliance
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
