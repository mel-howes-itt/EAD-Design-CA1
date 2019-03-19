Git Repo for EAD Design CA1: Technological University Dublin - Tallaght campus

Aim
----
Create a Chaos Monkey to disrupt a high availability ec2 cluster. 
Disruption means the random termination of instances.
Measure the time taken between start of disruption and cluster recovery.

Using the Chaos Monkey
---------------------

The script will look for input:

- Name tag of your ec2 instances
- Number of instances you would like to disrupt

It will poll instance statuses until the desired number are in a running state again. 

I have added lots of comments which should be removed if this were a live python script. 