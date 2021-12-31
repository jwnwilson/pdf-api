terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "jwnwilson-pdf-service"
    key = "terraform.tfstate"
  }
}

provider "aws" {
  region  = var.aws_region
}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "${var.project}-vpc-${var.environment}"
  cidr = "10.10.0.0/16"

  azs           = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
  intra_subnets = ["10.10.101.0/24", "10.10.102.0/24", "10.10.103.0/24"]

  # Add public_subnets and NAT Gateway to allow access to internet from Lambda
  # public_subnets  = ["10.10.1.0/24", "10.10.2.0/24", "10.10.3.0/24"]
  # enable_nat_gateway = true
}

module "pdf_api" {
  source                  = "terraform-aws-modules/lambda/aws"

  function_name           = "pdf_api_${var.environment}"
  description             = "PDF creator API"

  create_package          = false

  image_uri               = "${var.ecr_api_url}:${var.docker_tag}"
  package_type            = "Image"
  vpc_subnet_ids          = module.vpc.intra_subnets
  vpc_security_group_ids  = [module.vpc.default_security_group_id]
  attach_network_policy   = true

  environment_variables = {
    ENVIRONMENT = var.environment
  }

}

module "api_gateway" {
  source = "./modules/api/aws"

  environment       = var.environment
  lambda_invoke_arn = module.pdf_api.lambda_function_invoke_arn
  lambda_name       = module.pdf_api.lambda_function_name

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
  vpc_subnet_ids          = module.vpc.intra_subnets
  vpc_security_group_ids  = [module.vpc.default_security_group_id]
  attach_network_policy   = true

  environment_variables = {
    ENVIRONMENT = var.environment
  }

  # override docker image command to run worker handler
  image_config_command = ["app.adapter.into.sqs.handler"]
}

module "pdf_db" {
  source   = "terraform-aws-modules/dynamodb-table/aws"

  name     = "pdf_generation_${var.environment}"
  hash_key = "id"

  attributes = [
    {
      name = "id"
      type = "N"
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
        "Sid": "ListObjectsInBucket",
        "Effect": "Allow",
        "Action": ["s3:ListBucket"],
        "Resource": ["arn:aws:s3:::pdf_generation_${var.environment}"]
    },
    {
        "Sid": "AllObjectActions",
        "Effect": "Allow",
        "Action": "s3:*Object",
        "Resource": ["arn:aws:s3:::pdf_generation_${var.environment}/*"]
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "sqs-attach" {
  role       = module.pdf_worker.lambda_role_name
  policy_arn = aws_iam_policy.sqs-lambda-policy.arn
}

resource "aws_s3_bucket" "pdf_storage" {
  bucket = "pdf_generation_${var.environment}"
  acl    = "private"

  tags = {
    Name        = "Pdf generation bucket${var.environment} "
    Environment = var.environment
  }
}
