import logging

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def get_logger(name):
    """
    Returns a logger instance with the specified name.
    """
    return logging.getLogger(name)
