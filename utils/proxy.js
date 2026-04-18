const axios = require('axios');
const { SocksProxyAgent } = require('socks-proxy-agent');
const { HttpsProxyAgent } = require('https-proxy-agent');

class ProxyChecker {
  constructor(proxyString, protocol = 'HTTP') {
    this.proxyString = proxyString;
    this.protocol = protocol.toUpperCase();
    this.parseProxy();
  }

  parseProxy() {
    const parts = this.proxyString.split(':');

    if (parts.length === 2) {
      this.host = parts[0];
      this.port = parts[1];
      this.username = null;
      this.password = null;
    } else if (parts.length === 4) {
      this.host = parts[0];
      this.port = parts[1];
      this.username = parts[2];
      this.password = parts[3];
    } else {
      throw new Error('Invalid proxy format. Use host:port or host:port:username:password');
    }
  }

  getProxyUrl() {
    let auth = '';
    if (this.username && this.password) {
      auth = `${this.username}:${this.password}@`;
    }

    switch (this.protocol) {
      case 'HTTP':
        return `http://${auth}${this.host}:${this.port}`;
      case 'HTTPS':
        return `https://${auth}${this.host}:${this.port}`;
      case 'SOCKS4':
        return `socks4://${auth}${this.host}:${this.port}`;
      case 'SOCKS5':
        return `socks5://${auth}${this.host}:${this.port}`;
      default:
        return `http://${auth}${this.host}:${this.port}`;
    }
  }

  getAgent() {
    const proxyUrl = this.getProxyUrl();

    if (this.protocol === 'SOCKS4' || this.protocol === 'SOCKS5') {
      return new SocksProxyAgent(proxyUrl);
    } else {
      return new HttpsProxyAgent(proxyUrl);
    }
  }

  async check() {
    const startTime = Date.now();

    try {
      const agent = this.getAgent();

      const response = await axios.get('https://api.ipify.org?format=json', {
        httpAgent: agent,
        httpsAgent: agent,
        timeout: 10000,
        validateStatus: () => true,
      });

      const responseTime = Date.now() - startTime;

      if (response.status === 200 && response.data.ip) {
        return {
          working: true,
          responseTime,
          ip: response.data.ip,
        };
      }

      return {
        working: false,
        responseTime,
        error: 'Invalid response',
      };
    } catch (error) {
      const responseTime = Date.now() - startTime;
      return {
        working: false,
        responseTime,
        error: error.message,
      };
    }
  }
}

async function checkProxies(proxies, protocol = 'HTTP') {
  const results = [];

  for (const proxy of proxies) {
    try {
      const checker = new ProxyChecker(proxy, protocol);
      const result = await checker.check();
      results.push({
        proxy,
        ...result,
      });
    } catch (error) {
      results.push({
        proxy,
        working: false,
        error: error.message,
      });
    }
  }

  return results;
}

module.exports = { ProxyChecker, checkProxies };
