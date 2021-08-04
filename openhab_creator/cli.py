import click
import click_log

from openhab_creator.creator import Creator

from . import __version__, logger

click_log.basic_config(logger)


@click.command()
@click.argument('name', required=True)
@click.argument('configdir', type=click.Path(exists=True))
@click.argument('outputdir', envvar="OPENHAB_CONFIGDIR", type=click.Path(exists=True))
@click.option('--anonym', 'anonym', is_flag=True, default=False)
@click.option('--check-only', 'check_only', is_flag=True, default=False)
@click.option('--icons', 'icons', is_flag=True, default=False)
@click_log.simple_verbosity_option(logger)
def cli(**kwargs):
    creator = Creator(**kwargs)
    creator.run()


if __name__ == '__main__':
    cli(prog_name='openhab_creator')
