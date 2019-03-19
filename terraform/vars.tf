variable "ACCESS_KEY" {}
variable "SECRET_KEY" {}

variable "REGION" {
  default = "eu-west-1"
}

variable "INSTANCE_TYPE" {
  default = "t2.micro"
}

variable "KEY_NAME" {
  default = "TU_Dublin"
}

variable "COUNT" {
 default = 1
}

variable "AMI" {
  default = {
    eu-west-1 = "ami-03d6469eda9235f8e"
  }
}


