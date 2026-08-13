# digital-twin/src/logger.py
import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/app/data/twin.log')
        ]
    )
    return logging.getLogger(__name__)
