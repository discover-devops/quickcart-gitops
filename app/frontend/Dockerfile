# nginx-unprivileged runs as non-root and listens on port 8080
FROM nginxinc/nginx-unprivileged:1.27-alpine

COPY index.html /usr/share/nginx/html/index.html

# The shop name and banner come from a ConfigMap mounted at
# /usr/share/nginx/html/config/config.json. This default is used
# only when the ConfigMap is not mounted.
COPY config.json /usr/share/nginx/html/config/config.json

EXPOSE 8080
