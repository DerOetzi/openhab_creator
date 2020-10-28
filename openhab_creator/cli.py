import click

from . import __version__

@click.command()
def cli(**kwargs):
    print(__version__)
