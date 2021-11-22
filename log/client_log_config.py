import logging
from pathlib import Path
from datetime import date

CLIENT_LOG = logging.getLogger('client.app')
FORMATTER = logging.Formatter("%(asctime)-25s %(levelname)s - %(module)s | %(message)s")
TODAY = str(date.today())
# FILES_COUNT = len(sorted(Path('.').glob(f'{TODAY}-server-*.log')))
FILE_HANDLER = logging.FileHandler(f'{TODAY}-client.log', encoding='utf8')
FILE_HANDLER.setLevel(logging.DEBUG)
FILE_HANDLER.setFormatter(FORMATTER)
CLIENT_LOG.addHandler(FILE_HANDLER)
CLIENT_LOG.setLevel(logging.DEBUG)

STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setFormatter(FORMATTER)
CLIENT_LOG.addHandler(STREAM_HANDLER)
