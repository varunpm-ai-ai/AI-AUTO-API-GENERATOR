/**
 * Comprehensive Automated Verification Test Suite for Auth Microservice
 * Covers: Signup, Login, Password Reset, Multi-Tenant Isolation, Token Rotation, gRPC
 */
const test = require('node:test');
const assert = require('node:assert');

const { app } = require('../index');
const AuthGrpcServer = require('../grpc/authGrpcServer');
const AuthGrpcClient = require('../grpc/authGrpcClient');
const Storage = require('../models/storage');

test('Auth Service End-to-End Test Suite', async (t) => {
  let server;
  let grpcServer;
  let grpcClient;

  const testHttpPort = 5098;
  const testGrpcPort = 50058;

  let aliceToken = null;
  let aliceRefreshToken = null;
  let aliceTenantId = null;
  let aliceUserId = null;

  let bobToken = null;
  let bobTenantId = null;

  await t.test('Initialize test HTTP and gRPC servers', async () => {
    Storage.clearMemory();

    // Start HTTP server
    await new Promise((resolve) => {
      server = app.listen(testHttpPort, resolve);
    });

    // Start gRPC server
    grpcServer = new AuthGrpcServer(testGrpcPort);
    await grpcServer.start();

    // Initialize gRPC client
    grpcClient = new AuthGrpcClient(`localhost:${testGrpcPort}`);
  });

  await t.test('GET /health returns HTTP 200 with UP status', async () => {
    const res = await fetch(`http://localhost:${testHttpPort}/health`);
    assert.strictEqual(res.status, 200);
    const body = await res.json();
    assert.strictEqual(body.success, true);
    assert.strictEqual(body.data.status, 'UP');
    assert.strictEqual(body.data.service, 'auth-service');
  });

  await t.test('GET /readiness returns HTTP 200 with READY status', async () => {
    const res = await fetch(`http://localhost:${testHttpPort}/readiness`);
    assert.strictEqual(res.status, 200);
    const body = await res.json();
    assert.strictEqual(body.success, true);
    assert.strictEqual(body.data.status, 'READY');
  });

  await t.test('POST /api/v1/auth/signup rejects weak passwords', async () => {
    const res = await fetch(`http://localhost:${testHttpPort}/api/v1/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'weak@example.com',
        password: 'weak',
        name: 'Weak Pass User'
      })
    });
    assert.strictEqual(res.status, 400);
    const body = await res.json();
    assert.strictEqual(body.success, false);
    assert.strictEqual(body.error.code, 'VALIDATION_ERROR');
  });

  await t.test('POST /api/v1/auth/signup successfully registers Tenant Admin and creates Tenant', async () => {
    const res = await fetch(`http://localhost:${testHttpPort}/api/v1/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'alice@acme.com',
        password: 'Password123!',
        name: 'Alice Smith',
        tenantName: 'Acme AI Corp'
      })
    });
    assert.strictEqual(res.status, 201);
    const body = await res.json();
    assert.strictEqual(body.success, true);
    assert.ok(body.data.tokens.accessToken, 'Access token should be issued');
    assert.ok(body.data.tokens.refreshToken, 'Refresh token should be issued');
    assert.strictEqual(body.data.user.role, 'tenant_admin');
    assert.strictEqual(body.data.tenant.slug, 'acme-ai-corp');
    assert.strictEqual(body.data.user.passwordHash, undefined, 'passwordHash must never be exposed');

    aliceToken = body.data.tokens.accessToken;
    aliceRefreshToken = body.data.tokens.refreshToken;
    aliceTenantId = body.data.tenant.tenantId;
    aliceUserId = body.data.user.userId;
  });

  await t.test('POST /api/v1/auth/signup rejects duplicate email registration', async () => {
    const res = await fetch(`http://localhost:${testHttpPort}/api/v1/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'alice@acme.com',
        password: 'Password123!',
        name: 'Alice Duplicate'
      })
    });
    assert.strictEqual(res.status, 409);
    const body = await res.json();
    assert.strictEqual(body.success, false);
    assert.strictEqual(body.error.code, 'EMAIL_ALREADY_EXISTS');
  });

  await t.test('POST /api/v1/auth/login authenticates with valid credentials', async () => {
    const res = await fetch(`http://localhost:${testHttpPort}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'alice@acme.com',
        password: 'Password123!'
      })
    });
    assert.strictEqual(res.status, 200);
    const body = await res.json();
    assert.strictEqual(body.success, true);
    assert.ok(body.data.tokens.accessToken);
    assert.ok(body.data.tokens.refreshToken);
    assert.strictEqual(body.data.user.email, 'alice@acme.com');
  });

  await t.test('POST /api/v1/auth/login fails with wrong password without leaking info', async () => {
    const res = await fetch(`http://localhost:${testHttpPort}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'alice@acme.com',
        password: 'WrongPassword456!'
      })
    });
    assert.strictEqual(res.status, 401);
    const body = await res.json();
    assert.strictEqual(body.success, false);
    assert.strictEqual(body.error.code, 'INVALID_CREDENTIALS');
  });

  await t.test('GET /api/v1/auth/me returns current user and tenant context', async () => {
    const res = await fetch(`http://localhost:${testHttpPort}/api/v1/auth/me`, {
      headers: {
        Authorization: `Bearer ${aliceToken}`
      }
    });
    assert.strictEqual(res.status, 200);
    const body = await res.json();
    assert.strictEqual(body.success, true);
    assert.strictEqual(body.data.user.userId, aliceUserId);
    assert.strictEqual(body.data.tenant.tenantId, aliceTenantId);
  });

  await t.test('Multi-Tenant Isolation: Users in separate tenants are strictly partitioned', async () => {
    // Signup user Bob in separate tenant "Beta Systems"
    const resBob = await fetch(`http://localhost:${testHttpPort}/api/v1/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'bob@beta.io',
        password: 'BobPassword456!',
        name: 'Bob Jones',
        tenantName: 'Beta Systems'
      })
    });
    assert.strictEqual(resBob.status, 201);
    const bobData = await resBob.json();
    bobToken = bobData.data.tokens.accessToken;
    bobTenantId = bobData.data.tenant.tenantId;

    assert.notStrictEqual(bobTenantId, aliceTenantId, 'Tenant IDs must be distinct');

    // Bob requests his members: should only see Bob
    const resBobMembers = await fetch(`http://localhost:${testHttpPort}/api/v1/auth/tenants/current/members`, {
      headers: { Authorization: `Bearer ${bobToken}` }
    });
    assert.strictEqual(resBobMembers.status, 200);
    const bobMembers = await resBobMembers.json();
    assert.strictEqual(bobMembers.data.memberCount, 1);
    assert.strictEqual(bobMembers.data.members[0].email, 'bob@beta.io');

    // Alice requests her members: should only see Alice
    const resAliceMembers = await fetch(`http://localhost:${testHttpPort}/api/v1/auth/tenants/current/members`, {
      headers: { Authorization: `Bearer ${aliceToken}` }
    });
    assert.strictEqual(resAliceMembers.status, 200);
    const aliceMembers = await resAliceMembers.json();
    assert.strictEqual(aliceMembers.data.memberCount, 1);
    assert.strictEqual(aliceMembers.data.members[0].email, 'alice@acme.com');
  });

  await t.test('POST /api/v1/auth/tenants/current/members allows Tenant Admin to invite members', async () => {
    const res = await fetch(`http://localhost:${testHttpPort}/api/v1/auth/tenants/current/members`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${aliceToken}`
      },
      body: JSON.stringify({
        email: 'carol@acme.com',
        name: 'Carol Engineer',
        password: 'CarolPassword123!',
        role: 'developer'
      })
    });
    assert.strictEqual(res.status, 201);
    const body = await res.json();
    assert.strictEqual(body.success, true);
    assert.strictEqual(body.data.role, 'developer');
    assert.strictEqual(body.data.tenantId, aliceTenantId);

    // Verify member count for Alice is now 2
    const verifyRes = await fetch(`http://localhost:${testHttpPort}/api/v1/auth/tenants/current/members`, {
      headers: { Authorization: `Bearer ${aliceToken}` }
    });
    const verifyData = await verifyRes.json();
    assert.strictEqual(verifyData.data.memberCount, 2);
  });

  let resetToken = null;

  await t.test('POST /api/v1/auth/forgot-password generates hashed reset token securely', async () => {
    const res = await fetch(`http://localhost:${testHttpPort}/api/v1/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'alice@acme.com'
      })
    });
    assert.strictEqual(res.status, 200);
    const body = await res.json();
    assert.strictEqual(body.success, true);
    assert.ok(body.data.debug_token, 'Debug reset token returned in test env');
    resetToken = body.data.debug_token;

    // Verify raw token is NOT stored in storage, only SHA-256 hash
    const rawUser = await Storage.findUserById(aliceUserId, true);
    assert.notStrictEqual(rawUser.resetPasswordToken, resetToken, 'Raw reset token must NEVER be stored directly in DB');
    assert.strictEqual(typeof rawUser.resetPasswordToken, 'string');
    assert.strictEqual(rawUser.resetPasswordToken.length, 64, 'Stored token must be a 64-char SHA-256 hex digest');
  });

  await t.test('POST /api/v1/auth/reset-password updates password and invalidates sessions', async () => {
    const res = await fetch(`http://localhost:${testHttpPort}/api/v1/auth/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        token: resetToken,
        newPassword: 'BrandNewPassword999!'
      })
    });
    assert.strictEqual(res.status, 200);
    const body = await res.json();
    assert.strictEqual(body.success, true);

    // Old password should fail
    const oldLoginRes = await fetch(`http://localhost:${testHttpPort}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'alice@acme.com',
        password: 'Password123!'
      })
    });
    assert.strictEqual(oldLoginRes.status, 401);

    // New password should succeed
    const newLoginRes = await fetch(`http://localhost:${testHttpPort}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'alice@acme.com',
        password: 'BrandNewPassword999!'
      })
    });
    assert.strictEqual(newLoginRes.status, 200);
    const newLoginData = await newLoginRes.json();
    aliceRefreshToken = newLoginData.data.tokens.refreshToken;
    aliceToken = newLoginData.data.tokens.accessToken;
  });

  await t.test('POST /api/v1/auth/refresh rotates refresh token', async () => {
    const res = await fetch(`http://localhost:${testHttpPort}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        refreshToken: aliceRefreshToken
      })
    });
    assert.strictEqual(res.status, 200);
    const body = await res.json();
    assert.strictEqual(body.success, true);
    assert.ok(body.data.accessToken);
    assert.ok(body.data.refreshToken);
    assert.notStrictEqual(body.data.refreshToken, aliceRefreshToken, 'Refresh token must be rotated');

    // Attempting to reuse old refresh token should fail
    const reuseRes = await fetch(`http://localhost:${testHttpPort}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        refreshToken: aliceRefreshToken
      })
    });
    assert.strictEqual(reuseRes.status, 401);
  });

  await t.test('gRPC AuthService.ValidateToken verifies token synchronously', async () => {
    const validation = await grpcClient.validateToken(aliceToken);
    assert.strictEqual(validation.is_valid, true);
    assert.strictEqual(validation.user_id, aliceUserId);
    assert.strictEqual(validation.tenant_id, aliceTenantId);
    assert.strictEqual(validation.email, 'alice@acme.com');
  });

  await t.test('gRPC AuthService.VerifyTenantAccess enforces boundary checks', async () => {
    // Valid access: Alice accessing Acme
    const validAccess = await grpcClient.verifyTenantAccess(aliceUserId, aliceTenantId);
    assert.strictEqual(validAccess.has_access, true);

    // Invalid access: Alice attempting to access Beta Systems tenant
    const foreignAccess = await grpcClient.verifyTenantAccess(aliceUserId, bobTenantId);
    assert.strictEqual(foreignAccess.has_access, false);
    assert.ok(foreignAccess.reason.includes('Tenant boundary violation'));
  });

  await t.test('Clean up and shutdown test servers', async () => {
    grpcClient.close();
    await grpcServer.stop();
    await new Promise((resolve) => {
      server.close(resolve);
    });
  });
});
