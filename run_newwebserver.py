#------------------------------------------------------------- -----------------------#

# Student Name: Loti Ibrahimi | (20015453)
# Course: The Internet of Things (Year 3)
# Module: Dev Ops
# Lecturer: Jimmy McGibney

# Code references: Jimmy McGibney/Richard Frisby  DevOps labs (Boto3 tutorial/Assignment1-tips.pdf etc). 

# Description: An AWS Boto Script where a number of tasks are being carried out.

#------------------------------------------------------------------------------------#


#!/usr/bin/env python3

import time
import boto3
import subprocess 
import sys


# AWS - Option selection Menu
def main():
    print(">-----------------------------------------<")
    print("| AWS - Automated Tasks |") 
    print(">-----------------------------------------<")
    print("1) Create Instance")
    print("2) List Instances")
    print("3) Terminate Instance") 
    print("4) Create Bucket")
    print("5) List Buckets")
    print("6) Delete Bucket")
    print("7) Fill Bucket (insert file/image into existing Bucket)")
    print("8) Empty Bucket")
    print("9) Check if Nginx Server is running -> run, if it's not.")
    print("")
    print("0) Exit")
    print(">-----------------------------------------<")





# --------------------------- Method Functions ------------------------------------- #

# Create instance using key & add to specified security group.
# User Data start-up script to apply required patches and install nginx web server.
#===================================================================================#
def createInstance():
    ec2 = boto3.resource('ec2')
    
    # Reference for Config. 1 & 2 (below): Jimmy McGibney
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #1 Configuration for Security Group
    sgdefault = 'sg-0aafdb2861d29acaf'
    inputstr = 'Enter your sg [' + sgdefault + ']: '
    sg=str(input(inputstr))
    if (sg == ""):
        sg = sgdefault 

    #2 Configuration for Key Name
    kndefault = 'loti-key'
    inputstr = 'Enter your key name (without .pem) [' + kndefault + ']: '
    keyname=str(input(inputstr))
    if (keyname == ""):
        keyname = kndefault    

    print("Security group:", sg)
    print("Key name:", keyname)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


    # Take in user input for Instance Name - used in the name_tag field below.
    inst_name=input('Enter a name for your Instance: ')
    print("Instance Name:", inst_name)
    name_tag={'Key':'Name', 'Value':inst_name}
    
    instance = ec2.create_instances(
        # Tags ~ Reference: Assessment1 Tips(pdf)
        ImageId='ami-0c21ae4a3bd190229',
        KeyName=keyname,         # key-pair: loti-key.pem
        MinCount=1,
        MaxCount=1,
        SecurityGroupIds=[sg],   # my HTTP/SSH security group: sg-0aafdb2861d29acaf
        UserData='''#!/bin/bash
                    yum update -y
                    yum install python3 -y
                    amazon-linux-extras install nginx1.12 -y
                    service nginx start
                    touch /home/ec2-user/testfile''',  # to check all ok
        InstanceType='t2.micro')

    instance[0].create_tags(Tags=[name_tag])

    print("An instance with ID", instance[0].id, "has been created.")
    time.sleep(5)
    instance[0].reload()
    print("Public IP address:", instance[0].public_ip_address)



# List all AWS instances.
#=========================#
def listInstances():
    ec2 = boto3.resource('ec2')
    for instance in ec2.instances.all():
        print (instance.id, instance.state,instance.public_ip_address,instance.tags)
        print ("+=================================================+")



# Terminate an instance
#=========================#
def terminateInstance():
    ec2 = boto3.resource('ec2')
    #List all instances
    listInstances()
    #Prompt - what instance will be terminated via Instance ID.
    terminate_instance = input("Please enter ID (Instance) to Terminate: ")
    instance = ec2.Instance(terminate_instance)
    # Try catch exception for invalid instance ID for deletion.
    try:
        response = instance.terminate()
        print (response)
    except Exception as error:
        print(error)



