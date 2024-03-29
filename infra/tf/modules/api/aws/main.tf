variable "lambda_invoke_arn" {}

variable "lambda_name" {}

variable "environment" {}

variable "domain" {}

variable "api_subdomain" {}

variable "authorizer_name" {}

provider "aws" {
  alias  = "virginia"
  region = "us-east-1"
}

data "aws_route53_zone" "api_zone" {
  name = var.domain
}

resource "aws_route53_record" "pdf_api" {
  name    = aws_api_gateway_domain_name.pdf_api_domain_name.domain_name
  type    = "A"
  zone_id = data.aws_route53_zone.api_zone.id

  alias {
    evaluate_target_health = true
    name                   = aws_api_gateway_domain_name.pdf_api_domain_name.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.pdf_api_domain_name.cloudfront_zone_id
  }
}

resource "aws_acm_certificate" "api_cert" {
  domain_name       = "${var.api_subdomain}.${var.domain}"
  validation_method = "DNS"
  provider          = aws.virginia

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "api_cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.api_cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.api_zone.zone_id
}

resource "aws_acm_certificate_validation" "api_cert_validation" {
  provider                = aws.virginia
  certificate_arn         = aws_acm_certificate.api_cert.arn
  validation_record_fqdns = [for record in aws_route53_record.api_cert_validation : record.fqdn]
}


resource "aws_api_gateway_stage" "pdf_api" {
  deployment_id = aws_api_gateway_deployment.apideploy.id
  rest_api_id   = aws_api_gateway_rest_api.apiLambda.id
  stage_name    = var.environment
  cache_cluster_enabled = false
  cache_cluster_size = "0.5"
  xray_tracing_enabled = true
}

resource "aws_api_gateway_domain_name" "pdf_api_domain_name" {
  certificate_arn = aws_acm_certificate_validation.api_cert_validation.certificate_arn
  domain_name     = "${var.api_subdomain}.${var.domain}"
}

resource "aws_api_gateway_base_path_mapping" "example" {
  api_id      = aws_api_gateway_rest_api.apiLambda.id
  stage_name  = aws_api_gateway_stage.pdf_api.stage_name
  domain_name = aws_api_gateway_domain_name.pdf_api_domain_name.domain_name
}

resource "aws_api_gateway_rest_api" "apiLambda" {
  name        = "pdf_api_${var.environment}"
  description = "PDF creator API"

  #   policy = <<EOF
  # {
  #     "Version": "2012-10-17",
  #     "Statement": [
  #         {
  #             "Effect": "Allow",
  #             "Principal": "*",
  #             "Action": "execute-api:Invoke",
  #             "Resource": [
  #                 "*"
  #             ]
  #         },
  #         {
  #             "Effect": "Deny",
  #             "Principal": "*",
  #             "Action": "execute-api:Invoke",
  #             "Resource": [
  #                 "*"
  #             ],
  #             "Condition" : {
  #                 "StringNotEquals": {
  #                     "aws:SourceVpce": "${aws_vpc_endpoint.test.id}"
  #                 }
  #             }
  #         }
  #     ]
  # }
  # EOF

  #   endpoint_configuration {
  #     types = ["PRIVATE"]
  #     vpc_endpoint_ids = [aws_vpc_endpoint.test.id]
  #   }
}

data "aws_lambda_function" "authorizer" {
  function_name = var.authorizer_name
}

resource "aws_api_gateway_authorizer" "auth" {
  name           = "auth"
  rest_api_id    = aws_api_gateway_rest_api.apiLambda.id
  authorizer_uri = data.aws_lambda_function.authorizer.invoke_arn
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.apiLambda.id
  parent_id   = aws_api_gateway_rest_api.apiLambda.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxyMethod" {
  rest_api_id   = aws_api_gateway_rest_api.apiLambda.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.auth.id
}

resource "aws_api_gateway_resource" "docs" {
  rest_api_id = aws_api_gateway_rest_api.apiLambda.id
  parent_id   = aws_api_gateway_rest_api.apiLambda.root_resource_id
  path_part   = "docs"
}

resource "aws_api_gateway_method" "docs" {
  rest_api_id   = aws_api_gateway_rest_api.apiLambda.id
  resource_id   = aws_api_gateway_resource.docs.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_resource" "openapi_json" {
  rest_api_id = aws_api_gateway_rest_api.apiLambda.id
  parent_id   = aws_api_gateway_rest_api.apiLambda.root_resource_id
  path_part   = "openapi.json"
}

resource "aws_api_gateway_method" "openapi_json" {
  rest_api_id   = aws_api_gateway_rest_api.apiLambda.id
  resource_id   = aws_api_gateway_resource.openapi_json.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.apiLambda.id
  resource_id = aws_api_gateway_method.proxyMethod.resource_id
  http_method = aws_api_gateway_method.proxyMethod.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

resource "aws_api_gateway_integration" "docs" {
  rest_api_id = aws_api_gateway_rest_api.apiLambda.id
  resource_id = aws_api_gateway_method.docs.resource_id
  http_method = aws_api_gateway_method.docs.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

resource "aws_api_gateway_integration" "openapi_json" {
  rest_api_id = aws_api_gateway_rest_api.apiLambda.id
  resource_id = aws_api_gateway_method.openapi_json.resource_id
  http_method = aws_api_gateway_method.openapi_json.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

resource "aws_api_gateway_method" "proxy_root" {
  rest_api_id   = aws_api_gateway_rest_api.apiLambda.id
  resource_id   = aws_api_gateway_rest_api.apiLambda.root_resource_id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_root" {
  rest_api_id = aws_api_gateway_rest_api.apiLambda.id
  resource_id = aws_api_gateway_method.proxy_root.resource_id
  http_method = aws_api_gateway_method.proxy_root.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}


resource "aws_api_gateway_deployment" "apideploy" {
  depends_on = [
    aws_api_gateway_integration.lambda,
    aws_api_gateway_integration.lambda_root,
  ]

  rest_api_id = aws_api_gateway_rest_api.apiLambda.id
  stage_name  = var.environment
}


resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.apiLambda.execution_arn}/*/*"
}


output "base_url" {
  value = aws_api_gateway_deployment.apideploy.invoke_url
}
