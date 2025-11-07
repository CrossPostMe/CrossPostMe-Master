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
