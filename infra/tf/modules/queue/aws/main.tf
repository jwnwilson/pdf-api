variable "aws_access_key" {}

variable "aws_secret_key" {}

variable "region" {}

variable "environment" {}

# Configure the AWS Provider
provider "aws" {
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  region     = var.region
}

resource "aws_sqs_queue" "pdf_task_queue_deadletter" {
  name                      = "pdf_task_queue_deadletter"
  delay_seconds             = 90
  max_message_size          = 2048
  message_retention_seconds = 86400
  receive_wait_time_seconds = 10

  tags = {
    Environment = var.environment
  }
}

resource "aws_sqs_queue" "pdf_task_queue" {
  name                      = "pdf_task_queue"
  delay_seconds             = 90
  max_message_size          = 2048
  message_retention_seconds = 86400
  receive_wait_time_seconds = 10
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.pdf_task_queue_deadletter.arn
    maxReceiveCount     = 4
  })

  tags = {
    Environment = var.environment
  }
}

output "queue_arn" {
  value = aws_sqs_queue.pdf_task_queue.arn
}
