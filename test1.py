import boto3
import random
import time

# Initialize variables
myinstances = 0
r2instances = 0
myinstanceids = []
x = 0

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

# Get the ASG, related instanes and their tags
client = boto3.client('autoscaling')
response = client.describe_auto_scaling_groups()
all_instances = client.describe_auto_scaling_instances()
all_tags = client.describe_tags()

# Show the ASG details to the user
for asg in response['AutoScalingGroups']:
    print('Autoscaling Group Name: ', asg['AutoScalingGroupName'])
    print('ASG Max Size: ', asg['MaxSize'], 'ASG Min Size: ', asg['MinSize'])

# Check there are running instances found
if myinstances <1:
    print('No running instances found. Chaos Monkey will now exit.')
    exit()

print('\033[1;32;40mNumber of running instances: ', myinstances)
print()

print ('\033[1;37;40mInstance List:')
print ('------------------')
print()

# Print out the ID, name and state of the instances
for instance in all_instances['AutoScalingInstances']:
    print('Instance ID: ', instance['InstanceId'], 'Status: ', instance['LifecycleState'], 'Health Status: ', instance['HealthStatus'])
	myinstances +=1
	myinstanceids.append(instance['InstanceId'])

# Show the tags so the user can see the instance names as per the ASG
for tag in all_tags['Tags']:
    print('Key: ', tag['Key'], 'Value: ', tag['Value'])
			
print()

# Input with validation, permissable values between 1 and number of running instances
while True:
    try:
        disrupt = int(input('\033[1;37;40mHow many instances would you like tud_cm to disrupt? '))
        if disrupt < 1 or disrupt > myinstances:
            raise ValueError
        break
    except ValueError:
        print("\033[1;31;40mInvalid number input. Please enter a number between 1 and ", myinstances)
		
# Randomly choose unique instance IDs to disrupt from the list of running instances
mydisruptedids = random.sample(myinstanceids, int(disrupt))

print('\033[1;32;40mDisrupting ', disrupt, ' instances...')
print('\033[1;37;40mDisrupted IDs: ', mydisruptedids)
print()

# Start counter for elapsed time between terminating instances and the correct number being up and running again as per HA policy
start_time = time.time()

# Terminate the instances via changing instance health
for myinstancetoterminate in mydisruptedids:
    terminating = client.terminate_instance_in_auto_scaling_group(
    InstanceId=myinstancetoterminate,
    ShouldDecrementDesiredCapacity=False
    )
    print(terminating)
	
print('\033[1;33;40mChecking the time taken for the auto-scale group to recover, please wait...')

# Wait 10 seconds to allow the terminate command to take effect before checking
time.sleep(10)

# New section needed to check status of instances or ASG


# Print out the elapsed time to recovery
elapsed_time = time.time() - start_time
print('\n' * 2)
print('\033[1;37;40mElapsed time: ', elapsed_time, ' seconds')
if elapsed_time < 60:
    print("Excellent recovery! Less than a minute.")
else:
    print('A bit slow, over 60 seconds.')
