/**
 * Structured Logger Module for API Gateway
 */
const config = require('./env');

const formatMessage = (level, message, meta = {}) => {
  const timestamp = new Date().toISOString();
  return JSON.stringify({
    timestamp,
    service: 'api-gateway',
    level: level.toUpperCase(),
    env: config.NODE_ENV,
    message,
    ...meta
  });
};

const logger = {
  info: (msg, meta) => console.log(formatMessage('info', msg, meta)),
  error: (msg, meta) => console.error(formatMessage('error', msg, meta)),
  warn: (msg, meta) => console.warn(formatMessage('warn', msg, meta)),
  debug: (msg, meta) => {
    if (config.NODE_ENV !== 'production') {
      console.log(formatMessage('debug', msg, meta));
    }
  }
};

module.exports = logger;
