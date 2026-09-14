const dotenv = require('dotenv');
const path = require('path');
const { z } = require('zod');

dotenv.config({ path: path.join(__dirname, '../.env') });

const envSchema = z.object({
  PORT: z.string().default('4000').transform((val) => parseInt(val, 10)),
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  MONGO_URI: z.string().default('mongodb://localhost:27017/ai_api_gateway_db'),
  JWT_SECRET: z.string().default('super_secret_gateway_jwt_key_2026_change_in_production'),
  JWT_EXPIRES_IN: z.string().default('7d'),
  API_KEY_SALT: z.string().default('gateway_secure_salt_key_98765'),
  DISCOVERY_SERVICE_URL: z.string().default('http://localhost:5001'),
  WORKSPACE_SERVICE_URL: z.string().default('http://localhost:5002'),
  GATEWAY_PREFIX: z.string().default('/api/v1/gateway'),
  RATE_LIMIT_WINDOW_MS: z.string().default('900000').transform((val) => parseInt(val, 10)),
  RATE_LIMIT_MAX: z.string().default('100').transform((val) => parseInt(val, 10)),
  ALLOWED_ORIGINS: z.string().default('*')
});

const parseEnv = () => {
  const result = envSchema.safeParse(process.env);
  if (!result.success) {
    console.error('Invalid Gateway Environment Configuration:', result.error.format());
    process.exit(1);
  }
  return result.data;
};

const config = parseEnv();

module.exports = config;
