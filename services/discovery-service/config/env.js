const dotenv = require('dotenv');
const path = require('path');
const { z } = require('zod');

dotenv.config({ path: path.join(__dirname, '../.env') });

const envSchema = z.object({
  PORT: z.string().default('5001').transform((val) => parseInt(val, 10)),
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  MONGO_URI: z.string().default('mongodb://localhost:27017/ai_discovery_service_db'),
  GEMINI_API_KEY: z.string().optional().default(''),
  GEMINI_MODEL: z.string().default('gemini-2.5-flash'),
  OBJECT_STORAGE_BASE_PATH: z.string().default('./storage/datasets'),
  RATE_LIMIT_WINDOW_MS: z.string().default('900000').transform((val) => parseInt(val, 10)),
  RATE_LIMIT_MAX: z.string().default('100').transform((val) => parseInt(val, 10))
});

const parseEnv = () => {
  const result = envSchema.safeParse(process.env);
  if (!result.success) {
    console.error('Invalid Discovery Service Environment Configuration:', result.error.format());
    process.exit(1);
  }
  return result.data;
};

const config = parseEnv();

module.exports = config;
