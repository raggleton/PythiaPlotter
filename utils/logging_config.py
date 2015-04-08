"""Setup logging module here"""

import logging

console_handler = logging.StreamHandler()

root = logging.getLogger()
root.addHandler(console_handler)
root.setLevel(logging.INFO)
