data "aws_availability_zones" "all" {}

### Creating Security Group for EC2
resource "aws_security_group" "instance" {
  name = "EAD-CA-INSTANCE-SG"
  ingress {
    from_port = 80
    to_port   = 80
    protocol  = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
## Creating Launch Configuration
resource "aws_launch_configuration" "example" {
  name                   = "EAD-CA-LC"
  image_id               = "${lookup(var.AMI,var.REGION)}"
  instance_type          = "t2.micro"
  security_groups        = ["${aws_security_group.instance.id}"]
  key_name               = "${var.KEY_NAME}"
  lifecycle {
    create_before_destroy = true
  }
}
## Creating AutoScaling Group
resource "aws_autoscaling_group" "example" {
  name = "EAD-CA-ASG"
  launch_configuration = "${aws_launch_configuration.example.id}"
  availability_zones = ["${data.aws_availability_zones.all.names}"]
  min_size = 3
  max_size = 3
  default_cooldown = 60
  health_check_grace_period = 60
  target_group_arns = ["${aws_lb_target_group.alb_target_group.arn}"]
  tag {
    key = "Name"
    value = "EAD-CA-ASG-INSTANCE"
    propagate_at_launch = true
  }
}
## Security Group for ELB
resource "aws_security_group" "elb" {
  name = "EAD-CA-LB-SG"
  egress {
    from_port = 0
    to_port = 0 
    protocol = "-1"
    security_groups = ["${aws_security_group.instance.id}"]
  }
  ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
### Target Group
resource "aws_lb_target_group" "alb_target_group" {  
  name     = "EAD-CA-TG"  
  port     = "80"  
  protocol = "HTTP"  
  vpc_id   = "vpc-48ef3c2e"   
  tags {    
    name = "EAD-CA-TG"    
  }   
}
### Creating ELB
resource "aws_lb" "example" {
  name = "EAD-CA-LB"
  security_groups = ["${aws_security_group.elb.id}"]
  subnets = "${var.SUBNETS}"
}
# Listener
resource "aws_lb_listener" "alb_listener" {  
  load_balancer_arn = "${aws_lb.example.arn}"  
  port              = 80  
  protocol          = "HTTP"
  
  default_action {    
    target_group_arn = "${aws_lb_target_group.alb_target_group.arn}"
    type             = "forward"  
  }
}
