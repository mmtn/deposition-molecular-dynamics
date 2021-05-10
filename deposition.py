import click
import sys
from src import io, Deposition


@click.command()
@click.option("--settings", "settings_filename", required=True, type=click.Path(exists=True))
@click.option("--command-prefix", required=False, type=click.STRING, default="")
@click.option("--log-filename", required=False, type=click.Path(), default="deposition.log")
def main(settings_filename, command_prefix, log_filename):
    io.start_logging(log_filename=log_filename)  # TODO make sure logging is working everywhere
    deposition = Deposition.Deposition(settings_filename, command_prefix)
    return deposition.run_loop()


if __name__ == "__main__":
    sys.exit(main())
