# VK CHAT BOT FOR COMMUNITIES

It is simple bot based on vk_api package which works with VK API.

To set up CallBack we need to configure gunicorn and Nginx.

## Install requirements

Python packages:
```
pip install -r requirements.txt
```
Linux packages
```
sudo apt-get update ; \
sudo apt install -y nginx supervisor
```

## Configure supervisor
Make bash-script executable:
```
chmod +x {project_path}/bin/start_gunicorn.sh
```
Edit supervisor congif file:
```
vim /etc/supervisor/conf.d/erjan.conf
	[program:gunicorn]
	command=/home/me/erjan/bin/start_gunicorn.sh
	user=me
	process_name=%(program_name)s
	numprocs=1
	autostart=true
	autorestart=true
	redirect_stderr=true
	
sudo service supervisor restart
```

## Configure Nginx
```
sudo vim /etc/nginx/conf.d/default
    server {
            listen 80 default_server;
            listen [::]:80 default_server;
    
            root /var/me/html;
    
            index index.html index.htm, index.nginx-debian.html;
    
            server_name _;
    
            location / {
                    proxy_pass http://127.0.0.1:8001;
                    proxy_set_header X-Forwarded-Host $server_name;
                    proxy_set_header X-Real-IP $remote_addr;
                    add_header P3P 'CP="ALL DSP COR PSAa PSDa OUR NOR ONL UNI COm NAV"';
                    add_header Access-Control-Allow-Origin *;
            }
    }
    
sudo service nginx restart
```