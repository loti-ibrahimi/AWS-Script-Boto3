#!/usr/bin/env python3

#------------------------------------------------------------------------------------#
# Student Name: Loti Ibrahimi | (20015453)
# Course: The Internet of Things
# Module: Dev Ops
# Lecturer: Jimmy McGibney

# Code references: Jimmy McGibney/Richard Frisby  DevOps labs (Boto3 tutorial/Assignment1-tips.pdf).

# Description: An AWS Boto Script where a number of tasks are being carried out.
# Python 3 Automated tasks - Process of:
# 1. Creating instance,
# 2. Launching instance,
# 3. Monitoring public-facing web server in the Amazon cloud.
#------------------------------------------------------------------------------------#


# Importing the required libraries to be used.
import boto3
import time
from datetime import datetime, timedelta
import subprocess

# Global variable to access EC2 functions provided by Boto3;
ec2 = boto3.resource('ec2')
# Global variable to access S3 functions provided by Boto3;
s3 = boto3.resource("s3")
# Global variable to access Cloudwatch functions provided by Boto3:
cloudwatch = boto3.resource('cloudwatch')


# Creates and configures a AWS EC2 t2.micro instance.
#===========================================================#
'''
Following arguments to be used by the instance:
- Security Group ID from user's AWS account
- SSH private pem key located in the same directory as this file
'''
def create_instance(inst_tag, sg, key_name):
    print('-----------------------------------------------')
    print('Creating new instance with the following params: \n - Tag: ' + inst_tag + ' \n - Key: ' + key_name + ' \n - Security Group: ' + sg)
    print('-----------------------------------------------')
    try:
        new_instance = ec2.create_instances(
            # [Tags] Reference: Boto3 Documentation.
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': inst_tag
                        },
                    ]
                },
            ],
            ImageId = 'ami-0ce71448843cb18a1',
            MinCount = 1,
            MaxCount = 1,
            InstanceType = 't2.micro',
            SecurityGroupIds = [sg], # Security group the instance will abide to.
            KeyName = key_name, # Private key to be used to launch the instance.
            # Apply patches & install web server.
            UserData='''#!/bin/bash
                    yum install httpd -y
                    systemctl enable httpd
                    service httpd start''',  # to check all ok
        )

        print('New instance created (ID: ' + new_instance[0].id + ').')

        return new_instance

    except Exception as error:
        print('An error occured while trying to create a new instance: ' + error)


