FROM --platform=arm64 node:16.13.0-buster-slim AS frontend

WORKDIR /frontend

COPY package.json package-lock.json ./

RUN npm install

COPY . .

RUN npm run build

CMD [ "npm", "start" ]