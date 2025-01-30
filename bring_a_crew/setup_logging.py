
def setup_logging():
    import logging
    import sys

    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s %(name)s [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )