# Frontend Dockerfile for Create React App + craco
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json yarn.lock craco.config.js ./
COPY public ./public
COPY src ./src
RUN yarn install --frozen-lockfile
RUN yarn build

# Serve static build with nginx
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# For local dev, you may want to run the dev server instead of nginx static build
# Uncomment below for local dev:
# FROM node:20-alpine
# WORKDIR /app
# COPY package.json yarn.lock ./
# RUN yarn install --frozen-lockfile
# COPY . .
# EXPOSE 3000
# CMD ["yarn", "start"]
