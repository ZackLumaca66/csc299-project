from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass
class PKMSConfig:
    data_dir: str
    backend: str
    neo4j_enabled: bool = False
    verbose: bool = False

def load_config(backend: str | None = None) -> PKMSConfig:
    env_backend = backend or os.getenv('PKMS_BACKEND', 'json')
    data_dir = os.getenv('PKMS_DATA_DIR', os.path.join(os.getcwd(), 'data_pkms'))
    neo4j_enabled = os.getenv('PKMS_NEO4J', '0') == '1'
    verbose = os.getenv('PKMS_VERBOSE', '0') == '1'
    os.makedirs(data_dir, exist_ok=True)
    return PKMSConfig(data_dir=data_dir, backend=env_backend, neo4j_enabled=neo4j_enabled, verbose=verbose)

__all__ = ["PKMSConfig","load_config"]