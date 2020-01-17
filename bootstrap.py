import argparse

from sanic.log import logger

from dash import dash


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Boot a Dash server')
    parser.add_argument('-a', '--address', action='store', default='0.0.0.0',
                        help='Dash address')
    parser.add_argument('-p', '--port', action='store', help='Dash port', default=3000, type=int)
    parser.add_argument('-c', '--config', action='store', help='Config file path')

    args = parser.parse_args()

    try:
        dash.main(args)
    except KeyboardInterrupt:
        logger.info('Shutting down...')
