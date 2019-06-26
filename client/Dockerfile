FROM node:10-alpine

RUN apk --no-cache add rsync
WORKDIR /app
COPY ./package.json ./yarn.lock ./
# Install dependencies, don't build the project on postinstall
RUN NOYARNBUILD=1 yarn install

COPY . .
CMD npm run watch
