provider "aws" {
  region = "eu-west-2"
}

terraform {
  backend "s3" {
    bucket       = "brunns-rss-agg-terraform-state"
    key          = "rss-agg"
    region       = "eu-west-2"
    encrypt      = true
    use_lockfile = true
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
  handler          = "run.sh"
  source_code_hash = filebase64sha256("deployment_package.zip")
  runtime          = "python3.14"
  timeout          = 30
  layers           = ["arn:aws:lambda:eu-west-2:753240598075:layer:LambdaAdapterLayerX86:25"]

  environment {
    variables = {
      AWS_LAMBDA_EXEC_WRAPPER    = "/opt/bootstrap"
      AWS_LWA_PORT               = "8080"
      AWS_LWA_ENABLE_COMPRESSION = "true"
      FEEDS_FILE                 = var.feeds_file
      MAX_ITEMS                  = var.max_items
      MAX_CONNECTIONS            = var.max_connections
    }
  }
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

resource "aws_lambda_permission" "api_gateway_invoke" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.rss_aggregator.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.rss_aggregator_flask_api.execution_arn}/*/*"
}

resource "aws_api_gateway_rest_api" "rss_aggregator_flask_api" {
  name        = "Flask API"
  description = "API Gateway for Flask application"
}

resource "aws_cloudwatch_log_group" "rss_aggregator_logs" {
  name              = "/aws/lambda/${aws_lambda_function.rss_aggregator.function_name}"
  retention_in_days = 14
}

resource "aws_iam_role" "api_gateway_cloudwatch" {
  name = "api_gateway_cloudwatch_global_${random_string.suffix.result}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "api_gateway_cloudwatch" {
  role       = aws_iam_role.api_gateway_cloudwatch.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}

resource "aws_api_gateway_account" "demo" {
  cloudwatch_role_arn = aws_iam_role.api_gateway_cloudwatch.arn
}

resource "aws_api_gateway_method_settings" "general_settings" {
  rest_api_id = aws_api_gateway_rest_api.rss_aggregator_flask_api.id
  stage_name  = aws_api_gateway_stage.prod.stage_name
  method_path = "*/*"

  depends_on = [aws_api_gateway_account.demo]

  settings {
    metrics_enabled = true
    logging_level   = "INFO"
    throttling_rate_limit  = 10
    throttling_burst_limit = 5
  }
}

resource "aws_api_gateway_method" "rss_aggregator_root_method" {
  rest_api_id   = aws_api_gateway_rest_api.rss_aggregator_flask_api.id
  resource_id   = aws_api_gateway_rest_api.rss_aggregator_flask_api.root_resource_id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "rss_aggregator_root_integration" {
  rest_api_id             = aws_api_gateway_rest_api.rss_aggregator_flask_api.id
  resource_id             = aws_api_gateway_rest_api.rss_aggregator_flask_api.root_resource_id
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
  rest_api_id = aws_api_gateway_rest_api.rss_aggregator_flask_api.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_method.rss_aggregator_root_method.id,
      aws_api_gateway_integration.rss_aggregator_root_integration.id,
      aws_api_gateway_resource.rss_aggregator_proxy.id,
      aws_api_gateway_method.rss_aggregator_proxy_method.id,
      aws_api_gateway_integration.rss_aggregator_lambda_integration.id
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "prod" {
  deployment_id = aws_api_gateway_deployment.rss_aggregator_flask_api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.rss_aggregator_flask_api.id
  stage_name    = "prod"
}

output "api_url" {
  value = aws_api_gateway_stage.prod.invoke_url
}
