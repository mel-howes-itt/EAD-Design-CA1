import boto3
import random
import time
import json

# Initialize variables
myinstances = 0
myinstanceids = []
myrinstances = 0
myrinstanceids = []
mydisruptedids = []
myASGChoices = []
goal_recovery_time = 0

# Function to get number and IDs of running instances in named ASG
def check_instances_running(which_asg):
    # Get instances in ASG
    my_asg_response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[which_asg])
    global myinstances
    global myrinstances
    myinstances = 0
    myrinstances = 0
    for j in my_asg_response['AutoScalingGroups']:
        for l in j['Instances']:
            myinstances +=1
            myinstanceids.append(l['InstanceId'])
	# Now check which instances are running
    ec2 = boto3.resource('ec2')
    ec2list = ec2.instances.filter(InstanceIds=myinstanceids)
    runninginstances = ec2list.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for myrinstance in runninginstances.all():
        myrinstances +=1
        myrinstanceids.append(myrinstance.id)
	
    return myinstances, myrinstances, myrinstanceids

def send_notification_by_lambda(outputMessage):
    # Get the lambda ARN dynamically
    lambda_client = boto3.client('lambda')

    myFunctionARN = 'arn:aws:lambda:eu-west-1:978614868007:function:EAD-Design-CA-Topic'
    payload = {}
    payload['message'] = outputMessage
    response = lambda_client.invoke(
        FunctionName=myFunctionARN,
        InvocationType='RequestResponse',
        LogType='Tail',
        Payload=json.dumps(payload)
    )
    print('Sending notification to lambda.')

def send_notification_direct(deliverableMessage):
    TopicARN = 'arn:aws:sns:eu-west-1:978614868007:EAD-Design-CA-Notification'
    snsClient = boto3.client('sns')
    response = snsClient.publish(
        TargetArn=TopicARN,
        Message=deliverableMessage
    )
    print('Sending notification direct to my topic.')

def get_all_asgs():
    # Get the ASGs in this account
    asg_response = asg_client.describe_auto_scaling_groups()
    all_tags = asg_client.describe_tags()

   # Show the ASG details to the user
    for asg in asg_response['AutoScalingGroups']:
        print('List of autoscaling groups available:')
        print('Autoscaling Group Name: ', asg['AutoScalingGroupName'])
        print('ASG Max Size: ', asg['MaxSize'], 'ASG Min Size: ', asg['MinSize'])
        myASGChoices.append(asg['AutoScalingGroupName'])
    return myASGChoices

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

# Get all the ASGs in the account
asg_client = boto3.client('autoscaling')
myASGChoices = get_all_asgs()

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

# Get all the instances in the chosen ASG
my_asg_response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[which_asg])
desired_capacity = my_asg_response['AutoScalingGroups'][0]['DesiredCapacity']

all_my_instances = check_instances_running(which_asg)

myinstances = all_my_instances[0]
myrinstances = all_my_instances[1]
myrinstanceids = all_my_instances[2]

# Check there are instances found
if myinstances <1:
    print('No instances found. Chaos Monkey will now exit.')
    exit()

# Now get more info about the status of those instances
ec2 = boto3.resource('ec2')
ec2list = ec2.instances.filter(InstanceIds=myinstanceids)

print('\033[1;32;40mTotal number of instances: ', myinstances)
print('\033[1;32;40mTotal number of running instances: ', myrinstances)
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
        print("\033[1;31;40mInvalid number input. Please enter a number between 1 and ", myrinstances)

# Randomly choose unique instance IDs to disrupt from the list of running instances
mydisruptedids = random.sample(myrinstanceids, int(disrupt))

print('\033[1;32;40mDisrupting ', disrupt, ' instances...')
print('\033[1;37;40mDisrupted IDs: ', mydisruptedids)
print()

# Start counter for elapsed time between terminating instances and the correct number being up and running again as per HA policy
start_time = time.time()

# Terminate the chosen instances
ec2rec = boto3.client('ec2')
terminating = ec2rec.terminate_instances(InstanceIds=mydisruptedids)

print('\033[1;33;40mChecking the time taken for the auto-scale group to recover, please wait...')

# Wait 60 seconds to allow the terminate command to take effect before checking
time.sleep(60)

running_now = 0

# This is the bit to check if things are up and running again.....
while running_now < desired_capacity:
    all_running = check_instances_running(which_asg)
    running_now = all_running[1]
    print('Polling recovery. Number of instances running now: ', running_now)
    if running_now == desired_capacity:
        print('\033[1;32;40mOK, back up and running at desired capacity!')
        break

# Print out the elapsed time to recovery
elapsed_time = time.time() - start_time

# Set a goal for recovery based on number of instances disrupted and the time it might take one instance to boot up 
goal_recovery_seconds = int(disrupt)*120

print('\n' * 2)
print('\033[1;37;40mElapsed time: ', elapsed_time, ' seconds')
if elapsed_time < goal_recovery_seconds:
    message='Mel says: There was a problem with some instances in the ASG. Do not panic, they made an excellent recovery! Less than 2 minutes per instance on average.'
    print(message)
else:
    message='Mel says: There was a problem with some instances in the ASG. It was a bit slow but they have now recovered, taking over 2 minutes per instance on average.'
    print(message)

# Send this result via lambda over SNS to email - doesn't work because on Rosetta Hub I can't create Roles or apply policies
send_notification_by_lambda(message)
send_notification_direct(message)
