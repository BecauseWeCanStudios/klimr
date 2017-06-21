FROM nginx:1.11

# Add start script
ADD docker_services/webserver/config/start.sh /
RUN chmod +x start.sh

# Add nginx config file
ADD docker_services/webserver/config/nginx.tmpl /

# Execute start script
CMD ["./start.sh"]
