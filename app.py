""" Log Anomaly Detector"""
import click
from anomaly_detector.anomaly_detector import AnomalyDetector
from anomaly_detector.config import Configuration

CONFIGURATION_PREFIX = "LAD"

@click.group()
def cli():
    """Cli for log anomaly detector """
    click.echo("starting up log anomaly detectory")



@cli.command('run')
@click.option("--job-type",default="all",
              help="select either 'train', 'inference', 'all' "+
                   "by default it runs train and infer in loop")
@click.option("--config-yaml", default=".env_config.yaml",
              help="configuration file used to configure service")
def run(job_type, config_yaml):
    """ Performs machine learning model generation
    with input log data"""
    click.echo("Starting...")
    config = Configuration(prefix=CONFIGURATION_PREFIX,
                           config_yaml=config_yaml)
    anomaly_detector = AnomalyDetector(config)
    click.echo('Created jobtype {}'.format(job_type))


    if job_type == 'train':
        click.echo("Performing training...")
        anomaly_detector.train()
    elif job_type == 'inference':
        click.echo("Perform inference...")
        anomaly_detector.infer()
    elif job_type == 'all':
        click.echo("Perform training and inference in loop...")
        anomaly_detector.run()



if __name__ == "__main__":
   cli(auto_envvar_prefix='LAD')
