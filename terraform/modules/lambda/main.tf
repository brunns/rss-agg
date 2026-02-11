resource "aws_iam_role" "lambda_exec" {
  name = "rss_aggregator_lambda_exec_role_${var.name_suffix}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = { Service = "lambda.amazonaws.com" }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "this" {
  description   = "Aggregate, de-duplicate and republish RSS feeds"
  filename      = var.deployment_zip
  function_name = "rss_aggregator"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "run.sh"
  runtime       = "python3.14"
  architectures = ["arm64"]
  memory_size   = var.memory_size
  timeout       = var.lambda_timeout
  publish       = true
  source_code_hash = filebase64sha256(var.deployment_zip)

  layers = [
    "arn:aws:lambda:eu-west-2:753240598075:layer:LambdaAdapterLayerArm64:25"
  ]

  snap_start {
    apply_on = "PublishedVersions"
  }

  environment {
    variables = {
      AWS_LAMBDA_EXEC_WRAPPER    = "/opt/bootstrap"
      AWS_LWA_PORT               = "8080"
      AWS_LWA_ENABLE_COMPRESSION = "true"
      FEEDS_FILE                 = var.feeds_file
      MAX_ITEMS                  = var.max_items
      MAX_CONNECTIONS            = var.max_connections
      MAX_KEEPALIVE_CONNECTIONS  = var.max_keepalive_connections
      KEEPALIVE_EXPIRY           = var.keepalive_expiry
      RETRIES                    = var.retries
      TIMEOUT                    = var.fetch_timeout
      LOG_LEVEL                  = var.log_level
    }
  }
}

resource "aws_lambda_alias" "live" {
  name             = "live"
  description      = "Alias pointing to the latest published version"
  function_name    = aws_lambda_function.this.function_name
  function_version = aws_lambda_function.this.version
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.this.function_name}"
  retention_in_days = 14
}
