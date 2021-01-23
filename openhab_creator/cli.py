import click

from . import __version__
from openhab_creator.creator import Creator


@click.command()
@click.argument('name', required=True)
@click.argument('configdir', type=click.Path(exists=True))
@click.argument('outputdir', envvar="OPENHAB_CONFIGDIR", type=click.Path(exists=True))
@click.option('--anonym', 'anonym', is_flag=True, default=False)
@click.option('--all', 'all', is_flag=True, default=False)
@click.option('--check-only', 'check_only', is_flag=True, default=False)
@click.option('--icons', 'icons', is_flag=True, default=False)
@click.option('--automation', '--automation', 'automation', is_flag=True, default=False)
def cli(**kwargs):
    creator = Creator(**kwargs)
    creator.run()


if __name__ == '__main__':
    cli(prog_name='openhab_creator')
