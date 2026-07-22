FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG VITE_API_URL=/api
ARG VITE_RECOMMENDER_URL=/api/v1
ARG VITE_ASSISTANT_URL=/api/assistant

ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_RECOMMENDER_URL=${VITE_RECOMMENDER_URL}
ENV VITE_ASSISTANT_URL=${VITE_ASSISTANT_URL}

RUN npm run build

FROM nginx:1.28-alpine

COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html

RUN rm -f /etc/nginx/conf.d/default.conf

EXPOSE 80 443
