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

module "lambda" {
  source = "./modules/lambda"

  name_suffix                = random_string.suffix.result
  memory_size                = var.memory_size
  lambda_timeout             = var.lambda_timeout
  feeds_service              = var.feeds_service
  feeds_file                 = var.feeds_file
  max_items                  = var.max_items
  max_connections            = var.max_connections
  max_keepalive_connections  = var.max_keepalive_connections
  keepalive_expiry           = var.keepalive_expiry
  retries                    = var.retries
  fetch_timeout              = var.fetch_timeout
  deployment_zip             = "deployment_package.zip"
  log_level                  = var.log_level
}

module "api_gateway" {
  source = "./modules/api_gateway"

  name_suffix         = random_string.suffix.result
  lambda_function_arn = module.lambda.lambda_arn
  lambda_invoke_arn   = module.lambda.lambda_invoke_arn
  lambda_name         = module.lambda.lambda_name
}
