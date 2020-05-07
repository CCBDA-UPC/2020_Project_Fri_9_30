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

**2. Lambda function for simulation**
