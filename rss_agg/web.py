from rss_agg.flask_app_factory import create_app

app, container = create_app()

if __name__ == "__main__":
    app.run()
