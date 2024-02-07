import logging

def setup_logging():
    logging.basicConfig(filename='log.txt', 
                        filemode='a',  # a: append, w: overwrite
                        format='%(asctime)s: %(message)s', 
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO,
                        encoding='utf-8')