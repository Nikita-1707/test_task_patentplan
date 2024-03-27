import logging
from sys import stdout

log = logging.getLogger('TenderplanLogger')

log.setLevel(logging.DEBUG)

logFormatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
consoleHandler = logging.StreamHandler(stdout)
consoleHandler.setFormatter(logFormatter)

log.addHandler(consoleHandler)
