# pylint: skip-file
from core.log import LOG_PREFIX, logging
from core.rules import rule
from core.triggers import when
from personal.dateutils import DateUtils
from personal.item import Item, Group

import personal.item
reload(personal.item)

logger = logging.getLogger('{}.GasStation'.format(LOG_PREFIX))

FUELTYPE_GROUPS = ['DieselPrices', 'E10Prices', 'E5Prices']


@rule('Fuel prices colors')
@when('System started')
@when('Member of DieselPrices changed')
@when('Member of E10Prices changed')
@when('Member of E5Prices changed')
@when('Member of GasStationOpened changed')
def fuelprices(event):
    for fueltype_group in FUELTYPE_GROUPS:
        prices_group = Group(fueltype_group, event)
        min_price = int(prices_group.item.get_float(0.0) * 100)

        for price_item in prices_group:
            opened_item = price_item.from_scripting('opened_item')
            difference_item = price_item.from_scripting('difference_item')

            if opened_item.get_openclosed():
                price = int(price_item.get_float(0.0) * 100)
                logger.debug('%s: %d - %d', price_item, price, min_price)
                difference_item.post_update(price - min_price)
            else:
                logger.debug('%s: closed', price_item)
                difference_item.post_update(-1)
