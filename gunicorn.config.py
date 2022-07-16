from multiprocessing import cpu_count
from os import getenv as env

from service import log, settings

# The socket to bind.
host = env("HOST", "0.0.0.0")
port = int(env("PORT", "8080"))
bind = f"{host}:{port}"

# The maximum number of pending connections.
backlog = env("GUNICORN_BACKLOG", 2048)

# The number of worker processes for handling requests.
workers = env("GUNICORN_WORKERS", cpu_count())

# The type of workers to use.
worker_class = env("GUNICORN_WORKER_CLASS", "uvicorn.workers.UvicornWorker")

# The maximum number of requests a worker will process before restarting.
max_requests = env("GUNICORN_MAX_REQUESTS", 1024)

# Workers silent for more than this many seconds are killed and restarted.
timeout = env("GUNICORN_TIMEOUT", 3600)

# Timeout for graceful workers restart.
graceful_timeout = env("GUNICORN_GRACEFUL_TIMEOUT", 5)

# The number of seconds to wait for requests on a Keep-Alive connection.
keepalive = env("GUNICORN_KEEPALIVE", 5)

# Detaches the server from the controlling terminal and enters the background.
daemon = env("GUNICORN_DAEMON", False)

# Check the configuration.
check_config = env("GUNICORN_CHECK_CONFIG", False)

# A base to use with setproctitle for process naming.
proc_name = env("GUNICORN_PROC_NAME", "vertical")

# Internal setting that is adjusted for each type of application.
default_proc_name = env("GUNICORN_DEFAULT_PROC_NAME", "vertical")

# The Access log file to write to.
accesslog = env("GUNICORN_ACCESS_LOG", "-")

# The access log format.
access_log_format = env("GUNICORN_ACCESS_LOG_FORMAT", None)

# The Error log file to write to.
errorlog = env("GUNICORN_ERRORLOG", "-")

# The granularity of log output.
loglevel = env("GUNICORN_LOGLEVEL", "INFO")

# Redirect stdout/stderr to specified file in errorlog.
capture_output = env("GUNICORN_CAPTURE_OUTPUT", False)

# The log config dictionary to use.
logconfig_dict = log.get_config(settings.get_config())

# The maximum size of HTTP request line in bytes.
# This parameter can be used to prevent any DDOS attack.
limit_request_line = env("GUNICORN_LIMIT_REQUEST_LINE", 512)

# Limit the number of HTTP headers fields in a request.
# This parameter is used to limit the number of headers in a request.
limit_request_fields = env("GUNICORN_LIMIT_REQUEST_FIELDS", 64)

# Limit the allowed size of an HTTP request header field.
# Setting it to 0 will allow unlimited header field sizes.
limit_request_field_size = env("GUNICORN_LIMIT_REQUEST_FIELD_SIZE", 128)

# Load application code before the worker processes are forked.
preload_app = env("GUNICORN_PRELOAD_APP", False)

# Disables the use of sendfile.
sendfile = env("GUNICORN_SENDFILE", True)

# Set the SO_REUSEPORT flag on the listening socket.
reuse_port = env("GUNICORN_REUSE_PORT", True)

# A filename to use for the PID file.
# If not set, no PID file will be written.
pidfile = env("GUNICORN_PIDFILE", None)

# A directory to use for the worker heartbeat temporary file.
# If not set, the default temporary directory will be used.
worker_tmp_dir = env("GUNICORN_WORKER_TMP_DIR", None)

# Switch worker processes to run as this user.
user = env("GUNICORN_USER", None)

# Switch worker process to run as this group.
group = env("GUNICORN_GROUP", None)

# If true, set the worker process’s group access list with all of the groups
# of which the specified username is a member, plus the specified group id.
initgroups = env("GUNICORN_INITGROUPS", None)

# Directory to store temporary request data as they are read.
tmp_upload_dir = env("GUNICORN_TMP_UPLOAD_DIR", None)

# Front-end’s IPs from which allowed to handle set secure headers.
forwarded_allow_ips = env("GUNICORN_FORWARDER_ALLOW_IPS", "127.0.0.1")
