# Cloud Computing Project Challenge (*Draft Report*)

## Members:
- ariston.harianto.lim@est.fib.upc.edu
- yu-hsuan.chen@est.fib.upc.edu
- haonan.jin@est.fib.upc.edu
- yalei.li@est.fib.upc.edu
- manh.hung.nguyen@est.fib.upc.edu

## Functionalities

**1. Simulation of people's behavior and infection spread**

Basically, people in a particular area are represented by dots with different colors which indicate their health status. The coordinates of these dots depend on the locations of people and how they are moving based on individual daily agenda. These following factors can be specified by users via parameters.
- People: professions, daily agenda, transportation,...
- Infection characteristics: transmission rate, duration of the incubation stage, mortality percentage,...

<p align="center">
<img src="/images/simulation.png" alt="drawing" width="500"/>
</p>

**2. Simulation with Contact Tracing System based on the proposal from Apple and Google**

We are going to implement a simplified Contact Tracing System to keep track of people who have been recently in contact with an infected person. We then take some measures, for example, self-quarantined and specify it in the simulation to see the changes in infection rate whether it goes down or not.

<p align="center">
<img src="/images/ContactTracing.png" alt="drawing" width="300"/>
</p>


## Scopes

This project aims at developing infection simulating and contact tracing services to evaluate and decide which measures should be taken to stop people from getting infected with coronavirus.  

- Deliverables: Infection Simulating and contact tracing service
- Customers & Stakeholders: Government, Citizens, ...
- Duration: 5 weeks
- Development methods: Agile

## Services and Resources
### Elastic stack ( Kibana & Elasticsearch)
#### For simulation

We are thinking about using **Kibana** to help us present the simulation result as, according to the official document, there is a GIS visualization service that we can implement. However, after research, we realized that it is usually used to visualize in a bigger scope. We are not sure if Kibana is the best choice for us because we focus more on how people move within the smaller granularity (regions, sublocations). 


However, we can still use Kibana if we want to fulfill the following functions.

