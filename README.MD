Git Repo for EAD Design CA1: Technological University Dublin - Tallaght campus
------------------------------------------------------------------------------

Aim
----
Create a Chaos Monkey to disrupt a high availability ec2 cluster. 
Disruption means the random termination of instances.
Measure the time taken between start of disruption and cluster recovery.

Set-up
------
The python script runs on Linux with the AWC CLI and SDK installed. 
I have created a helper terraform script (and given credit to the source I based it on) that will spin up the high availability autoscaling group. Please note that you will need to supply your own credentials (access and secret keys) in a further file or add them into the vars.tf file. 
I have set the max and min numbers of instances to 6. 

Using the Chaos Monkey
---------------------
The script will look for user input when it runs:

- Name of your Autoscaling Group
- Number of instances you would like to disrupt

It will poll instance statuses until the desired number are in a running state again. 
