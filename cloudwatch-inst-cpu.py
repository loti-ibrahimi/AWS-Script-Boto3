#!/usr/bin/python3

import boto3
from datetime import datetime, timedelta

cloudwatch = boto3.resource('cloudwatch')

instid = input("Please enter instance ID: ")

metric_iterator = cloudwatch.metrics.filter(Namespace='AWS/EC2', 
                                           MetricName='CPUUtilization', 
                                           Dimensions=[{'Name':'InstanceId', 'Value': instid}])

for metric in metric_iterator:
    response = metric.get_statistics(StartTime=datetime.now() - timedelta(minutes=65),     # 5 minutes ago
                                     EndTime=datetime.now() - timedelta(minutes=60),       # now
                                     Period=300,                                           # 5 minute intervals
                                     Statistics=['Average'])
    print ("Average CPU utilisation:", response['Datapoints'][0]['Average'])
#   print (response)   # for debugging only

