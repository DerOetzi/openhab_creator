import click

from . import __version__
from .creator import run

@click.command()
@click.argument('configfile', type=click.File('rb'))
@click.argument('outputdir', envvar="OPENHAB_CONFIGDIR", type=click.Path(exists=True))
def cli(**kwargs):
    run(**kwargs)

if __name__ == '__main__':
    cli(prog_name='openhab_creator')