from private.parse import parse_yaml, parse_json

DB_CONFIG = parse_yaml('private', 'config.yaml')['database']

__auth_config = parse_json('private', 'client_secret.json')

AUTH_CONFIG = {
    "token_uri": __auth_config['web']['token_uri'],
    "client_secret": __auth_config['web']['client_secret']
}