from unittest.mock import patch

from rss_agg.web import app


def test_get_data_returns_rss_response():
    with patch("rss_agg.web.read_and_generate_rss", return_value="<rss></rss>"):
        response = app.test_client().get("/")
        assert response.status_code == 200
        assert response.mimetype == "text/xml"
        assert response.data.decode() == "<rss></rss>"


def test_get_data_handles_empty_rss():
    with patch("rss_agg.web.read_and_generate_rss", return_value=""):
        response = app.test_client().get("/")
        assert response.status_code == 200
        assert response.mimetype == "text/xml"
        assert response.data.decode() == ""


def test_get_data_handles_exception():
    with patch("rss_agg.web.read_and_generate_rss", side_effect=Exception("Error")):
        response = app.test_client().get("/")
        assert response.status_code == 500
