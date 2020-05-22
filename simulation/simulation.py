import datetime
import json
import os
import sys
import time
from io import StringIO
from random import randint

import boto3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from config import Configuration, config_error
from environment import build_hospital
from infection import find_nearby, infect, recover_or_die, compute_mortality, \
    healthcare_infection_correction
from motion import update_positions, out_of_bounds, update_randoms, \
    get_motion_parameters
from path_planning import go_to_location, set_destination, check_at_destination, \
    keep_at_destination, reset_destinations
from population import initialize_population, initialize_destination_matrix, \
    set_destination_bounds, save_data, save_population, Population_trackers
from visualiser import build_fig, draw_tstep, set_style
from ses import sent


# set seed for reproducibility
# np.random.seed(100)

def differences_calculation(sim1, sim2):
    message1 = ""
    if len(sim2.population[sim2.population[:, 6] == 3]) < len(sim1.population[sim1.population[:, 6] == 3]):
        message1 += "\nThe number of deaths decreases by: " + \
                    str(round(((len(sim1.population[sim1.population[:, 6] == 3]) - len(
                        sim2.population[sim2.population[:, 6] == 3]))
                               / (len(sim1.population[sim1.population[:, 6] == 3])+1) * 100), 2)) + "%"
    else:
        message1 += "\nThe number of deaths increases by: " + \
                    str(round(((len(sim2.population[sim2.population[:, 6] == 3]) - len(
                        sim1.population[sim1.population[:, 6] == 3]))
                               / (len(sim1.population[sim1.population[:, 6] == 3])+1) * 100), 2)) + "%"

    message2 = ""
    if len(sim2.population[sim2.population[:, 6] == 2]) < len(sim1.population[sim1.population[:, 6] == 2]):
        message2 += "\nThe number of infected people decreases by: " + \
                    str(round(((len(sim1.population[sim1.population[:, 6] == 2]) - len(
                        sim2.population[sim2.population[:, 6] == 2])+1)
                               / (len(sim1.population[sim1.population[:, 6] == 2])+1) * 100), 2)) + "%"
    else:
        message2 += "\nThe number of infected people increases by: " + \
                    str(round(((len(sim2.population[sim2.population[:, 6] == 2]) - len(
                        sim1.population[sim1.population[:, 6] == 2]))
                               / (len(sim1.population[sim1.population[:, 6] == 2])+1) * 100), 2)) + "%"

    return message1,message2

def send_results(sim1, sim2):
    message1, message2 = differences_calculation(sim1,sim2)

    client = boto3.client('s3', region_name='eu-west-1')
    # Log structure: dayNumber, healthy, infected, immune, in treatment, dead

    # ---------- Plot a graph for the simulation without contact tracing ----------- #
    TESTDATA = StringIO("""Day;healthy;infected;immune;in treatment;dead
        %s
        """ % sim1.log)
    df = pd.read_csv(TESTDATA, sep=";")
    print(df)

    plt.clf()
    plt.cla()
    plt.close()

    ax = plt.gca()
    df.plot(kind='line', x='Day', y='healthy', color='orange', ax=ax)
    df.plot(kind='line', x='Day', y='infected', color='lightcoral', ax=ax)
    df.plot(kind='line', x='Day', y='immune', color='powderblue', ax=ax)
    df.plot(kind='line', x='Day', y='in treatment', color='darkseagreen', ax=ax)
    df.plot(kind='line', x='Day', y='dead', color='darkgrey', ax=ax)

    plt.savefig('result/no-contact-tracing.png')  # simulation result

    plt.clf()
    plt.cla()
    plt.close()

    # ---------- Plot a graph for the simulation with contact tracing ----------- #
    TESTDATA2 = StringIO("""Day;healthy;infected;immune;in treatment;dead
            %s
            """ % sim2.log)
    df2 = pd.read_csv(TESTDATA2, sep=";")
    print(df2)

    plt.clf()
    plt.cla()
    plt.close()

    ax2 = plt.gca()
    df2.plot(kind='line', x='Day', y='healthy', color='orange', ax=ax2)
    df2.plot(kind='line', x='Day', y='infected', color='lightcoral', ax=ax2)
    df2.plot(kind='line', x='Day', y='immune', color='powderblue', ax=ax2)
    df2.plot(kind='line', x='Day', y='in treatment', color='darkseagreen', ax=ax2)
    df2.plot(kind='line', x='Day', y='dead', color='darkgrey', ax=ax2)

    plt.savefig('result/contact-tracing.png')  # simulation result

    plt.clf()
    plt.cla()
    plt.close()

    # ---------- Upload images ----------- #

    ts = datetime.datetime.now().timestamp()

    noContactTracing = 'no-contact-tracing-' + str(ts) + '.png'
    contacttracing = 'contact-tracing-' + str(ts) + '.png'

    client.upload_file('result/no-contact-tracing.png', 'simulationresult2', noContactTracing)
    client.upload_file('result/contact-tracing.png', 'simulationresult2', contacttracing)

    # ---------- Send an email ----------- #
    sent(noContactTracing, contacttracing, sim1.Config.pop_size, "True", sim1.Config.email, message1, message2)

