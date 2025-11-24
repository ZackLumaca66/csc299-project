from __future__ import annotations
import logging

def init_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='[%(levelname)s] %(message)s')
    return logging.getLogger('pkms')

__all__ = ["init_logging"]