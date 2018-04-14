import sys

##
## Name: name
## Type: string
## Required: no
## Default: "esp8266"
## Description: The name of the logger instance.  This name will be provided 
## as a component to all log messages sent through this logger instance.
## Example:
name="uPyEasy"


##
## Name: levels
## Type: [level], where level is one of: 'debug', 'info', 'warning', 'error'
## Required: no
## Default: ['info', 'warning', 'error']
## Description: The list of log levels to log to
## Example:
levels=['debug', 'info', 'warning', 'error']

##
## Name: sinks
## Type: Dictionary 
## Required: no
## Default: {'console': None}
## Description: A specification of the sinks to instantiate in this logger instance.
## This dictionary is of the form {<name>: <config>}, where <name> is a sink name
## corresponding to a module called <name>_sink, and <config>
## is a dictionary (or None) whose structure is specific to the sink type.
## Example:
sinks = {
    'console': {
        'output': sys.stderr,
        'level': 1
    },
    'syslog': {
        'host': '0.0.0.0',
        'port': 514,
        'level': 0
    },
    'log': {
        'buffersize': 25,
        'level': 0
    },
}

