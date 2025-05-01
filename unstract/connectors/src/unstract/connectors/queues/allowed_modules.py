# List of allowed modules that can be dynamically imported
ALLOWED_MODULES = {
    "unstract.connectors.queues.sqs",
    "unstract.connectors.queues.rabbitmq",
    # Add other legitimate modules here
}

def is_allowed_module(module_name):
    """Check if the module name is in the allowed list."""
    return module_name in ALLOWED_MODULES
