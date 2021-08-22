# pylint: skip-file
import json

from core.actions import HTTP
from core.log import LOG_PREFIX, logging
from core.rules import rule
from core.triggers import when
from personal.dateutils import DateUtils
from personal.item import Group, Item

logger = logging.getLogger('{}.AISensor'.format(LOG_PREFIX))

lock_until = {
    'all': DateUtils.now().minusSeconds(1)
}


def get_dataset(event):
    dataset = {}

    for aisensor_item in Group('AISensor', event):
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

    logger.debug('AISensor dataset: %s', dataset)

    return dataset


@rule('AISensor changed')
@when('System started')
@when('Member of AISensor changed')
def aisensor_changed(event):
    global lock_until
    if lock_until['all'].isAfter(DateUtils.now()):
        return

    lock_until['all'] = DateUtils.now().plusSeconds(50)

    dataset = get_dataset(event)
    data_json = json.dumps(dataset)

    logger.debug('%s', dataset)

    for dependent_item in Group('LearningHouse'):
        base_url = dependent_item.scripting('base_url')
        model_name = dependent_item.scripting('model_name')

        if model_name in lock_until and lock_until[model_name].isAfter(DateUtils.now()):
            continue

        lock_until[model_name] = DateUtils.now().plusSeconds(30)

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

        score_item = dependent_item.from_scripting('score_item')
        model_score = result['model']['score'] * 100
        score_item.post_update(model_score)

        dependent_item.set_label(
            dependent_item.scripting('label').format(model_score))


@rule('LearningHouse training')
@when('Member of LearningHouseTrain received command')
def learning_house_training(event):
    train_item = Item.from_event(event)
    train = train_item.get_onoff()

    dependent_item = train_item.from_scripting('dependent_item')
    dependent = dependent_item.get_onoff(True)

    base_url = dependent_item.scripting('base_url')
    model_name = dependent_item.scripting('model_name')

    if not train:
        dependent = not dependent

        global lock_until
        lock_until[model_name] = DateUtils.now().plusMinutes(30)

        if dependent:
            dependent_item.post_update(ON)
        else:
            dependent_item.post_update(OFF)

    dataset = get_dataset(event)
    dataset[dependent_item.name] = dependent
    data_json = json.dumps(dataset)

    logger.debug(data_json)

    response_json = HTTP.sendHttpPutRequest(
        '{}/training/{}'.format(base_url, model_name), 'application/json', data_json)

    result = json.loads(response_json)

    logger.info('Trained {} results in score {:.1f}'.format(
        model_name, result['score'] * 100))

    train_item.post_update(NULL)
