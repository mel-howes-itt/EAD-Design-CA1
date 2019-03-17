import boto3


print ('Welcome to Mels TUD Chaos Monkey (tud_cm)')
print ('----------------------------------------')

ec2 = boto3.resource('ec2')
vpc = ec2.Vpc('vpc-48ef3c2e')
print('vpc state: ', vpc.state)

print ('Instance List:')
print ('------------------')

vpclist = vpc.instances.all()
for instance in vpclist:
    print(instance)
