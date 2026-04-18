const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
);

class Database {
  async getOrCreateUser(telegramId, username = '') {
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .eq('telegram_id', telegramId)
      .maybeSingle();

    if (data) {
      return data;
    }

    const { data: newUser, error: insertError } = await supabase
      .from('users')
      .insert([{ telegram_id: telegramId, username }])
      .select()
      .single();

    return newUser;
  }

  async addCookie(userId, cookieData) {
    const { data, error } = await supabase
      .from('roblox_cookies')
      .insert([{
        user_id: userId,
        cookie: cookieData.cookie,
        roblox_user_id: cookieData.robloxUserId,
        username: cookieData.username,
        display_name: cookieData.displayName,
        robux_balance: cookieData.robuxBalance,
        is_premium: cookieData.isPremium,
        has_2fa: cookieData.has2FA,
        has_pin: cookieData.hasPin,
        friend_count: cookieData.friendCount,
        group_count: cookieData.groupCount,
        last_checked: new Date().toISOString(),
        is_valid: cookieData.valid,
      }])
      .select()
      .single();

    return data;
  }

  async getCookies(userId) {
    const { data, error } = await supabase
      .from('roblox_cookies')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    return data || [];
  }

  async updateCookie(cookieId, updates) {
    const { data, error } = await supabase
      .from('roblox_cookies')
      .update({
        ...updates,
        updated_at: new Date().toISOString(),
      })
      .eq('id', cookieId)
      .select()
      .single();

    return data;
  }

  async deleteCookie(cookieId, userId) {
    const { data, error } = await supabase
      .from('roblox_cookies')
      .delete()
      .eq('id', cookieId)
      .eq('user_id', userId);

    return !error;
  }

  async addProxy(userId, proxyData) {
    const { data, error } = await supabase
      .from('proxies')
      .insert([{
        user_id: userId,
        proxy_address: proxyData.proxy,
        protocol: proxyData.protocol,
        username: proxyData.username || '',
        password: proxyData.password || '',
        is_working: proxyData.working,
        response_time: proxyData.responseTime,
        last_checked: new Date().toISOString(),
      }])
      .select()
      .single();

    return data;
  }

  async getProxies(userId) {
    const { data, error } = await supabase
      .from('proxies')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    return data || [];
  }

  async updateProxy(proxyId, updates) {
    const { data, error } = await supabase
      .from('proxies')
      .update({
        ...updates,
        updated_at: new Date().toISOString(),
      })
      .eq('id', proxyId)
      .select()
      .single();

    return data;
  }

  async deleteProxy(proxyId, userId) {
    const { data, error } = await supabase
      .from('proxies')
      .delete()
      .eq('id', proxyId)
      .eq('user_id', userId);

    return !error;
  }

  async addTransactionLog(userId, cookieId, transactionData) {
    const { data, error } = await supabase
      .from('transaction_logs')
      .insert([{
        user_id: userId,
        roblox_cookie_id: cookieId,
        place_id: transactionData.placeId,
        transaction_type: transactionData.type,
        amount: transactionData.amount,
        description: transactionData.description,
        timestamp: transactionData.timestamp,
      }])
      .select()
      .single();

    return data;
  }

  async getTransactionLogs(userId, cookieId = null) {
    let query = supabase
      .from('transaction_logs')
      .select('*')
      .eq('user_id', userId);

    if (cookieId) {
      query = query.eq('roblox_cookie_id', cookieId);
    }

    const { data, error } = await query.order('timestamp', { ascending: false });

    return data || [];
  }
}

module.exports = new Database();
