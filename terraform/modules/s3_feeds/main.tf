resource "aws_s3_bucket" "feeds" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_versioning" "feeds" {
  bucket = aws_s3_bucket.feeds.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "feeds" {
  bucket = aws_s3_bucket.feeds.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