# Create a Bucket in S3 (Asks for user input - Bucket name)
#===========================================================#
def create_bucket(bucket_name):
    try:
        # Create a Bucket in the EU West location
        new_bucket = s3.create_bucket(Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
        print(new_bucket)

        return new_bucket

    except Exception as error:
        print(error + 'Please try again.. (make sure Bucket name is unique!)')


# List all Buckets incl. all associated content.
#===========================================================#
def list_buckets():
    s3 = boto3.resource('s3')

    #List bucket each bucket by name
    for bucket in s3.buckets.all():
        print(bucket.name)
        print('')

        #List all Bucket contents
        try:
            for item in bucket.objects.all():
                print ('\t%s' % item.key)
        except Exception as error:
            print(error)


# Download image locally.
#===========================================================#
def fetch_file(file_name):
    cmd = 'curl http://devops.witdemo.net/' + file_name + ' > ' + file_name

    try:
        subprocess.run(cmd, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(15)
        # Throw an error if not found.
        checkFile = open(file_name)

    except Exception as error:
        print(error + 'Failed to fetch file.. Please try again.')


# Upload local file to specified bucket.
#===========================================================#
def fill_bucket(file_name, bucket_name):
    try:
        print('Adding ' + file_name + ' to the following bucket: ' + bucket_name)

        # Add file to aws bucket and make it public read.
        response = s3.Object(bucket_name, file_name).put(Body=open(file_name, 'rb'), ACL = ('public-read'))
        return response

    except Exception as error:
        print(error + 'Failed to upload file to bucket..')


# Create index.html locally & copy it to Web Server.
#===========================================================#
def create_index_page(key_name, instance_public_ip, file_name, bucket_name):
    try:
        # Commands
        # 1. Constructing index.html line-by-line.
        cmd = 'echo "<html>" > index.html'
        cmd1 = 'echo "<br> <b> Loti Ibrahimi | 20015453 </b>" >> index.html'
        cmd2 = 'echo "<br> Image display: <br>" >> index.html'
        cmd3 = 'echo "<img src="https://' + bucket_name + '.s3-eu-west-1.amazonaws.com/' + file_name + '">" >> index.html'

        print('Creating a new file: index.html')
        subprocess.run(cmd, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5)
        subprocess.run(cmd1, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(cmd2, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(cmd3, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print('~---------------------------~')
        print('New File Created: index.html')

        print('')
        print('Copying "index.html" to Web Server..')
        time.sleep(3)
        # 2. Copying index.html to home directory of instance.
        cmd4 = 'scp -o StrictHostKeyChecking=no -i ' + key_name + '.pem index.html ec2-user@' + instance_public_ip + ':.'
        # 3. Copy from home directory of instance to right path.
        cmd5 = 'ssh -i ' + key_name + '.pem ec2-user@' + instance_public_ip + ' "sudo cp index.html /var/www/html"'
        subprocess.run(cmd4, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(cmd5, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    except Exception as error:
        print(error)


# Metrics Monitoring using CloudWatch - CPU Utilisation + Incoming Network bytes
#=================================================================================#
def monitor_metrics(instance_id):
    # Force increased CPU Utilisation for test monitoring purposes.    (Causing problems - crash issues)
    # cmd = 'ssh -i ' + key_name + '.pem ec2-user@' + instance_public_ip
    # cmd1 = 'while true; do x=0; done'
    # subprocess.run(cmd, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # subprocess.run(cmd1, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Metric 1. The percentage of allocated EC2 compute units that are currently in use on the instance.
    # Reference: Script to monitor CPU Utilisation in CloudWatch using boto (moodle)
    print('')
    print('Reading CPU utilisation..')
    time.sleep(60)

    cpu_metric_iterator = cloudwatch.metrics.filter(Namespace='AWS/EC2',
                                               MetricName='CPUUtilization',
                                               Dimensions=[{'Name':'InstanceId', 'Value': instance_id}])
    for metric in cpu_metric_iterator:
        response = metric.get_statistics(StartTime=datetime.now() - timedelta(minutes=65),     # 5 minutes ago
                                         EndTime=datetime.now() - timedelta(minutes=60),       # now
                                         Period=300,                                           # 5 minute intervals
                                         Statistics=['Average'])
        print("~ Average CPU utilisation (%): ", response['Datapoints'][0]['Average'])


    # Metric 2. Determine the number of bytes received on all network interfaces by the instance.
    print('')
    print('Reading incoming Network bytes..')
    time.sleep(60)

    networkIn_metric_iterator = cloudwatch.metrics.filter(Namespace='AWS/EC2',
                                               MetricName='NetworkIn',
                                               Dimensions=[{'Name':'InstanceId', 'Value': instance_id}])
    for metric in networkIn_metric_iterator:
        response = metric.get_statistics(StartTime=datetime.now() - timedelta(minutes=65),     # 5 minutes ago
                                         EndTime=datetime.now() - timedelta(minutes=60),       # now
                                         Period=300,                                           # 5 minute intervals
                                         Statistics=['Average'])
        print("~ Average Network Bytes: ", response['Datapoints'][0]['Average'])

# ------------------------------------------------------------------------------------------------- #

def main():
    '''
        Main function to start-up the program.
        1) Creates a new instance.
        2) Create a new bucket.
        3) Fetch file/image & Upload to existing bucket.
        4) List Bucket & Bucket Contents.
        5) Create index.html file locally & copy to webserver.
        6) Cloudwatch Monitoring.
    '''
    print('')
    print('This python script will create an AWS EC2 web server & display some static content')
    print('')
    print('+++++++++++++++++++++++++++++++++++++')
    print('Parameter References')
    print('* Public Key: loti-key \n* Security Group ID: sg-07cd9856bdbdfa855 \n* File Name: image.jpg')
    print('+++++++++++++++++++++++++++++++++++++')
    print('')

    # 1.New Instance
    #==================================================================================
    # Take in user input for Instance Name - used in the name_tag field below.
    inst_tag=input('Enter a name tag for your Instance: ')
    sg = input('Please provide security group id: ')
    key_name = input('Please provide public key (Omit the file extension): ')
    instance = create_instance(inst_tag, sg, key_name)

    print('Sleeping the program for 60 seconds to allow the instance to be configured..')
    time.sleep(60)
    instance[0].reload()
    print('60 seconds passed.')
    instance_public_ip = instance[0].public_ip_address
    print('Instance Public IP Address: ' + instance_public_ip)
    instance_id = instance[0].id
    print('Instance ID: ' + instance_id)
    # Enabling detailed monitoring.
    instance[0].monitor()


    # 2.New Bucket
    #==================================================================================
    print('')
    bucket_name = input('Please enter a new Bucket name: ')
    bucket = create_bucket(bucket_name)


    # 3.File to be Fetched & Uploaded
    #==================================================================================
    print('')
    file_name = input('Please provide file to be uploaded (e.g. image.jpg): ')
    # Fetch File
    print('Fetching file, please wait..')
    fetch_file(file_name)
    # Upload file to Bucket
    print('')
    fill_bucket(file_name, bucket_name)


    # 4. List Buckets & their contents
    #==================================================================================
    print('')
    print('List of Buckets & Content')
    print('--------------------------')
    list_buckets()
    print('--------------------------')


    # 5. Create index.html file locally, then copy it to instance web server.
    #==================================================================================
    print('')
    create_index_page(key_name, instance_public_ip, file_name, bucket_name)
    print('')
    print('View Web Page here: http://' + instance_public_ip)
    print('')


    # 6. CloudWatch Monitoring
    #==================================================================================
    print('')
    print('CloudWatch Monitoring')
    print('~-----------------------------------------------~')
    print('Please wait, gathering Instance metrics.')
    monitor_metrics(instance_id)


    #=============================== End of Program ===================================
    print('')
    input('Press any key to terminate the instance.')
    instance[0].terminate()

if __name__ == '__main__':
  main()
