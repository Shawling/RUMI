import hashlib

token = 'rumi-wesmart'
signature, timestamp, nonce, echostr = (
    'b4c8608bb1d61a2ffdf061fa9d23c9e9b9d5854d', '1512369119', '2584527210',
    '10365580399901732863')
l1 = [token, timestamp, nonce]

l1 = ['1512369119', '2584527210', 'rumi-wesmart']
sorted(l1)
sha1 = hashlib.sha1()
print(l1)
# map(lambda x: sha1.update(x.encode('utf-8')), l1)
sha1.update('1512369119'.encode('utf-8'))
sha1.update('2584527210'.encode('utf-8'))
sha1.update('rumi-wesmart'.encode('utf-8'))
hashcode = sha1.hexdigest()
print(hashcode)

# coding: utf-8
''' 
@date: 2016-10-13 
@author: alex.lin 
'''
import logging


class LogLevelFilter(logging.Filter):
    def __init__(self, name='', level=logging.DEBUG):
        super(LogLevelFilter, self).__init__(name)
        self.level = level

    def filter(self, record):
        return record.levelno == self.level


# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

fh_info = logging.FileHandler('logging_info.log')
fh_info.setLevel(logging.INFO)

fh_debug = logging.FileHandler('logging_debug.log')
fh_debug.setLevel(logging.DEBUG)

filter_info = LogLevelFilter(level=logging.INFO)
filter_debug = LogLevelFilter(level=logging.DEBUG)

fh_info.addFilter(filter_info)
fh_debug.addFilter(filter_debug)

logger.addHandler(fh_info)
logger.addHandler(fh_debug)

logger.debug('for debug')
logger.info('for info')
logger.error('for error')

{'a': 1, 'b': 2, 'c': 3}
