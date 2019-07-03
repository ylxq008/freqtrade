"""
Various tool function for Freqtrade and scripts
"""
import gzip
import logging
import re
from datetime import datetime

import numpy as np
import rapidjson


logger = logging.getLogger(__name__)


def shorten_date(_date: str) -> str:
    """
    Trim the date so it fits on small screens
    """
    new_date = re.sub('seconds?', 'sec', _date)
    new_date = re.sub('minutes?', 'min', new_date)
    new_date = re.sub('hours?', 'h', new_date)
    new_date = re.sub('days?', 'd', new_date)
    new_date = re.sub('^an?', '1', new_date)
    return new_date


############################################
# Used by scripts                          #
# Matplotlib doesn't support ::datetime64, #
# so we need to convert it into ::datetime #
############################################
def datesarray_to_datetimearray(dates: np.ndarray) -> np.ndarray:
    """
    Convert an pandas-array of timestamps into
    An numpy-array of datetimes
    :return: numpy-array of datetime
    """
    return dates.dt.to_pydatetime()


def file_dump_json(filename, data, is_zip=False) -> None:
    """
    Dump JSON data into a file
    :param filename: file to create
    :param data: JSON Data to save
    :return:
    """
    logger.info(f'dumping json to "{filename}"')

    if is_zip:
        if not filename.endswith('.gz'):
            filename = filename + '.gz'
        with gzip.open(filename, 'w') as fp:
            rapidjson.dump(data, fp, default=str, number_mode=rapidjson.NM_NATIVE)
    else:
        with open(filename, 'w') as fp:
            rapidjson.dump(data, fp, default=str, number_mode=rapidjson.NM_NATIVE)

    logger.debug(f'done json to "{filename}"')


def json_load(datafile):
    """
    load data with rapidjson
    Use this to have a consistent experience,
    sete number_mode to "NM_NATIVE" for greatest speed
    """
    return rapidjson.load(datafile, number_mode=rapidjson.NM_NATIVE)


def file_load_json(file):

    gzipfile = file.with_suffix(file.suffix + '.gz')

    # Try gzip file first, otherwise regular json file.
    if gzipfile.is_file():
        logger.debug('Loading ticker data from file %s', gzipfile)
        with gzip.open(gzipfile) as tickerdata:
            pairdata = json_load(tickerdata)
    elif file.is_file():
        logger.debug('Loading ticker data from file %s', file)
        with open(file) as tickerdata:
            pairdata = json_load(tickerdata)
    else:
        return None
    return pairdata


def format_ms_time(date: int) -> str:
    """
    convert MS date to readable format.
    : epoch-string in ms
    """
    return datetime.fromtimestamp(date/1000.0).strftime('%Y-%m-%dT%H:%M:%S')


def deep_merge_dicts(source, destination):
    """
    Values from Source override destination, destination is returned (and modified!!)
    Sample:
    >>> a = { 'first' : { 'rows' : { 'pass' : 'dog', 'number' : '1' } } }
    >>> b = { 'first' : { 'rows' : { 'fail' : 'cat', 'number' : '5' } } }
    >>> merge(b, a) == { 'first' : { 'rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
    True
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            deep_merge_dicts(value, node)
        else:
            destination[key] = value

    return destination


def plural(num, singular: str, plural: str = None) -> str:
    return singular if (num == 1 or num == -1) else plural or singular + 's'


def symbol_is_pair(symbol: str, base_currency: str = None, quote_currency: str = None):
    """
    Check if the symbol is a pair, i.e. consists of the base currency and the quote currency
    separated by '/' character. If base_currency and/or quote_currency is passed, it also checks
    that the symbol contains appropriate base and/or quote currency part before and after
    the separating character correspondingly.
    """
    symbol_parts = symbol.split('/')
    return (len(symbol_parts) == 2 and
            (symbol_parts[0] == base_currency if base_currency else len(symbol_parts[0]) > 0) and
            (symbol_parts[1] == quote_currency if quote_currency else len(symbol_parts[1]) > 0))
