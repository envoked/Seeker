from django.conf import settings

#!/usr/bin/env python
import logging

def getLogger(filename):
    LOG = logging.getLogger(filename)
    LOG.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    hn = logging.FileHandler(settings.LOGGING_PATH + filename + ".log")
    LOG.addHandler(hn)
    hn.setFormatter(formatter)
    return LOG