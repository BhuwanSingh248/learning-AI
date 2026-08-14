import logging
import sys
import contextvars

# Context variable to hold the trace ID for the lifetime of a request
trace_id_var = contextvars.ContextVar("trace_id", default="-")

class TraceIdFilter(logging.Filter):
    """
    Filter to inject trace_id from context variables into log records.
    """
    def filter(self, record):
        record.trace_id = trace_id_var.get()
        return True

def setup_logger(name: str = "stock_agent") -> logging.Logger:
    """
    Sets up and configures a central logger for the application.
    """
    logger = logging.getLogger(name)

    # Return if already configured to avoid duplicate logs
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)

    # Standard log format with trace ID
    formatter = logging.Formatter(
        "%(asctime)s - [Trace: %(trace_id)s] - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addFilter(TraceIdFilter())

    return logger

# Create a central logger instance
logger = setup_logger()
