#get the latest alpine image from node registry
FROM node:18-alpine AS dependencies
# RUN npm i -g yarn
#set the working directory
    
WORKDIR /app
#copy the package and package lock files
#from local to container work directory /app
COPY package.json /app/

#Run command npm install to install packages
RUN yarn

#copy all the folder contents from local to container & build
FROM node:18-alpine AS builder

ARG NEXT_PUBLIC_API_BASE_URL
ARG NEXT_PUBLIC_WEBSOCKET_URL
ARG NEXT_PUBLIC_REPORT_ISSUE_API

    
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_WEBSOCKET_URL=$NEXT_PUBLIC_WEBSOCKET_URL
ENV NEXT_PUBLIC_REPORT_ISSUE_API=$NEXT_PUBLIC_REPORT_ISSUE_API

    
WORKDIR /app
    
COPY . .

    
COPY --from=dependencies /app/node_modules ./node_modules

    
RUN yarn run build
    
#specify env variables at runtime
FROM node:18-alpine AS runner
WORKDIR /app

# If you are using a custom next.config.js file, uncomment this line.
# COPY --from=builder next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

    
EXPOSE 3000    
CMD ["yarn", "start"]
