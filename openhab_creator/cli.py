import click

from . import __version__
from openhab_creator.creator import Creator


@click.command()
@click.argument('configfile', type=click.File('rb'))
@click.argument('outputdir', envvar="OPENHAB_CONFIGDIR", type=click.Path(exists=True))
@click.option('-s', '--secrets', 'secretsfile', required=False, type=click.File('r'), )
@click.option('-c', '--check-only', 'check_only', is_flag=True, default=False)
def cli(**kwargs):
    creator = Creator(**kwargs)
    creator.run()


if __name__ == '__main__':
    cli(prog_name='openhab_creator')
