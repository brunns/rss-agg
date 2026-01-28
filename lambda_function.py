import awsgi
from rss_agg.web import app

def lambda_handler(event, context):
    return awsgi.response(app, event, context)
