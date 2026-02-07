variable "feeds_file" {
  type    = string
  default = "feeds.txt"
}

variable "max_items" {
  type    = string
  default = "50"
}

variable "max_connections" {
  type    = string
  default = "16"
}

variable "timeout" {
  type    = number
  default = 30
}

variable "memory_size" {
  type    = number
  default = 512
}
