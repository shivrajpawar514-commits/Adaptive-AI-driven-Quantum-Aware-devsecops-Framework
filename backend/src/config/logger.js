const winston = require('winston');
const path = require('path');
const fs = require('fs');

const logDir = path.join(__dirname, '../../logs');
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}

const levels = {
  error: 0,
  warn: 1,
  info: 2,
  http: 3,
  debug: 4
};

const colors = {
  error: 'red',
  warn: 'yellow',
  info: 'green',
  http: 'magenta',
  debug: 'white'
};

winston.addColors(colors);

const format = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss:ms' }),
  winston.format.printf(
    (info) => `[${info.timestamp}] [${info.level.toUpperCase()}]: ${info.message}`
  )
);

const transports = [
  new winston.transports.Console({
    format: winston.format.combine(
      winston.format.colorize({ all: true }),
      winston.format.printf(
        (info) => `[${info.timestamp}] [${info.level}]: ${info.message}`
      )
    )
  }),
  new winston.transports.File({
    filename: path.join(logDir, 'backend-error.log'),
    level: 'error',
    format: winston.format.json()
  }),
  new winston.transports.File({
    filename: path.join(logDir, 'backend-combined.log'),
    format: winston.format.json()
  })
];

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  levels,
  format,
  transports
});

module.exports = logger;