1. To visualize how infected speed and recovered rate changes before and after the Apple solution or other not geo-related visualization. Then Kibana allows visualizing the data in various expressive ways.![Kibana Visualization](https://img-blog.csdnimg.cn/2019012001182146.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3Bvd2VyY2NuYQ==,size_16,color_FFFFFF,t_70)

2. Compare the result between defined regions according to the density of the different sublocation( commercial area and residential area etc…). The example below is using Coordinate heatmaps in the Kibana to visualize the crime rate in different areas and with Data filtering we can see the result in a different perspective, for instance, different time, date, weekday and weekend or even more delicate query according to the data we provided) (https://blog.mimacom.com/kibana-heatmap/) ![Heatmap](https://blog.mimacom.com/en/media/71a0c43d66a68048321ff1624fe7ebd8/2018-11-20-vancouver-vehicle-theft.png)

    For more diverse visualization, someone did a [COVID-19 update](https://covid.alphasec.eu/app/kibana#/dashboards?_g=(refreshInterval:(pause:!t,value:0),time:(from:now-40d,to:now)) )in Spain.
Some [interesting website](https://c19simulation.com/) that sort of related to our topic.

#### For prototype of the Google Apple project
**Elasticsearch** offers the spatial query; for example, it can query geolocation according to the user’s location and find the nearby pharmacy, hospital. 

* **Geo_distance**: we can set each individual as a center of the circle and draw a circle with the radius of potentially infected distance and find all people located within the circle.


* **Using in our project**: Let’s assume that people who stay with each other in the closet enough distance that around 10 mins can get infected. We query every 10 minutes and see if there are any points( individual) returned in the two queries. If so we can add them as a pair into our database. And we connecting to AWS service in the next bullet point


* **Elasticsearch can work with AWS**

##### ElasticBeanstalk 
Deploy ELK stack on an **EC2 instance** belonging to an ElasticBeanstalk environment (e.g. Django file) : we can set each individual as a center of the circle and draw a circle with the radius of potentially infected distance and find all people located within the circle. Further deployment configuration please refer to next topic Elastic Beanstalk for deployment configuration.
[Official Documentations](https://discuss.elastic.co/t/connection-refused-for-elasticsearch-and-kibana-on-aws-elastic-beanstalk/187836)

##### DynamoDB
For example, A and B sit right next to each other than 10 minutes, and their phone is querying every 10 minutes. And if when 2 phones finds out they spend more than time minutes together, the pair (A_identifier, B_identifer) will be stored in the DynamoDB.

Ps. Elasticsearch can integrate with DynamoDB and we can take it into consideration as we need mass writing operation to store the pair but the database of elasticsearch is great for less writes and more reads. 
[Relevant Instructions](https://www.youtube.com/watch?v=WXmghnE1_vU)

##### DynamoDB Stream
Amazon DynamoDB is integrated with **AWS Lambda** so we can create triggers that automatically respond to events in DynamoDB Streams. With triggers, we can build applications that react to data modifications in DynamoDB tables.
In our case, if one person is confirmed infected then the lambda function can be trigger and we can send the notification to those who spend more than 10 mins with the infected person.  
[Relevant Instructions](https://www.youtube.com/watch?v=vHVUuV2ihN4)

##### Lambda Function
After set up the lambda configuration and function to call ElasticSearch service, so we can write an elasticsearch query in the lambda function and read the ElasticSearch query result (Decoded from JSON format and will be saved in the result variable.).
[Relevant Instructions](https://blogs.tensult.com/2020/01/01/aws-lambda-to-perform-various-tasks-in-elasticsearch/)

### Elastic Beanstalk for deployment configuration

Elastic Beanstalk can offer plenty of integrity platforms or services, which can improve the efficiency of our work. We make use of Elastic Beanstalk throughout the whole tasks including simulation and  prototype of the Google Apple project because of its universality, convenience and scalability.

#### Advantage

Compared to local API, Amazon Elastic Beanstalk reduces management complexity without restricting choice or control. All you need to do is upload the application and Elastic Beanstalk will automatically handle deployment details about capacity provisioning, load balancing, scaling, and application health monitoring.It supports applications developed in Go, Java, .NET, Node.js, PHP, Python, and Ruby. When you deploy an application, Elastic Beanstalk builds the selected supported platform version and provision one or more AWS resources (such as Amazon EC2 instances) to run your application.

#### How to use in our tasks
##### Amazon Elastic Compute Cloud (Amazon EC2) 

Basically, EC2 provide virtual computing environment(the instance), a pre-configured template, or Amazon Machine Images (AMI), which encapsulates the components required by the server (including operating system and other software) and various configurations of instance CPU, memory, storage and networking functions, that is, instance type. In our project, the two tasks can be implemented easily and efficiently with the help of EC2. For simulation and prototype, we just need to figure out the simulation or prototype code ,how to visualize our simulation result or how to design Contact tracing method, we do not think too much on low-level design, memory space and runtime.

##### Amazon EC2 Auto Scaling 

During the whole process of our simulation and prototype design stage, Amazon EC2 Auto Scaling helps us ensure that we have the right amount of Amazon EC2 instances to handle our application load. When we are busy with the simulation model with large amount dataset, we can create a collection of EC2 instances called Auto Scaling groups as well as specify the minimum number of instances in each Auto Scaling group, which can reduce the occurrence of code error and thus improve the efficiency of our code.

##### Elastic Load Balancing 

A load balancer can distribute workload across multiple computing resources, such as virtual servers. Using a load balancer can improve the availability and fault tolerance of the application. For example, the prototype of the Google Apple project needs to trace potentially infected people and infected people and take measures to send notification to the potential infected people based on the changing data and geolocation function. Therefore, it is necessary for us to pay attention to health check monitoring so as to let the load balancer only sends requests to healthy requests. Also, we can also We can also transfer encryption and decryption work to the load balancer so that your computing resources can focus on their main work.

##### Amazon Simple Storage Service (Amazon S3)	
Needless to say, the storage and share function of Amazon S3 could be fully used, which can easily manage and update shared datasets, files and code using Amazon S3 access points. For example, Every time members can update their code and part code result stored in Amazon S3, which will implement or check other time member contributions in Amazon service and don’t need to connect or upload something again from the local computer.

##### Elastic Beanstalk Python platform

The reason why we use this platform is easy to understand. The Elastic Beanstalk Python platform can improve our collaborative time-work efficiency when we design or test the code when we figure out the problems of simulation and prototype. 
[Official Deployment Details](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-apps.html)

##### Elastic Beanstalk Docker platform

Elastic Beanstalk supports the deployment of web applications from Docker containers. Using Docker containers, you can define your own runtime environment. You can choose your platform, programming language, and any application dependencies that are not supported by other platforms (such as package managers or tools). By Docker, we can automatically handle details of capacity configuration, load balancing, scaling, and application health monitoring when we design the simulation and prototype python project. 
[Official Documentations](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create_deploy_docker.html)

[Biological neuronal network simulations with Python](https://hub.docker.com/r/neuralensemble/simulation)

### Amazon CloudFront
#### For prototype

Given the project is initiated by Google and Apple, we believe it is necessary to use cloud distributed networks to empower the service for global use. Therefore, Amazon CloudFront is considered to be deployed if we will develop the prototype into a globally accessible web-based application. 

Using CloudFront can significantly improve the access delay caused by distribution, bandwidth, and server performance. It is especially suitable for our prototype as a live broadcasting service scenario. Global users can obtain the required content nearby without the network congestion, and the response speed and success rate of users visiting the website are also improved.

To be more specific, we plan to deploy the architecture of Amazon CloudFront for dynamic websites (shown below). It is proposed to use EC2 and Global Server Load Balancer (GSBL) to be the source of the CloudFront (where we create an EC2 first, and add a GSLB layer on the top) [1](https://blog.csdn.net/keithyau/article/details/49509187). 
 ![Potential Architecture](https://www.google.com/url?sa=i&url=https%3A%2F%2Faws.amazon.com%2Fblogs%2Faws%2Famazon-cloudfront-support-for-dynamic-content%2F&psig=AOvVaw2tnZ0x2IxSESOXz0g7BrR2&ust=1587766136606000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCLiE2_bH_-gCFQAAAAAdAAAAABAk)
 
### Amazon Simple Notification Service (SNS) 
#### For prototype
One significant function of the prototype is to actively notify people when their close contacts change health status to confirmed cases. Therefore, it is essential to quickly and effectively send people notifications. Amazon SNS provides a simple web service interface and browser-based management console to easily set up, run and send message notifications and push services from the cloud. Taking advantage of SNS, we can achieve high scalability, flexibility, cost-effectiveness and real-timeness for publishing messages from our application. Here, several approaches are considered for different development cases.
1. SNS + Notification
    1. SMS
    2. Email
2. SNS + Mobile Push
    1. SNS + Google Firebase Cloud Messaging (FCM)
    2. SNS + Apple PushNotification Service (APNS)

![Potential Structure](https://www.google.com/url?sa=i&url=https%3A%2F%2Fmedium.com%2F%40amisree%2Fauthor-arafath-misree-cc5da85888ef&psig=AOvVaw20HUGuZFc60CM9piFNRGmR&ust=1587756135340000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCNj00Laj_-gCFQAAAAAdAAAAABAD)

The final notification sending method depends on the detailed realization of the prototype, and what information people are willing to provide. If phone numbers or email are able to be obtained, we can easily send SMS and emails, and also use them as our key to the database. Ideally, the partnership of Apple and Google should be able to access some of their platform endpoints, which enables us to connect SNS with these push notification services. [2]

### Other Potential Resources
Our options service that we may use in the lab based on our future plan. **Amazon Redshift** and **Amazon EMR** are regarded as data warehouses and stronger data science integrated services facing large amounts of data streams.  We also need the basic **Amazon Relational Database** to support our lab if necessary.

## Tasks Planning
