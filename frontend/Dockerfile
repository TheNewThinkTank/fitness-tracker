FROM node:26.10.0-alpine@sha256:0b36e8c136b94cd4fcf02188228e76c31ad5872eef3fec8cbd2eee500cfd9e80 AS dependencies

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM dependencies AS development

COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM dependencies AS build

COPY . .
RUN npm run check && npm test && npm run build

FROM nginxinc/nginx-unprivileged:1.30.4-alpine-slim@sha256:11f3f6249b4ae3d7a4ec2a51797060107b88ead52b33b6ed3c6c33f55ca96200 AS runtime

LABEL org.opencontainers.image.title="Fitness Tracker Frontend" \
	org.opencontainers.image.version="0.1.0" \
	org.opencontainers.image.source="https://github.com/TheNewThinkTank/fitness-tracker" \
	org.opencontainers.image.licenses="MIT"

ENV NGINX_ENVSUBST_FILTER="^FITNESS_TRACKER_API_TOKEN$" \
	NGINX_ENVSUBST_OUTPUT_DIR=/tmp

USER root
RUN rm -f /etc/nginx/conf.d/default.conf

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
COPY default.conf.template /etc/nginx/templates/default.conf.template

USER 101

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
	CMD ["wget", "--quiet", "--output-document=-", "http://127.0.0.1:8080/healthz"]
