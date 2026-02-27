output "bucket_name" {
  value = aws_s3_bucket.feeds.bucket
}

output "bucket_arn" {
  value = aws_s3_bucket.feeds.arn
}
