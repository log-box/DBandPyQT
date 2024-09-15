import logging
import logging.handlers
import os.path
from pathlib import Path
from datetime import date
import sys

sys.path.append(os.path.join(os.getcwd(), '..'))
sys.path.append('../')
TODAY = str(date.today())
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, f'{TODAY}-server.log')

SERVER_LOG = logging.getLogger('server.app')
FORMATTER = logging.Formatter("%(asctime)-25s %(levelname)s - %(module)s | %(message)s")

# FILES_COUNT = len(sorted(Path('.').glob(f'{TODAY}-server-*.log')))
FILE_HANDLER = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf8', interval=1, when='D') #FileHandler(f'{TODAY}-server.log', encoding='utf8')
FILE_HANDLER.setLevel(logging.DEBUG)
FILE_HANDLER.setFormatter(FORMATTER)
SERVER_LOG.addHandler(FILE_HANDLER)
SERVER_LOG.setLevel(logging.DEBUG)


STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setFormatter(FORMATTER)
SERVER_LOG.addHandler(STREAM_HANDLER)
