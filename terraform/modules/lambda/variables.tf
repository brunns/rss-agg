variable "name_suffix" {
  type = string
}

variable "memory_size" {
  type = number
}

variable "lambda_timeout" {
  type = number
}

variable "feeds_service" {
  type = string
}

variable "feeds_file" {
  type = string
}

variable "max_items" {
  type = number
}

variable "max_connections" {
  type = number
}

variable "max_keepalive_connections" {
  type = number
}

variable "keepalive_expiry" {
  type = number
}

variable "retries" {
  type = number
}

variable "fetch_timeout" {
  type = number
}

variable "deployment_zip" {
  type = string
}

variable "log_level" {
  type = string
}

variable "feeds_bucket_arn" {
  type = string
}

variable "feeds_bucket_name" {
  type    = string
  default = "brunns-rss-agg-feeds"
}

variable "feeds_object_name" {
  type    = string
  default = "feeds.txt"
}
