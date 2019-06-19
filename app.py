"""Log Anomaly Detector."""
from prometheus_client import start_http_server
from anomaly_detector.config import Configuration
from anomaly_detector.fact_store.app import app
from anomaly_detector.anomaly_detector_facade import AnomalyDetectorFacade
import click

CONFIGURATION_PREFIX = "LAD"


@click.group()
@click.option("--metric-port", default=8080, help="sets up metrics to publish ot custom port")
def cli(metric_port):
    """Cli bootstrap method."""
    start_http_server(metric_port)
    click.echo("starting up log anomaly detectory with metric_port: {}".format(metric_port))


@cli.command("ui")
@click.option("--debug", default=False, help="Sets flask in debug mode to true")
@click.option("--port", default=5001, help="Select the port number you would like to run the web ui ")
def ui(debug, port):
    """Start web ui for user feedback system."""
    click.echo("Starting UI...")
    app.run(debug=debug, port=port, host="0.0.0.0")


@cli.command("run")
@click.option(
    "--job-type",
    default="all",
    help="select either 'train', 'inference', 'all' by default it runs train and infer in loop", )
@click.option("--config-yaml", default=".env_config.yaml", help="configuration file used to configure service")
@click.option("--single-run", default=False, help="it will loop infinitely pause at interval if set to true")
# Initializing click function.
def run(job_type, config_yaml, single_run):
    """Perform machine learning model generation with input log data."""
    click.echo("Starting...")
    config = Configuration(prefix=CONFIGURATION_PREFIX, config_yaml=config_yaml)
    anomaly_detector = AnomalyDetectorFacade(config)
    click.echo("Created jobtype {}".format(job_type))

    if job_type == "train":
        click.echo("Performing training...")
        anomaly_detector.train()
    elif job_type == "inference":
        click.echo("Perform inference...")
        anomaly_detector.infer()
    elif job_type == "all":
        click.echo("Perform training and inference in loop...")
        anomaly_detector.run(single_run=single_run)


if __name__ == "__main__":
    cli(auto_envvar_prefix="LAD")
