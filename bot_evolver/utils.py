import logging

def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)

# usage:
# setup_logger('log1', 'log1.log')
# setup_logger('log2', 'log2.log', logging.ERROR)

# now, you can get the logger and use it in your code
# logger1 = logging.getLogger('log1')
# logger1.info('This is an information message.')
# logger2 = logging.getLogger('log2')
# logger2.error('This is an error message.')

# https://stackoverflow.com/questions/11232230/logging-to-two-files-with-different-settings
# https://stackoverflow.com/questions/15727420/using-python-logging-in-multiple-modules