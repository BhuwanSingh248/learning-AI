import logging
import sys

def setup_logger(name: str = "stock_agent") -> logging.Logger:
    """
    Sets up and configures a central logger for the application.
    """
    logger = logging.getLogger(name)

    # Return if already configured to avoid duplicate logs
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)

    # Standard log format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger

# Create a central logger instance
logger = setup_logger()
