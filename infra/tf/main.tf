terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "jwnwilson-pdf-service"
    key = "terraform.tfstate"
  }
  required_providers {
    aws = {
      source = "hashicorp/aws"
      # There is an issue in 3.74.0 that prevents us from deploying AWS API Gateway
      # stages. https://github.com/hashicorp/terraform-provider-aws/issues/22866
      version = "~> 3.73.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
}

# Complete using this guide:
# https://medium.com/@ilia.lazebnik/simplifying-aws-private-api-gateway-vpc-endpoint-association-with-terraform-b379a247afbf

# module "vpc" {
#   source = "terraform-aws-modules/vpc/aws"

#   name = "${var.project}-vpc-${var.environment}"
#   cidr = "10.10.0.0/16"

#   azs           = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]

#   # Add public_subnets and NAT Gateway to allow access to internet from Lambda
#   public_subnets  = ["10.10.1.0/24", "10.10.2.0/24", "10.10.3.0/24"]
#   private_subnets = ["10.10.101.0/24", "10.10.102.0/24", "10.10.103.0/24"]
#
#   If we attach our lambda to a VPC then we have to use a nat gateway for internet access
#   Do not do this as this is expensive.
#   enable_nat_gateway = false
# }

# data "aws_vpc_endpoint_service" "test" {
#   service = "execute-api"
# }

# resource "aws_vpc_endpoint" "pdf_vpc_endpoint" {
#   vpc_id              = module.vpc.vpc_id
#   service_name        = "pdf generation service"
#   vpc_endpoint_type   = "Interface"
#   private_dns_enabled = true

#   subnet_ids = module.vpc.private_subnets
#   security_group_ids = [module.vpc.default_security_group_id]
# }

module "pdf_api" {
  source                  = "terraform-aws-modules/lambda/aws"

  function_name           = "pdf_api_${var.environment}"
  description             = "PDF creator API"

  create_package          = false

  image_uri               = "${var.ecr_api_url}:${var.docker_tag}"
  package_type            = "Image"
  # vpc_subnet_ids          = module.vpc.private_subnets
  # vpc_security_group_ids  = [module.vpc.default_security_group_id]
  attach_network_policy   = true
  timeout                 = 30

  attach_tracing_policy   = true
  tracing_mode            = "Active"

  provisioned_concurrent_executions = 10
  publish                 = true

  environment_variables = {
    ENVIRONMENT = var.environment
  }

}

module "api_gateway" {
  source = "./modules/api/aws"

  environment       = var.environment
  lambda_invoke_arn = module.pdf_api.lambda_function_invoke_arn
  lambda_name       = module.pdf_api.lambda_function_name
  domain            = "jwnwilson.co.uk"
  api_subdomain     = "pdf-generator-${var.environment}"
  authorizer_name   = "authorizer_api_gw_${var.environment}"
}

module "queue" {
  source = "./modules/queue/aws"

  environment           = var.environment
  aws_access_key        = var.aws_access_key
  aws_secret_key        = var.aws_secret_key
  region                = var.region
}

resource "aws_lambda_event_source_mapping" "sqs" {
  event_source_arn = module.queue.queue_arn
  function_name    = module.pdf_worker.lambda_function_name
}

module "pdf_worker" {
  source                  = "terraform-aws-modules/lambda/aws"

  function_name           = "pdf_worker_${var.environment}"
  description             = "PDF creator worker"

  create_package          = false

  image_uri               = "${var.ecr_api_url}:${var.docker_tag}"
  package_type            = "Image"
  # vpc_subnet_ids          = module.vpc.private_subnets
  # vpc_security_group_ids  = [module.vpc.default_security_group_id]
  attach_network_policy   = true
  timeout                 = 900

  environment_variables = {
    ENVIRONMENT = var.environment
  }

  # override docker image command to run worker handler
  image_config_command = ["app.adapter.into.sqs.handler.pdf_generator_lambda_handler"]

}

module "pdf_db" {
  source   = "terraform-aws-modules/dynamodb-table/aws"

  name     = "pdf_task_${var.environment}"
  hash_key = "user_id"
  range_key = "task_id"

  attributes = [
    {
      name = "user_id"
      type = "S"
    },
    {
      name = "task_id"
      type = "S"
    }
  ]

  tags = {
    Terraform   = "true"
    Environment = var.environment
  }
}

resource "aws_iam_policy" "sqs-s3-lambda-policy" {
  name        = "sqs-s3-lambda-policy-${var.environment}"
  description = "lambda sqs s3 policy"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "sqs:*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    },
    {
        "Sid": "AllS3Actions",
        "Effect": "Allow",
        "Action": "s3:*",
        "Resource": [
          "arn:aws:s3:::jwnwilson-pdf-template-${var.environment}/*",
          "arn:aws:s3:::jwnwilson-pdf-task-${var.environment}*/",
          "*"
        ]
    },
    {
      "Sid": "AllDynamodbActions",
      "Action": [
        "dynamodb:*"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:dynamodb:::table/pdf_task_*",
        "arn:aws:dynamodb:eu-west-1:675468650888:table/pdf_task_*"
      ]
    },
    {
        "Effect": "Allow",
        "Action": [
            "ssm:DescribeParameters",
            "ssm:GetParameters",
            "ssm:GetParameter"
        ],
        "Resource": [
          "arn:aws:ssm:eu-west-1:675468650888:parameter/pdf-api/upload_access_id_${var.environment}",
          "arn:aws:ssm:eu-west-1:675468650888:parameter/pdf-api/upload_secret_key_${var.environment}"
        ]
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "sqs-attach" {
  role       = module.pdf_worker.lambda_role_name
  policy_arn = aws_iam_policy.sqs-s3-lambda-policy.arn
}

resource "aws_iam_role_policy_attachment" "sqs-attach-api" {
  role       = module.pdf_api.lambda_role_name
  policy_arn = aws_iam_policy.sqs-s3-lambda-policy.arn
}

resource "aws_s3_bucket" "pdf_task_storage" {
  bucket = "jwnwilson-pdf-task-${var.environment}"
  acl    = "private"

  policy = <<EOF
  {
    "Version": "2008-10-17",
    "Statement": [{
      "Sid": "AllowAccessInAWS",
      "Effect": "Allow",
      "Principal": { "AWS": "*" },
      "Action": ["s3:*"],
      "Resource": ["arn:aws:s3:::jwnwilson-pdf-task-${var.environment}/*" ]
    }]
  }
  EOF

  tags = {
    Name        = "Pdf task bucket${var.environment} "
    Environment = var.environment
  }
}

resource "aws_s3_bucket" "pdf_storage" {
  bucket = "jwnwilson-pdf-template-${var.environment}"
  acl    = "private"

  policy = <<EOF
  {
    "Version": "2008-10-17",
    "Statement": [{
      "Sid": "AllowAccessInAWS",
      "Effect": "Allow",
      "Principal": { "AWS": "*" },
      "Action": ["s3:*"],
      "Resource": ["arn:aws:s3:::jwnwilson-pdf-template-${var.environment}/*" ]
    }]
  }
  EOF

  tags = {
    Name        = "Pdf template bucket ${var.environment} "
    Environment = var.environment
  }
}

resource "aws_iam_access_key" "upload_user" {
  user    = aws_iam_user.upload_user.name
}

resource "aws_iam_user" "upload_user" {
  name = "upload_user_${var.environment}"
  path = "/"
}

resource "aws_iam_user_policy" "upload_user_s3" {
  name = "upload_user_s3_${var.environment}"
  user = aws_iam_user.upload_user.name

  policy = <<EOF
{
  "Version": "2008-10-17",
  "Statement": [{
    "Sid": "AllowAccessInAWS",
    "Effect": "Allow",
    "Action": ["s3:*"],
    "Resource": [
      "arn:aws:s3:::jwnwilson-pdf-template-${var.environment}/*",
      "arn:aws:s3:::jwnwilson-pdf-task-${var.environment}/*" 
    ]
  }]
}
EOF
}

resource "aws_ssm_parameter" "upload_access_id" {
  name  = "/pdf-api/upload_access_id_${var.environment}"
  type  = "String"
  value = aws_iam_access_key.upload_user.id
}

resource "aws_ssm_parameter" "upload_secret_key" {
  name  = "/pdf-api/upload_secret_key_${var.environment}"
  type  = "String"
  value = aws_iam_access_key.upload_user.secret
}