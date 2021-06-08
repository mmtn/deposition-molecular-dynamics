import click
import sys
from src import io, Deposition


@click.command()
@click.option("--settings", "settings_filename", required=True, type=click.Path(exists=True))
@click.option("--log-filename", required=False, type=click.Path(), default="deposition.log")
def main(settings_filename, log_filename):
    """Starts logging, initiates the simulation, and runs the deposition loop.

    :param settings_filename: path to a YAML file which provides the settings for the deposition simulation
    :param log_filename: (optional; default="deposition.log") path to write the log file
    :return:
    """
    io.start_logging(log_filename=log_filename)
    deposition = Deposition.Deposition(settings_filename)
    return deposition.run_loop()


if __name__ == "__main__":
    sys.exit(main())
