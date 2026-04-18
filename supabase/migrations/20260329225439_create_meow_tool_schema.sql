/*
  # MeowTool Telegram Bot Database Schema

  1. New Tables
    - users: Stores Telegram user information
    - roblox_cookies: Stores Roblox account cookies and associated data
    - proxies: Stores proxy configurations and status
    - transaction_logs: Stores Roblox transaction history

  2. Security
    - Enable RLS on all tables
    - Users can only access their own data

  3. Indexes
    - Optimized lookups for telegram_id and user_id
*/

-- Create users table
CREATE TABLE IF NOT EXISTS users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  telegram_id bigint UNIQUE NOT NULL,
  username text DEFAULT '',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create roblox_cookies table
CREATE TABLE IF NOT EXISTS roblox_cookies (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  cookie text NOT NULL,
  roblox_user_id bigint,
  username text DEFAULT '',
  display_name text DEFAULT '',
  robux_balance integer DEFAULT 0,
  is_premium boolean DEFAULT false,
  has_2fa boolean DEFAULT false,
  has_pin boolean DEFAULT false,
  friend_count integer DEFAULT 0,
  group_count integer DEFAULT 0,
  last_checked timestamptz,
  is_valid boolean DEFAULT true,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create proxies table
CREATE TABLE IF NOT EXISTS proxies (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  proxy_address text NOT NULL,
  protocol text DEFAULT 'HTTP',
  username text DEFAULT '',
  password text DEFAULT '',
  is_working boolean DEFAULT false,
  response_time integer DEFAULT 0,
  last_checked timestamptz,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create transaction_logs table
CREATE TABLE IF NOT EXISTS transaction_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  roblox_cookie_id uuid REFERENCES roblox_cookies(id) ON DELETE CASCADE,
  place_id bigint,
  transaction_type text DEFAULT '',
  amount integer DEFAULT 0,
  description text DEFAULT '',
  timestamp timestamptz,
  created_at timestamptz DEFAULT now()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS users_telegram_id_idx ON users(telegram_id);
CREATE INDEX IF NOT EXISTS roblox_cookies_user_id_idx ON roblox_cookies(user_id);
CREATE INDEX IF NOT EXISTS roblox_cookies_roblox_user_id_idx ON roblox_cookies(roblox_user_id);
CREATE INDEX IF NOT EXISTS proxies_user_id_idx ON proxies(user_id);
CREATE INDEX IF NOT EXISTS transaction_logs_user_id_idx ON transaction_logs(user_id);
CREATE INDEX IF NOT EXISTS transaction_logs_cookie_id_idx ON transaction_logs(roblox_cookie_id);

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE roblox_cookies ENABLE ROW LEVEL SECURITY;
ALTER TABLE proxies ENABLE ROW LEVEL SECURITY;
ALTER TABLE transaction_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
CREATE POLICY "Users can view own profile"
  ON users FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON users FOR UPDATE
  TO authenticated
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
  ON users FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = id);

-- RLS Policies for roblox_cookies table
CREATE POLICY "Users can view own cookies"
  ON roblox_cookies FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

CREATE POLICY "Users can insert own cookies"
  ON roblox_cookies FOR INSERT
  TO authenticated
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own cookies"
  ON roblox_cookies FOR UPDATE
  TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can delete own cookies"
  ON roblox_cookies FOR DELETE
  TO authenticated
  USING (user_id = auth.uid());

-- RLS Policies for proxies table
CREATE POLICY "Users can view own proxies"
  ON proxies FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

CREATE POLICY "Users can insert own proxies"
  ON proxies FOR INSERT
  TO authenticated
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own proxies"
  ON proxies FOR UPDATE
  TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can delete own proxies"
  ON proxies FOR DELETE
  TO authenticated
  USING (user_id = auth.uid());

-- RLS Policies for transaction_logs table
CREATE POLICY "Users can view own transaction logs"
  ON transaction_logs FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

CREATE POLICY "Users can insert own transaction logs"
  ON transaction_logs FOR INSERT
  TO authenticated
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can delete own transaction logs"
  ON transaction_logs FOR DELETE
  TO authenticated
  USING (user_id = auth.uid());