"""Log Anomaly Detector."""
from anomaly_detector.anomaly_detector import AnomalyDetector
from anomaly_detector.config import Configuration
from anomaly_detector.fact_store.app import app
import click

CONFIGURATION_PREFIX = "LAD"


@click.group()
def cli():
    """Cli bootstrap method."""
    click.echo("starting up log anomaly detectory")


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
    help="select either 'train', 'inference', 'all' by default it runs train and infer in loop",)
@click.option("--config-yaml", default=".env_config.yaml", help="configuration file used to configure service")
# Initializing click function.
def run(job_type, config_yaml):
    """Perform machine learning model generation with input log data."""
    click.echo("Starting...")
    config = Configuration(prefix=CONFIGURATION_PREFIX, config_yaml=config_yaml)
    anomaly_detector = AnomalyDetector(config)
    click.echo("Created jobtype {}".format(job_type))

    if job_type == "train":
        click.echo("Performing training...")
        anomaly_detector.train()
    elif job_type == "inference":
        click.echo("Perform inference...")
        anomaly_detector.infer()
    elif job_type == "all":
        click.echo("Perform training and inference in loop...")
        anomaly_detector.run()


if __name__ == "__main__":
    cli(auto_envvar_prefix="LAD")
