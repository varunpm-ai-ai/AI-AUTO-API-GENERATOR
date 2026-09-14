/**
 * Automated Verification Tests for API Gateway Microservice
 */
const test = require('node:test');
const assert = require('node:assert');

const app = require('../index');
const API_CONSTANTS = require('../constants/apiConstants');

test('API Gateway Health & Spec Endpoints', async (t) => {
  let server;
  const testPort = 4099;

  await t.test('Start test server instance', () => {
    return new Promise((resolve) => {
      server = app.listen(testPort, () => {
        resolve();
      });
    });
  });

  await t.test('GET /health returns HTTP 200 with status UP', async () => {
    const res = await fetch(`http://localhost:${testPort}/health`);
    assert.strictEqual(res.status, 200);
    const body = await res.json();
    assert.strictEqual(body.success, true);
    assert.strictEqual(body.data.status, 'UP');
    assert.strictEqual(body.data.service, 'api-gateway');
  });

  await t.test('GET /api/v1/gateway/info returns edge capabilities', async () => {
    const res = await fetch(`http://localhost:${testPort}/api/v1/gateway/info`);
    assert.strictEqual(res.status, 200);
    const body = await res.json();
    assert.strictEqual(body.success, true);
    assert.strictEqual(body.data.service, 'API Gateway');
    assert.ok(Array.isArray(body.data.edge_capabilities));
  });

  await t.test('Gateway injects Request-ID and Correlation-ID headers', async () => {
    const res = await fetch(`http://localhost:${testPort}/health`);
    const requestId = res.headers.get('x-request-id');
    const correlationId = res.headers.get('x-correlation-id');
    assert.ok(requestId, 'x-request-id header should be present');
    assert.ok(correlationId, 'x-correlation-id header should be present');
  });

  await t.test('Close test server instance', () => {
    return new Promise((resolve) => {
      server.close(resolve);
    });
  });
});
