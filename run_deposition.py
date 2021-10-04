import click
import sys
import deposition


@click.command()
@click.option("--settings", "settings_filename", required=True, type=click.Path(exists=True))
def main(settings_filename):
    settings = deposition.io.read_settings_from_file(settings_filename)
    calculation = deposition.Deposition.Deposition(settings)
    return calculation.run()


if __name__ == "__main__":
    sys.exit(main())
