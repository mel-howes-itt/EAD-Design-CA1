import boto3
import random
import time

from use_lambda_function import ActivateLambdaNotification

# Initialize variables
myinstances = 0
rinstances = 0
r2instances = 0
rinstances2 = 0
myinstanceids = []
myrinstanceids = []
mydisruptedids = []
recoveredinstanceids = []
myASGChoices = []
numASGs = 0
all_my_instances = []
x = 0

# Welcome user to chaos monkey
print('\n' * 5)
print ('Welcome to Mels TUD Chaos Monkey (tud_cm)')
print ('----------------------------------------')
print()
print(r"""See no evil,    hear no evil,    speak no evil,    deliver chaos!

       .---.            .---.            .---.           .---.
     _/_-.-_\_        _/.-.-.\_        _/.-.-.\_       _/.-.-.\_
    / __} {__ \      /|( o o )|\      ( ( o o ) )     ( ( o o ) )
   / //     \\ \    | //     \\ |      |/     \|       |/     \|
  / / \ --- / \ \  / / \ --- / \ \      \ /^\ /         \ .-. /
  \ \_/-----\_/ /  \ \_/-----\_/ /      / \ / \         /-----\
   \           /    \           /      /  /|\  \       /       \

""")
print()

# Get the ASGs in this account
asg_client = boto3.client('autoscaling')
asg_response = asg_client.describe_auto_scaling_groups()
all_tags = asg_client.describe_tags()

# Show the ASG details to the user
for asg in asg_response['AutoScalingGroups']:
    print('List of autoscaling groups available:')
    print('Autoscaling Group Name: ', asg['AutoScalingGroupName'])
    print('ASG Max Size: ', asg['MaxSize'], 'ASG Min Size: ', asg['MinSize'])
    max_size = asg['MaxSize']
    myASGChoices.append(asg['AutoScalingGroupName'])
    numASGs+=1

# Ask user which ASG to disrupt, as there may be more than 1
while True:
    try:
        which_asg = input('\033[1;33;40mWhich ASG do you want to disrupt? ')
        if which_asg in myASGChoices:
            break
        raise ValueError
    except ValueError:
        print('\033[1;37;40mInvalid ASG name. Please enter a name from the list.')

print('\033[1;37;40mYou chose this ASG: ', which_asg)

# Get instances in that chosen ASG
my_asg_response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[which_asg])

for i in my_asg_response['AutoScalingGroups']:
    for k in i['Instances']:
        myinstances +=1
        myinstanceids.append(k['InstanceId'])

# Check there are instances found
if myinstances <1:
    print('No instances found. Chaos Monkey will now exit.')
    exit()

# Now get more info about the status of those instances
ec2 = boto3.resource('ec2')
ec2list = ec2.instances.filter(InstanceIds=myinstanceids)

print('\033[1;32;40mTotal number of instances: ', myinstances)
print('\033[1;32;40mNumber of running instances: ', rinstances)
print()

print ('\033[1;37;40mInstance List:')
print ('------------------')
print()

# Print out the ID, name and state of each instance
for instance in ec2list.all():
    for tag in instance.tags:
        if tag['Key']=='Name':
            print('\033[1;37;40mInstance ID: ',instance.id, 'Instance Name: ', tag['Value'], 'State: ', instance.state['Name'])

print()

# Input with validation, permissable values between 1 and number of running instances
while True:
    try:
        disrupt = int(input('\033[1;37;40mHow many instances would you like tud_cm to disrupt? '))
        if disrupt < 1 or disrupt > myinstances:
            raise ValueError
        break
    except ValueError:
        print("\033[1;31;40mInvalid number input. Please enter a number between 1 and ", rinstances)

# Randomly choose unique instance IDs to disrupt from the list of running instances
mydisruptedids = random.sample(myinstanceids, int(disrupt))

print('\033[1;32;40mDisrupting ', disrupt, ' instances...')
print('\033[1;37;40mDisrupted IDs: ', mydisruptedids)
print()

# Start counter for elapsed time between terminating instances and the correct number being up and running again as per HA policy
start_time = time.time()

# Terminate instances in ASG
ec2rec = boto3.client('ec2')
terminating = ec2rec.terminate_instances(InstanceIds=mydisruptedids)

print('\033[1;33;40mChecking the time taken for the auto-scale group to recover, please wait...')

# Wait 120 seconds to allow the terminate command to take effect before checking
time.sleep(120)

# Poll ec2 instances in ASG to check if there are less than the max size number of instances
recovered_instances = 0
while recovered_instances < int(max_size):
    recovered_instances = 0
    recovered_asg_response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[which_asg])
    for m in recovered_asg_response['AutoScalingGroups']:
        for p in m['Instances']:
            recoveredinstanceids.append(k['InstanceId'])
    recoveredec2list = ec2.instances.filter(InstanceIds=recoveredinstanceids)
    runninginstances = ec2list.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for recinstance in runninginstances.all():
        recovered_instances +=1

# Print out the elapsed time to recovery
elapsed_time = time.time() - start_time
print('\n' * 2)
print('\033[1;37;40mElapsed time: ', elapsed_time, ' seconds')
if elapsed_time < 60:
    message='Excellent recovery! Less than a minute.'
    print('Excellent recovery! Less than a minute.')
else:
    message='A bit slow, over 60 seconds.'
    print('A bit slow, over 60 seconds.')

# Send this result via lambda over SNS to email - doesn't work because on Rosetta Hub I can't create Roles or apply policies
ActivateLambdaNotification(message)
