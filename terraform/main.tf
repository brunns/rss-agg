provider "aws" {
  region = "eu-west-2"
}

terraform {
  backend "s3" {
    bucket         = "brunning-terraform-state"
    key            = "rss-agg"
    region         = "eu-west-2"
    dynamodb_table = "brunning-terraform-lock-table"
    encrypt        = true
  }
}

resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_lambda_function" "rss_aggregator" {
  filename         = "deployment_package.zip"
  function_name    = "rss_aggregator"
  role             = aws_iam_role.rss_aggregator_lambda_exec.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = filebase64sha256("deployment_package.zip")
  runtime          = "python3.14"
  timeout          = 15
}

resource "aws_iam_role" "rss_aggregator_lambda_exec" {
  name = "rss_aggregator_lambda_exec_role_${random_string.suffix.result}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "rss_aggregator_lambda_policy" {
  role       = aws_iam_role.rss_aggregator_lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_api_gateway_rest_api" "rss_aggregator_flask_api" {
  name        = "Flask API"
  description = "API Gateway for Flask application"
}

resource "aws_api_gateway_resource" "rss_aggregator_root" {
  rest_api_id = aws_api_gateway_rest_api.rss_aggregator_flask_api.id
  parent_id   = aws_api_gateway_rest_api.rss_aggregator_flask_api.root_resource_id
  path_part   = ""
}

resource "aws_api_gateway_method" "rss_aggregator_root_method" {
  rest_api_id   = aws_api_gateway_rest_api.rss_aggregator_flask_api.id
  resource_id   = aws_api_gateway_resource.rss_aggregator_root.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "rss_aggregator_root_integration" {
  rest_api_id             = aws_api_gateway_rest_api.rss_aggregator_flask_api.id
  resource_id             = aws_api_gateway_resource.rss_aggregator_root.id
  http_method             = aws_api_gateway_method.rss_aggregator_root_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.rss_aggregator.invoke_arn
}

resource "aws_api_gateway_resource" "rss_aggregator_proxy" {
  rest_api_id = aws_api_gateway_rest_api.rss_aggregator_flask_api.id
  parent_id   = aws_api_gateway_rest_api.rss_aggregator_flask_api.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "rss_aggregator_proxy_method" {
  rest_api_id   = aws_api_gateway_rest_api.rss_aggregator_flask_api.id
  resource_id   = aws_api_gateway_resource.rss_aggregator_proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "rss_aggregator_lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.rss_aggregator_flask_api.id
  resource_id             = aws_api_gateway_resource.rss_aggregator_proxy.id
  http_method             = aws_api_gateway_method.rss_aggregator_proxy_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.rss_aggregator.invoke_arn
}

resource "aws_api_gateway_deployment" "rss_aggregator_flask_api_deployment" {
  depends_on = [
    aws_api_gateway_integration.rss_aggregator_lambda_integration,
    aws_api_gateway_integration.rss_aggregator_root_integration
  ]
  rest_api_id = aws_api_gateway_rest_api.rss_aggregator_flask_api.id
  stage_name  = "prod"
}

output "api_url" {
  value = aws_api_gateway_deployment.rss_aggregator_flask_api_deployment.invoke_url
}