class Simulation():

    # TODO: if lockdown or otherwise stopped: destination -1 means no motion
    def __init__(self, config):
        # load default config data
        self.Config = config
        self.frame = 0

        self.log = ""
        # self.log.append(str(self.Config.pop_size) + "\n")  # first line is the population

        # initialize default population
        self.population_init()

        self.pop_tracker = Population_trackers()

        # initalise destinations vector
        self.destinations = initialize_destination_matrix(self.Config.pop_size, 1)

        # self.fig, self.spec, self.ax1, self.ax2 = build_fig(self.Config)

        # set_style(self.Config)

    def population_init(self):
        '''(re-)initializes population'''
        self.population = initialize_population(self.Config, self.Config.mean_age,
                                                self.Config.max_age, self.Config.xbounds,
                                                self.Config.ybounds)

    def tstep(self):
        '''
        takes a time step in the simulation
        '''

        # check destinations if active
        # define motion vectors if destinations active and not everybody is at destination
        active_dests = len(self.population[self.population[:, 11] != 0])  # look op this only once

        if active_dests > 0 and len(self.population[self.population[:, 12] == 0]) > 0:
            self.population = set_destination(self.population, self.destinations)
            self.population = check_at_destination(self.population, self.destinations,
                                                   wander_factor=self.Config.wander_factor_dest,
                                                   speed=self.Config.speed)

        if active_dests > 0 and len(self.population[self.population[:, 12] == 1]) > 0:
            # keep them at destination
            self.population = keep_at_destination(self.population, self.destinations,
                                                  self.Config.wander_factor)

        # out of bounds
        # define bounds arrays, excluding those who are marked as having a custom destination
        if len(self.population[:, 11] == 0) > 0:
            _xbounds = np.array([[self.Config.xbounds[0] + 0.02, self.Config.xbounds[1] - 0.02]] * len(
                self.population[self.population[:, 11] == 0]))
            _ybounds = np.array([[self.Config.ybounds[0] + 0.02, self.Config.ybounds[1] - 0.02]] * len(
                self.population[self.population[:, 11] == 0]))
            self.population[self.population[:, 11] == 0] = out_of_bounds(self.population[self.population[:, 11] == 0],
                                                                         _xbounds, _ybounds)

        # set randoms
        if self.Config.lockdown:
            if len(self.pop_tracker.infectious) == 0:
                mx = 0
            else:
                mx = np.max(self.pop_tracker.infectious)

            if len(self.population[self.population[:, 6] == 1]) >= len(
                    self.population) * self.Config.lockdown_percentage or \
                    mx >= (len(self.population) * self.Config.lockdown_percentage):
                # reduce speed of all members of society
                self.population[:, 5] = np.clip(self.population[:, 5], a_min=None, a_max=0.001)
                # set speeds of complying people to 0
                self.population[:, 5][self.Config.lockdown_vector == 0] = 0
            else:
                # update randoms
                self.population = update_randoms(self.population, self.Config.pop_size, self.Config.speed)
        else:
            # update randoms
            self.population = update_randoms(self.population, self.Config.pop_size, self.Config.speed)

        # for dead ones: set speed and heading to 0
        self.population[:, 3:5][self.population[:, 6] == 3] = 0

        # update positions
        self.population = update_positions(self.population)

        # find new infections
        self.population, self.destinations = infect(self.population, self.Config, self.frame,
                                                    send_to_location = self.Config.self_isolate | self.Config.contact_tracing,
                                                    location_bounds = self.Config.isolation_bounds,
                                                    destinations = self.destinations,
                                                    location_no = 1,
                                                    location_odds = max(self.Config.self_isolate_proportion, self.Config.app_installed_probability))

        # recover and die
        self.population = recover_or_die(self.population, self.frame, self.Config)

        # send cured back to population if self isolation active
        # perhaps put in recover or die class
        # send cured back to population
        self.population[:, 11][self.population[:, 6] == 2] = 0

        # update population statistics
        self.pop_tracker.update_counts(self.population)

        # visualise
        # if self.Config.visualise:
        #     draw_tstep(self.Config, self.population, self.pop_tracker, self.frame,
        #                self.fig, self.spec, self.ax1, self.ax2)

        # report stuff to console
        # sys.stdout.write('\r')
        # sys.stdout.write('%i: healthy: %i, infected: %i, immune: %i, in treatment: %i, \
        # dead: %i, of total: %i' % (self.frame, self.pop_tracker.susceptible[-1], self.pop_tracker.infectious[-1],
        #                            self.pop_tracker.recovered[-1], len(self.population[self.population[:, 10] == 1]),
        #                            self.pop_tracker.fatalities[-1], self.Config.pop_size))
        self.log = self.log + (str(self.frame) + ";"
                               + str(self.pop_tracker.susceptible[-1]) + ";"
                               + str(self.pop_tracker.infectious[-1]) + ";"
                               + str(self.pop_tracker.recovered[-1]) + ";"
                               + str(len(self.population[self.population[:, 10] == 1])) + ";"
                               + str(self.pop_tracker.fatalities[-1]) + "\n")
        # change the log content
        # save popdata if required
        if self.Config.save_pop and (self.frame % self.Config.save_pop_freq) == 0:
            save_population(self.population, self.frame, self.Config.save_pop_folder)
        # run callback
        self.callback()

        # update frame
        self.frame += 1


    def callback(self):
        '''placeholder function that can be overwritten.

        By ovewriting this method any custom behaviour can be implemented.
        The method is called after every simulation timestep.
        '''

        if self.frame == 50:
            print('\ninfecting person')
            self.population[0][6] = 1
            self.population[0][8] = 50
            self.population[0][10] = 1

      # pass all the variable that will be in the mail

    def run(self):
        '''run simulation'''

        i = 0

        while i < self.Config.simulation_steps:
            try:
                self.tstep()
            except KeyboardInterrupt:
                print('\nCTRL-C caught, exiting')
                sys.exit(1)

            # check whether to end if no infecious persons remain.
            # check if self.frame is above some threshold to prevent early breaking when simulation
            # starts initially with no infections.
            if self.Config.endif_no_infections and self.frame >= 500:
                if len(self.population[(self.population[:, 6] == 1) |
                                       (self.population[:, 6] == 4)]) == 0:
                    i = self.Config.simulation_steps

        if self.Config.save_data:
            save_data(self.population, self.pop_tracker)

        # report outcomes
        print('\n-----stopping-----\n')
        print('total timesteps taken: %i' % self.frame)
        print('total dead: %i' % len(self.population[self.population[:, 6] == 3]))
        print('total recovered: %i' % len(self.population[self.population[:, 6] == 2]))
        print('total infected: %i' % len(self.population[self.population[:, 6] == 1]))
        print('total infectious: %i' % len(self.population[(self.population[:, 6] == 1) |
                                                           (self.population[:, 6] == 4)]))
        print('total unaffected: %i' % len(self.population[self.population[:, 6] == 0]))

