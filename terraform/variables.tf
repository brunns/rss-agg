variable "feeds_file" {
  type    = string
  default = "feeds.txt"
}

variable "max_items" {
  type    = number
  default = 50
}

variable "max_connections" {
  type    = number
  default = 16
}

variable "max_keepalive_connections" {
  type    = number
  default = 16
}

variable "keepalive_expiry" {
  type    = number
  default = 5
}

variable "retries" {
  type    = number
  default = 3
}

variable "fetch_timeout" {
  type    = number
  default = 3
}

variable "lambda_timeout" {
  type    = number
  default = 15
}

variable "memory_size" {
  type    = number
  default = 256
}

variable "log_level" {
  type    = string
  default = "INFO"
}
