from private.parse import parse_yaml

DB_CONFIG = parse_yaml('private', 'config.yaml')['database']