def run_locally():
    # Config
    config1 = Configuration()
    config1.contact_tracing = False
    config1.pop_size = 2000
    config1.email = "hungnm.vnu@gmail.com"

    config2 = Configuration()
    config2.contact_tracing = True
    config2.set_contact_tracing(app_installed_probability=0, contact_tracing_compliance=1, symptomatic_stage_duration=48, incubation_stage_duration=336)
    config2.pop_size = 2000
    config2.email = "hungnm.vnu@gmail.com"

    # initialize
    sim1 = Simulation(config1)
    sim2 = Simulation(config2)

    # Run
    sim2.run()
    sim1.run()

    # Send emails
    send_results(sim1, sim2)

def pull_jobs():
    sqs = boto3.client('sqs', region_name='eu-west-1')
    queue_url = 'https://sqs.eu-west-1.amazonaws.com/355914966584/jobs.fifo'
    while True:
        try:
            # Get 1 message from SQS
            response = sqs.receive_message(
                QueueUrl=queue_url,
                AttributeNames=['SentTimestamp'],
                MaxNumberOfMessages=1,
                MessageAttributeNames=['All'],
                VisibilityTimeout=30,
                WaitTimeSeconds=0
            )

            # Delete the received message
            message = response['Messages'][0]
            receipt_handle = message['ReceiptHandle']
            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)

            # Parse the message to get parameters
            parameters = message['MessageAttributes']
            print(parameters)

            # Config
            config1 = Configuration()
            config1.contact_tracing = False
            config1.pop_size = int(parameters['pop_size']['StringValue'])  # Set population size
            config1.email = parameters['email']['StringValue']  # Set email

            config2 = Configuration()
            config2.contact_tracing = True
            config2.set_contact_tracing(app_installed_probability=float(parameters['app_installed_probability']['StringValue']),
                                        contact_tracing_compliance=float(parameters['contact_tracing_compliance']['StringValue']),
                                        symptomatic_stage_duration=int(parameters['symptomatic_stage_duration']['StringValue']),
                                        incubation_stage_duration=int(parameters['incubation_stage_duration']['StringValue']))
            config2.pop_size = int(parameters['pop_size']['StringValue'])  # Set population size
            config2.email = parameters['email']['StringValue']  # Set email


            # initialize
            sim1 = Simulation(config1)
            sim2 = Simulation(config2)

            # Run
            sim1.run()
            sim2.run()

            # Send emails
            send_results(sim1, sim2)

        except Exception as e:
            print(e)
            print("Exception occurs! => Getting a new job...")
            time.sleep(10)  ## Check jobs every 10 secs


if __name__ == '__main__':
    # run_locally()  ## test simulation locally
    pull_jobs() ## start pulling jobs
