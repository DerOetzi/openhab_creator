import click

from . import __version__
from openhab_creator.creator import Creator


@click.command()
@click.argument('name', required=True)
@click.argument('configdir', type=click.Path(exists=True))
@click.argument('outputdir', envvar="OPENHAB_CONFIGDIR", type=click.Path(exists=True))
@click.option('-a', '--anonym', 'anonym', is_flag=True, default=False)
@click.option('-b', '--basics', 'basics', is_flag=True, default=False)
@click.option('-c', '--check-only', 'check_only', is_flag=True, default=False)
@click.option('-i', '--icons', 'icons', is_flag=True, default=False)
@click.option('-r', '--rules', 'rules', is_flag=True, default=False)
def cli(**kwargs):
    creator = Creator(**kwargs)
    creator.run()


if __name__ == '__main__':
    cli(prog_name='openhab_creator')
