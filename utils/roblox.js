const axios = require('axios');

class RobloxAPI {
  constructor(cookie) {
    this.cookie = cookie;
    this.csrfToken = null;
  }

  async getCsrfToken() {
    try {
      const response = await axios.post('https://auth.roblox.com/v2/logout', {}, {
        headers: {
          'Cookie': `.ROBLOSECURITY=${this.cookie}`,
        },
        validateStatus: () => true,
      });

      if (response.headers['x-csrf-token']) {
        this.csrfToken = response.headers['x-csrf-token'];
        return this.csrfToken;
      }
    } catch (error) {
      console.error('Error getting CSRF token:', error.message);
    }
    return null;
  }

  async getCurrentUser() {
    try {
      const response = await axios.get('https://users.roblox.com/v1/users/authenticated', {
        headers: {
          'Cookie': `.ROBLOSECURITY=${this.cookie}`,
        },
      });
      return response.data;
    } catch (error) {
      return null;
    }
  }

  async getRobuxBalance(userId) {
    try {
      const response = await axios.get(`https://economy.roblox.com/v1/users/${userId}/currency`, {
        headers: {
          'Cookie': `.ROBLOSECURITY=${this.cookie}`,
        },
      });
      return response.data.robux || 0;
    } catch (error) {
      return 0;
    }
  }

  async getPremiumStatus(userId) {
    try {
      const response = await axios.get(`https://premiumfeatures.roblox.com/v1/users/${userId}/validate-membership`, {
        headers: {
          'Cookie': `.ROBLOSECURITY=${this.cookie}`,
        },
      });
      return response.data.isPremium || false;
    } catch (error) {
      return false;
    }
  }

  async getFriendCount(userId) {
    try {
      const response = await axios.get(`https://friends.roblox.com/v1/users/${userId}/friends/count`, {
        headers: {
          'Cookie': `.ROBLOSECURITY=${this.cookie}`,
        },
      });
      return response.data.count || 0;
    } catch (error) {
      return 0;
    }
  }

  async getGroupCount(userId) {
    try {
      const response = await axios.get(`https://groups.roblox.com/v1/users/${userId}/groups/roles`, {
        headers: {
          'Cookie': `.ROBLOSECURITY=${this.cookie}`,
        },
      });
      return response.data.data ? response.data.data.length : 0;
    } catch (error) {
      return 0;
    }
  }

  async getSecuritySettings() {
    try {
      const response = await axios.get('https://twostepverification.roblox.com/v1/users/me/configuration', {
        headers: {
          'Cookie': `.ROBLOSECURITY=${this.cookie}`,
        },
      });

      const has2FA = response.data.methods?.some(m => m.enabled) || false;

      const pinResponse = await axios.get('https://auth.roblox.com/v1/account/pin', {
        headers: {
          'Cookie': `.ROBLOSECURITY=${this.cookie}`,
        },
      });
      const hasPin = pinResponse.data.isEnabled || false;

      return { has2FA, hasPin };
    } catch (error) {
      return { has2FA: false, hasPin: false };
    }
  }

  async checkCookie() {
    try {
      const user = await this.getCurrentUser();
      if (!user || !user.id) {
        return { valid: false };
      }

      const [robux, isPremium, friendCount, groupCount, security] = await Promise.all([
        this.getRobuxBalance(user.id),
        this.getPremiumStatus(user.id),
        this.getFriendCount(user.id),
        this.getGroupCount(user.id),
        this.getSecuritySettings(),
      ]);

      return {
        valid: true,
        robloxUserId: user.id,
        username: user.name,
        displayName: user.displayName,
        robuxBalance: robux,
        isPremium,
        friendCount,
        groupCount,
        has2FA: security.has2FA,
        hasPin: security.hasPin,
      };
    } catch (error) {
      return { valid: false };
    }
  }

  async refreshCookie() {
    try {
      await this.getCsrfToken();

      const response = await axios.post('https://auth.roblox.com/v1/authentication-ticket', {}, {
        headers: {
          'Cookie': `.ROBLOSECURITY=${this.cookie}`,
          'X-CSRF-TOKEN': this.csrfToken,
          'Referer': 'https://www.roblox.com/',
        },
      });

      if (response.headers['set-cookie']) {
        const cookies = response.headers['set-cookie'];
        for (const cookie of cookies) {
          if (cookie.startsWith('.ROBLOSECURITY=')) {
            const newCookie = cookie.split(';')[0].replace('.ROBLOSECURITY=', '');
            return { success: true, cookie: newCookie };
          }
        }
      }

      return { success: false };
    } catch (error) {
      return { success: false };
    }
  }

  async getTransactions(userId, placeId = null, limit = 50) {
    try {
      let url = `https://economy.roblox.com/v2/users/${userId}/transactions?limit=${limit}&transactionType=Purchase,Sale,AffiliateSale,DevEx,GroupPayout,AdSpend`;

      const response = await axios.get(url, {
        headers: {
          'Cookie': `.ROBLOSECURITY=${this.cookie}`,
        },
      });

      let transactions = response.data.data || [];

      if (placeId) {
        transactions = transactions.filter(t => t.details?.placeId === placeId);
      }

      return transactions;
    } catch (error) {
      return [];
    }
  }

  async getBadges(placeId) {
    try {
      const response = await axios.get(`https://badges.roblox.com/v1/universes/${placeId}/badges?limit=100&sortOrder=Asc`);
      return response.data.data || [];
    } catch (error) {
      return [];
    }
  }

  async getGamePasses(placeId) {
    try {
      const response = await axios.get(`https://games.roblox.com/v1/games/${placeId}/game-passes?limit=100&sortOrder=Asc`);
      return response.data.data || [];
    } catch (error) {
      return [];
    }
  }
}

module.exports = RobloxAPI;
