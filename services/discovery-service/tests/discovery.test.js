/**
 * Automated Verification Tests for Discovery Service Microservice
 */
const test = require('node:test');
const assert = require('node:assert');

const app = require('../index');
const catalogGrpcClient = require('../grpc/catalogClient');

test('Discovery Service Endpoints & Workflow', async (t) => {
  let server;
  const testPort = 5099;

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
    assert.strictEqual(body.data.service, 'discovery-service');
  });

  await t.test('POST /api/v1/discover initiates discovery workflow', async () => {
    const res = await fetch(`http://localhost:${testPort}/api/v1/discover`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: 'global climate temperature data', category: 'environment' })
    });
    assert.strictEqual(res.status, 201);
    const body = await res.json();
    assert.strictEqual(body.success, true);
    assert.strictEqual(body.data.status, 'ACQUIRED');
    assert.ok(body.data.planId, 'Plan ID should be generated');
    assert.ok(body.data.acquiredDatasetId, 'Acquired Dataset ID should be present');
  });

  await t.test('Catalog gRPC client handles offline server gracefully with fallback', async () => {
    const dupRes = await catalogGrpcClient.checkDuplicate('dummy-sha256-hash', '', 300);
    assert.strictEqual(dupRes.is_duplicate, false);
    assert.strictEqual(dupRes.fallback, true);

    const idRes = await catalogGrpcClient.resolveIdentity('NonExistent', '', '', 300);
    assert.strictEqual(idRes.is_existing, false);
    assert.strictEqual(idRes.fallback, true);
  });

  await t.test('Close test server instance', () => {
    catalogGrpcClient.close();
    return new Promise((resolve) => {
      server.close(resolve);
    });
  });
});
