FROM node:20-alpine AS builder

WORKDIR /app

ARG REACT_APP_API_URL
ENV VITE_API_URL=$REACT_APP_API_URL

COPY package.json package-lock.json* ./
RUN npm ci --silent

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