# Create a Bucket in S3 (Asks for Bucket name)
# Buckets are used to store files on AWS. 
#===========================================================#
def createBucket():
    s3 = boto3.resource("s3")
    create_bucket = input("Please enter your Bucket name: ")

    try:
        # Create a Bucket in the EU West location
        response = s3.create_bucket(Bucket=create_bucket,
        CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
        print(response)
    except Exception as error:
        print(error + "Please try again.. (make sure Bucket name is unique!")



# List all Buckets incl. all associated content.
#=================================================#
def listBuckets():
    s3 = boto3.resource('s3')

    #List bucket each bucket by name
    for bucket in s3.buckets.all():
        print (bucket.name)

        #List all Bucket contents
        try:
            for item in bucket.objects.all():
                print ("\t%s" % item.key)
        except Exception as error:
            print(error)



# Delete a specified Bucket (via Bucket name)
#================================================#
def deleteBucket():
    s3 = boto3.resource('s3')
    for bucket in s3.buckets.all():
        print(bucket.name)
    print("Please enter the Bucket you wish to Delete: ")
    bucket_name = input()
    bucket = s3.Bucket(bucket_name)
    try:
        response = bucket.delete()
        print(response)
    except Exception as error:
        print(error)





# Fill a Bucket - Insert File/Image into an existing Bucket
# Asks for user Bucket name, then for File name - copies and sends into the Bucket  
#=================================================================================#
def fillBucket():
    s3 = boto3.resource("s3")
    for bucket in s3.buckets.all():
        print(bucket.name)
    bucket_name = input("Please enter your Bucket name: ")
    object_name = input("Please enter the File/Image Name: ")
    
    # Try catch exception to see if the entered Bucket name exists.
    if (bucket.name == bucket_name):
        try:
            # Add file to aws bucket and make it public read.
            response = s3.Object(bucket_name, object_name).put(Body=open(object_name, 'rb'),ACL = ("public-read"))
            print (response)

        except Exception as error:
            print (error)
            


# Empty Bucket contents (i.e. Files/Images)
#=============================================#
def emptyBucket():
    # We'll firstly list all existing Buckets (if any)
    listBuckets()

    # Emptying a Bucket
    s3 = boto3.resource('s3')
    empty_bucket = input("Please enter the  Bucket you wish to empty: ")
    bucket = s3.Bucket(empty_bucket)
    if (empty_bucket == bucket.name):
        for key in bucket.objects.all():
            try:
                response = key.delete()
                print (response)
            except Exception as error:
                print (error)




# Checking whether Nginx is running or not.
#=============================================#
def checkNginx():
    try:
        # Nginx command
        cmd = 'ps -A | grep nginx'
        listInstances()
        #Run commands using subprocess:
        subprocess.run(cmd, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Nginx Server IS running")
        return 0
      
    #Error 
    except subprocess.CalledProcessError:
        print("Nginx Server IS NOT running")
        return 1



# Start Nginx Web Server.
#==========================#
def startNginx():
    try:
        cmd = 'sudo service nginx start'
        subprocess.run(cmd, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Nginx started")
   
    except subprocess.CalledProcessError:
        print("--- Error starting Nginx! ---")



# Each option -> different function.
#=============================================#
loop = True

while loop:
    main()
    option = input("Please select an option: ")
    
    #1
    if option == "1":
        print("Just a moment, creating Instance")
        print("..")
        createInstance()
       
    #2
    elif option == "2":
        print("List of Instances:")
        listInstances()
       
    #3
    elif option == "3":
        print("Terminating specified Instance")
        print("..")
        terminateInstance()
        
    #4
    elif option == "4":
        print("Just a moment, creating Bucket")
        print("..")  
        createBucket()
       
    #5
    elif option == "5":
        print("List of Buckets:")
        print("----------------")
        listBuckets()
       
    #6
    elif option == "6":
        print("Deleting specified Bucket")
        print("..")
        deleteBucket()
       
    #7
    elif option == "7":
        print("Adding File/Image to specified Bucket")
        print("..")
        fillBucket()
 
    #8
    elif option == "8":
        print("Emptying specified Bucket")
        print("..")
        emptyBucket()

    #9
    elif option == "9":
        print("Checking Nginx Server")
        print("..")
        checkNginx()
            
        if checkNginx() == 1:
            startNginx()
    
    #0    
    elif option == "0":
        print("Exiting..")
        exit()




# This is the standard boilerplate that calls the main() function.
#===================================================================#
if __name__ == '__main__':
    main()
