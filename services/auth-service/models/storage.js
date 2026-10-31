/**
 * Unified Storage Layer for Auth Service
 * Supports MongoDB when online, seamlessly falls back to thread-safe memory store
 */
const { getDbStatus } = require('../config/db');
const Tenant = require('./Tenant');
const User = require('./User');
const logger = require('../config/logger');

// Fallback in-memory stores
const memoryTenants = new Map();
const memoryUsers = new Map();

class Storage {
  static sanitizeUser(user) {
    if (!user) return null;
    const obj = typeof user.toObject === 'function' ? user.toObject() : { ...user };
    delete obj.passwordHash;
    delete obj.resetPasswordToken;
    delete obj.resetPasswordExpires;
    delete obj.refreshTokens;
    delete obj.__v;
    return obj;
  }

  // --- TENANT OPERATIONS ---

  static async findTenantById(tenantId) {
    if (getDbStatus()) {
      try {
        return await Tenant.findOne({ tenantId });
      } catch (err) {
        logger.warn(`MongoDB findTenantById error, falling back to memory: ${err.message}`);
      }
    }
    return memoryTenants.get(tenantId) || null;
  }

  static async findTenantBySlug(slug) {
    const normalizedSlug = slug.toLowerCase().trim();
    if (getDbStatus()) {
      try {
        return await Tenant.findOne({ slug: normalizedSlug });
      } catch (err) {
        logger.warn(`MongoDB findTenantBySlug error, falling back to memory: ${err.message}`);
      }
    }
    for (const tenant of memoryTenants.values()) {
      if (tenant.slug === normalizedSlug) return tenant;
    }
    return null;
  }

  static async createTenant(data) {
    const record = {
      tenantId: data.tenantId,
      name: data.name,
      slug: data.slug.toLowerCase().trim(),
      plan: data.plan || 'starter',
      status: data.status || 'ACTIVE',
      settings: data.settings || { maxUsers: 50, allowedDomains: [], requireMFA: false },
      createdAt: new Date(),
      updatedAt: new Date()
    };

    if (getDbStatus()) {
      try {
        const created = await Tenant.create(record);
        memoryTenants.set(record.tenantId, record);
        return created;
      } catch (err) {
        logger.warn(`MongoDB createTenant error, falling back to memory: ${err.message}`);
      }
    }

    memoryTenants.set(record.tenantId, record);
    return record;
  }

  // --- USER OPERATIONS ---

  static async findUserById(userId, includeSensitive = false) {
    if (getDbStatus()) {
      try {
        const user = await User.findOne({ userId });
        if (!user) return null;
        return includeSensitive ? user : this.sanitizeUser(user);
      } catch (err) {
        logger.warn(`MongoDB findUserById error, falling back to memory: ${err.message}`);
      }
    }

    const user = memoryUsers.get(userId);
    if (!user) return null;
    return includeSensitive ? user : this.sanitizeUser(user);
  }

  static async findUserByEmail(email, tenantId = null, includeSensitive = false) {
    const normalizedEmail = email.toLowerCase().trim();
    if (getDbStatus()) {
      try {
        const query = { email: normalizedEmail };
        if (tenantId) query.tenantId = tenantId;
        const user = await User.findOne(query);
        if (!user) return null;
        return includeSensitive ? user : this.sanitizeUser(user);
      } catch (err) {
        logger.warn(`MongoDB findUserByEmail error, falling back to memory: ${err.message}`);
      }
    }

    for (const user of memoryUsers.values()) {
      if (user.email === normalizedEmail) {
        if (!tenantId || user.tenantId === tenantId) {
          return includeSensitive ? user : this.sanitizeUser(user);
        }
      }
    }
    return null;
  }

  static async findUserByResetToken(tokenHash, includeSensitive = false) {
    if (getDbStatus()) {
      try {
        const user = await User.findOne({
          resetPasswordToken: tokenHash,
          resetPasswordExpires: { $gt: new Date() }
        });
        if (!user) return null;
        return includeSensitive ? user : this.sanitizeUser(user);
      } catch (err) {
        logger.warn(`MongoDB findUserByResetToken error, falling back to memory: ${err.message}`);
      }
    }

    const now = new Date();
    for (const user of memoryUsers.values()) {
      if (
        user.resetPasswordToken === tokenHash &&
        user.resetPasswordExpires &&
        new Date(user.resetPasswordExpires) > now
      ) {
        return includeSensitive ? user : this.sanitizeUser(user);
      }
    }
    return null;
  }

  static async findUserByRefreshToken(tokenHash, includeSensitive = false) {
    if (getDbStatus()) {
      try {
        const user = await User.findOne({
          'refreshTokens.tokenHash': tokenHash,
          'refreshTokens.expiresAt': { $gt: new Date() }
        });
        if (!user) return null;
        return includeSensitive ? user : this.sanitizeUser(user);
      } catch (err) {
        logger.warn(`MongoDB findUserByRefreshToken error, falling back to memory: ${err.message}`);
      }
    }

    const now = new Date();
    for (const user of memoryUsers.values()) {
      if (Array.isArray(user.refreshTokens)) {
        const matched = user.refreshTokens.some(
          (t) => t.tokenHash === tokenHash && new Date(t.expiresAt) > now
        );
        if (matched) {
          return includeSensitive ? user : this.sanitizeUser(user);
        }
      }
    }
    return null;
  }

  static async createUser(data) {
    const record = {
      userId: data.userId,
      tenantId: data.tenantId,
      email: data.email.toLowerCase().trim(),
      passwordHash: data.passwordHash,
      name: data.name,
      role: data.role || 'viewer',
      status: data.status || 'ACTIVE',
      resetPasswordToken: null,
      resetPasswordExpires: null,
      refreshTokens: data.refreshTokens || [],
      createdAt: new Date(),
      updatedAt: new Date()
    };

    if (getDbStatus()) {
      try {
        const created = await User.create(record);
        memoryUsers.set(record.userId, record);
        return created;
      } catch (err) {
        logger.warn(`MongoDB createUser error, falling back to memory: ${err.message}`);
      }
    }

    memoryUsers.set(record.userId, record);
    return record;
  }

  static async updateUser(userId, updates) {
    if (getDbStatus()) {
      try {
        const updated = await User.findOneAndUpdate(
          { userId },
          { $set: { ...updates, updatedAt: new Date() } },
          { new: true }
        );
        if (updated) {
          const inMem = memoryUsers.get(userId) || {};
          memoryUsers.set(userId, { ...inMem, ...updates, updatedAt: new Date() });
          return updated;
        }
      } catch (err) {
        logger.warn(`MongoDB updateUser error, falling back to memory: ${err.message}`);
      }
    }

    const existing = memoryUsers.get(userId);
    if (!existing) return null;
    const merged = { ...existing, ...updates, updatedAt: new Date() };
    memoryUsers.set(userId, merged);
    return merged;
  }

  static async findUsersByTenant(tenantId) {
    if (getDbStatus()) {
      try {
        const users = await User.find({ tenantId });
        return users.map((u) => this.sanitizeUser(u));
      } catch (err) {
        logger.warn(`MongoDB findUsersByTenant error, falling back to memory: ${err.message}`);
      }
    }

    const results = [];
    for (const user of memoryUsers.values()) {
      if (user.tenantId === tenantId) {
        results.push(this.sanitizeUser(user));
      }
    }
    return results;
  }

  static clearMemory() {
    memoryTenants.clear();
    memoryUsers.clear();
  }
}

module.exports = Storage;
