output "lambda_arn" {
  value = aws_lambda_alias.live.arn
}

output "lambda_invoke_arn" {
  value = aws_lambda_alias.live.invoke_arn
}

output "lambda_name" {
  value = aws_lambda_alias.live.function_name
}
