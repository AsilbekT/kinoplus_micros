import multiprocessing

bind = 'unix:/tmp/panda_catalog.sock'
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = '/var/www/panda_catalog/logs/access.log'
errorlog = '/var/www/panda_catalog/logs/error.log'
loglevel = 'info'
limit_request_line = 8190 