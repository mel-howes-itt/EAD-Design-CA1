output "elb_dns_name" {
  value = "${aws_lb.example.dns_name}"
}
