provider "aws" {
  region = "eu-west-2"
}

terraform {
  required_version = ">= 1.0"

  backend "s3" {
    bucket       = "brunns-rss-agg-terraform-state"
    key          = "rss-agg"
    region       = "eu-west-2"
    encrypt      = true
    use_lockfile = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }

    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

module "s3_feeds" {
  source      = "./modules/s3_feeds"
  bucket_name = var.feeds_bucket_name
}

module "lambda" {
  source = "./modules/lambda"

  name_suffix               = random_string.suffix.result
  memory_size               = var.memory_size
  lambda_timeout            = var.lambda_timeout
  feeds_service             = var.feeds_service
  feeds_file                = var.feeds_file
  feeds_bucket_arn          = module.s3_feeds.bucket_arn
  feeds_bucket_name         = var.feeds_bucket_name
  feeds_object_name         = var.feeds_object_name
  max_items                 = var.max_items
  max_connections           = var.max_connections
  max_keepalive_connections = var.max_keepalive_connections
  keepalive_expiry          = var.keepalive_expiry
  retries                   = var.retries
  fetch_timeout             = var.fetch_timeout
  deployment_zip            = "deployment_package.zip"
  log_level                 = var.log_level
}

module "api_gateway" {
  source = "./modules/api_gateway"

  name_suffix       = random_string.suffix.result
  lambda_invoke_arn = module.lambda.lambda_invoke_arn
  lambda_name       = module.lambda.lambda_name
}
