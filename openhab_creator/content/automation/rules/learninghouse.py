# pylint: skip-file
import json

from core.actions import HTTP
from core.log import LOG_PREFIX, logging
from core.rules import rule
from core.triggers import when
from personal.dateutils import DateUtils
from personal.item import Item

logger = logging.getLogger('{}.AISensor'.format(LOG_PREFIX))

lock_until = DateUtils.now().minusSeconds(1)


def get_dataset(event):
    dataset = {}

    for aisensor in ir.getItem('AISensor').members:
        aisensor_item = Item(aisensor, event)
        aisensor_value = aisensor_item.get_value()

        if isinstance(aisensor_value, QuantityType) or isinstance(aisensor_value, DecimalType):
            dataset[aisensor_item.name] = aisensor_value.floatValue()
        elif isinstance(aisensor_value, StringType):
            dataset[aisensor_item.name] = aisensor_value.toFullString()
        elif isinstance(aisensor_value, OnOffType):
            dataset[aisensor_item.name] = aisensor_value == ON
        elif aisensor_value is None:
            dataset[aisensor_item.name] = None
        else:
            logger.warn('unknown AISensor type {}'.format(
                type(aisensor_value)))

    return dataset


@rule('AISensor changed')
@when('System started')
@when('Member of AISensor changed')
def aisensor_changed(event):
    global lock_until
    if lock_until.isAfter(DateUtils.now()):
        return

    lock_until = DateUtils.now().plusSeconds(50)

    dataset = get_dataset(event)
    data_json = json.dumps(dataset)

    logger.debug('%s', dataset)

    for dependent in ir.getItem('LearningHouse').members:
        dependent_item = Item(dependent)

        base_url = dependent_item.scripting('base_url')
        model_name = dependent_item.scripting('model_name')

        response_json = HTTP.sendHttpPostRequest(
            '{}/prediction/{}'.format(base_url, model_name), 'application/json', data_json)

        result = json.loads(response_json)

        logger.debug(u"{} => {} {:.2f} (model score: {:.2f})".format(
            data_json, model_name, result['prediction'], result['model']['score']))
        logger.info(u"{}: {}".format(model_name, result['prediction']))

        if result['prediction']:
            dependent_item.post_update(ON)
        elif not result['prediction']:
            dependent_item.post_update(OFF)
