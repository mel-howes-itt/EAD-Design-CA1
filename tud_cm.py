import boto3
import random
import time

# Initialize variables
myinstances = 0
myinstanceids = []
mydisruptedids = []
x = 0

print ('Welcome to Mels TUD Chaos Monkey (tud_cm)')
print ('----------------------------------------')

ec2 = boto3.resource('ec2')

print ('Instance List:')
print ('------------------')

# Only select the instances that are part of my HA group. They all have the name EAD-Design-CA-Web.
inst_filter = [{'Name':'tag:Name', 'Values':['EAD-Design-CA-Web']}]
ec2list = ec2.instances.filter(Filters=inst_filter)

for instance in ec2list.all():
    myinstances +=1
    myinstanceids.append(instance.id)

# Need a new variable for the number of ec2 instances that are state running (rather than pending, stopped or terminated)
print('\033[1;32;40mNumber or instances: ', myinstances)

# Print out the ID, name and state of each instance
for instance in ec2list.all():
    for tag in instance.tags:
        if tag['Key']=='Name':
            print('\033[1;37;40mInstance ID: ',instance.id, 'Instance Name: ', tag['Value'], 'State: ', instance.state['Name'])

# Needs input validation, values between 1 and number of running instances
disrupt = input('\033[1;37;40mHow many instances would you like tud_cm to disrupt? ')

while x < (int(disrupt)):
    myrandom = random.choice(myinstanceids)
    mydisruptedids.append(myrandom)
    x+=1

print('\033[1;32;40mDisrupting ', disrupt, ' instances...')
print('\033[1;37;40mDisrupted IDs: ', mydisruptedids)

# Start counter for elapsed time between terminating instances and the correct number being up and running again as per HA policy
start_time = time.time()

for myinstancetoterminate in mydisruptedids:
    instance = ec2.Instance(myinstancetoterminate)
    instance.terminate()

print('Waiting 10 seconds....')

time.sleep(10)

ec2list = ec2.instances.filter(Filters=inst_filter)
for instance in ec2list.all():
    for tag in instance.tags:
        if tag['Key']=='Name':
            print('\033[1;37;40mInstance ID: ',instance.id, 'Instance Name: ', tag['Value'], 'State: ', instance.state['Name'])


print('Waiting 30 seconds....')

time.sleep(30)

ec2list = ec2.instances.filter(Filters=inst_filter)
for instance in ec2list.all():
    for tag in instance.tags:
        if tag['Key']=='Name':
            print('\033[1;37;40mInstance ID: ',instance.id, 'Instance Name: ', tag['Value'], 'State: ', instance.state['Name'])


print('Waiting another 45 seconds....')

time.sleep(45)

ec2list = ec2.instances.filter(Filters=inst_filter)
for instance in ec2list.all():
    for tag in instance.tags:
        if tag['Key']=='Name':
            print('\033[1;37;40mInstance ID: ',instance.id, 'Instance Name: ', tag['Value'], 'State: ', instance.state['Name'])

elapsed_time = time.time() - start_time
print('Elapsed time: ', elapsed_time)
