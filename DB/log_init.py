import logging
import logging.config

logging.config.fileConfig('../configs/log.conf')
logger = logging.getLogger('MedAssistLog')