# panda_catalog

[Unit]
Description=gunicorn daemon for app1
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/nginx/app1
ExecStart=/usr/local/bin/gunicorn --config /var/www/nginx/panda/gunicorn_config_app1.py app1.wsgi:application

[Install]
WantedBy=multi-user.target
