FROM node:18
WORKDIR /app
COPY . .
RUN npm init -y
EXPOSE 3000
CMD ["node", "app.js"]
