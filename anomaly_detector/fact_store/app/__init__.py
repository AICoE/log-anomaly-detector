"""Fact Store App."""
import os
from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

from anomaly_detector.fact_store.app.models.model import db
from anomaly_detector.fact_store.app.views.api import api
from anomaly_detector.fact_store.app.views.index import index_blueprint


def create_app():
    """Create Flask App."""
    app = Flask(__name__, static_folder="static")

    # Register blueprints
    app.register_blueprint(index_blueprint)
    app.register_blueprint(api)

    sql_db = os.getenv("SQL_CONNECT", "sqlite://")
    app.config['SQLALCHEMY_DATABASE_URI'] = sql_db
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Setup Prometheus Metrics
    metrics = PrometheusMetrics(app)
    metrics.info('app_info', 'Log Anomaly Detector', version='v0.1.0.beta1')

    # Initialize db and tables
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app
