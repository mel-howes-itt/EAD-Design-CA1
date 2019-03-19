import boto3
import random
import time

# Initialize variables
myinstances = 0
rinstances = 0
r2instances = 0
myinstanceids = []
myrinstanceids = []
mydisruptedids = []
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

ec2 = boto3.resource('ec2')

myclustername = input('What is the name of the instances in your cluster? ')

# Only select the instances that are part of the HA group i.e. have the same Name tag. 
inst_filter = [{'Name':'tag:Name', 'Values':[myclustername]}]
ec2list = ec2.instances.filter(Filters=inst_filter)

for instance in ec2list.all():
    myinstances +=1
    myinstanceids.append(instance.id)

# Check there are instances found
if myinstances <1:
    print('No instances found. Chaos Monkey will now exit.')
    exit()

# Get a variable that is the number of running instances, as opposed to terminated, pending etc
runninginstances = ec2list.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

for rinstance in runninginstances.all():
    rinstances +=1
    myrinstanceids.append(rinstance.id)

# Check there are running instances found
if rinstances <1:
    print('No running instances found. Chaos Monkey will now exit.')
    exit()

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
        if disrupt < 1 or disrupt > rinstances:
            raise ValueError
        break
    except ValueError:
        print("\033[1;31;40mInvalid number input. Please enter a number between 1 and ", rinstances)
		
# Choose random instance ids, from the list of running instances, to disrupt		
while x < (int(disrupt)):
    myrandom = random.choice(myrinstanceids)
    mydisruptedids.append(myrandom)
    x+=1

print('\033[1;32;40mDisrupting ', disrupt, ' instances...')
print('\033[1;37;40mDisrupted IDs: ', mydisruptedids)
print()

# Start counter for elapsed time between terminating instances and the correct number being up and running again as per HA policy
start_time = time.time()

# Terminate the instances
for myinstancetoterminate in mydisruptedids:
    instance = ec2.Instance(myinstancetoterminate)
    instance.terminate()
	
print('\033[1;33;40mChecking recovery, please wait...')

# Wait 10 seconds to allow the terminate command to take effect before checking
time.sleep(10)

# Poll to check if there are the required number of instances in a running state again yet i.e. HA has recovered	
while r2instances < rinstances:
    r2instances = 0
    ec2list = ec2.instances.filter(Filters=inst_filter)
    runninginstances = ec2list.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for rinstance in runninginstances.all():
        r2instances +=1
    # Add a few seconds in each loop before printing the ... (optional - just reduces the scrolling but impacts the accuracy of the elapsed time)
    time.sleep(5)
    print('...')

# Print out the elapsed time to recovery
elapsed_time = time.time() - start_time
print('\n' * 2)
print('\033[1;37;40mElapsed time: ', elapsed_time, ' seconds')
if elapsed_time < 60:
    print("Excellent recovery! Less than a minute.")
else:
    print('A bit slow, over 60 seconds.')


