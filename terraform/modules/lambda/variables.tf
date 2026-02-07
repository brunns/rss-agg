variable "name_suffix" {
  type = string
}

variable "memory_size" {
  type = number
}

variable "lambda_timeout" {
  type = number
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

variable "fetch_timeout" {
  type = number
}

variable "deployment_zip" {
  type = string
}
