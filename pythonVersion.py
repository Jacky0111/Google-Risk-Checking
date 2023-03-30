import logging

# create a logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

# create a file handler and set its level to debug
fh = logging.FileHandler('my_log_file.log')
fh.setLevel(logging.DEBUG)

# create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

# add the file handler to the logger
logger.addHandler(fh)

# Example of exception handling code
try:
    result = 1 / 0
except Exception as e:
    # log the exception
    logger.exception('An exception occurred: %s', e)

# Example of exception handling code
try:
    file = open("nonexistent_file.txt", "r")
except Exception as e:
    # log the exception
    logger.exception('An exception occurred: %s', e)
