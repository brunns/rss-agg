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

variable "fetch_timeout" {
  type    = number
  default = 3
}

variable "lambda_timeout" {
  type    = number
  default = 10
}

variable "memory_size" {
  type    = number
  default = 512
}

variable "log_level" {
  type    = string
  default = "INFO"
}
