# Cloud Computing Project Challenge (*Sprint 02*)

## Members:
- ariston.harianto.lim@est.fib.upc.edu
- yu-hsuan.chen@est.fib.upc.edu
- haonan.jin@est.fib.upc.edu
- yalei.li@est.fib.upc.edu
- manh.hung.nguyen@est.fib.upc.edu

**1. Lambda function for data generation**
# Data Generation by Lambda Function and S3
Based on the local data generation code and dataset desgin thinking(Report-Srpint01.md), we generate data by AWS Lambda function and store data in S3. Finally, we make some configuration and share S3 dataset to every teammembers.

![](gendata/Gendata.PNG)
In order to make the connection bewteen Lambda function and S3 and store dataset to S3, we need to configure S3 trigger.

![](gendata/Gendata2.PNG)
Run local gata genration code in lambda functions and make use of "hello world" format to test code.

![](gendata/Gendata3.PNG)
Configure permission in S3 by AWS email account thus making every team member share S3 dataset

### Explanation of dataset

Randomy generate following data:
```
1. ID: Phone number (Unique)
2. Gender: 1 Male, 0 Female
3. Age
4. Occupation: 1-50 tags of occupation. e.g. 23 = Software Engineer
5. Income: Based on the Spain average salary by standard normal distribution
6. District:The main districts in Barcelona 
   1=Ciutat Vella, 2=L'Eixample, 3=Sants-Montjuïc, 4=Gràcia, 5=Les Corts, 
   6=Sarri Sant Gervasi, 7=Horta Guinard, 8=Nou Barris, 9=Sant Andreu, 10=Sant Mart
7. Health Care Capacity: Control approaches.
   1=Business As Usual , 2=Reduced Interaction , 3=Lock-Down ,4=Self-Isolation
8. Health Status: 
   1=Healthy, 2=Infected , 3=Recovered , 4=Dead (Random generate with weight:50,25,20,5 respectly)
9. Location(Latitude,longitude) Barcelona 41.3851° N, 2.1734° E. with random generate digits follow 
10. Timestamp：Random generate timestem e.g 405201346 （date:month:year:hour:sec)
11. Notified: initially 0, if the notification sent then it will become 1
```

<p align="center"><img src="./images/Dataset_Screenshot.png" width="70%" height="70%" alt="sampledata"/></p>

**2. Lambda function for simulation**
