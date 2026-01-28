from typing import Any

import awsgi

from rss_agg.web import app


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    AWS Lambda handler for WSGI application.

    Args:
        event: The Lambda event object (dict) containing the request data.
        context: The Lambda context object containing runtime information.

    Returns:
        A dictionary formatted as an API Gateway response.
    """
    return awsgi.response(app, event, context)
