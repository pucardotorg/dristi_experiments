# Use the official Nginx image as the base image
FROM nginx:alpine

# Copy the static website files to the Nginx web root directory
COPY . /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]