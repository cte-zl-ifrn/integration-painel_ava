import multiprocessing
import os

wsgi_app = "wsgi:application"
bind_port = os.getenv("VIRTUAL_PORT", "8000")
bind = f"0.0.0.0:{bind_port}"
default_web_concurrency = multiprocessing.cpu_count() * int(os.getenv("WORKER_PER_CPU", 2)) + 1
workers = int(os.getenv("WEB_CONCURRENCY", default_web_concurrency))
worker_class = os.getenv("WORKER_CLASS", "sync")
worker_tmp_dir = "/dev/shm"
loglevel = "info"
timeout = int(os.getenv("WORKER_TIMEOUT", 120))
error_logfile = "-"
errorlog = "-"
accesslog = "-"
capture_output = False
syslog = False
logger_class = "gunicorn.glogging.Logger"
