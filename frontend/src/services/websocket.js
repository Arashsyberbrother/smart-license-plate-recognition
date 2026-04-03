const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
const RECONNECT_INTERVAL = 3000;
const MAX_RECONNECT_ATTEMPTS = 5;

class WebSocketService {
  constructor() {
    this.socket = null;
    this.reconnectAttempts = 0;
    this.onMessageCallback = null;
    this.onConnectCallback = null;
    this.onDisconnectCallback = null;
    this.reconnectTimer = null;
    this.isManualDisconnect = false;
  }

  connect(path = '/ws') {
    this.isManualDisconnect = false;
    this._createConnection(path);
  }

  _createConnection(path) {
    try {
      this.socket = new WebSocket(`${WS_URL}${path}`);

      this.socket.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        if (this.onConnectCallback) this.onConnectCallback();
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (this.onMessageCallback) this.onMessageCallback(data);
        } catch {
          if (this.onMessageCallback) this.onMessageCallback(event.data);
        }
      };

      this.socket.onclose = () => {
        console.log('WebSocket disconnected');
        if (this.onDisconnectCallback) this.onDisconnectCallback();
        if (!this.isManualDisconnect) {
          this._scheduleReconnect(path);
        }
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this._scheduleReconnect(path);
    }
  }

  _scheduleReconnect(path) {
    if (this.reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      console.warn('Max WebSocket reconnect attempts reached');
      return;
    }
    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++;
      console.log(`Reconnecting... attempt ${this.reconnectAttempts}`);
      this._createConnection(path);
    }, RECONNECT_INTERVAL);
  }

  disconnect() {
    this.isManualDisconnect = true;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    }
  }

  onMessage(callback) {
    this.onMessageCallback = callback;
  }

  onConnect(callback) {
    this.onConnectCallback = callback;
  }

  onDisconnect(callback) {
    this.onDisconnectCallback = callback;
  }

  isConnected() {
    return this.socket && this.socket.readyState === WebSocket.OPEN;
  }
}

const wsService = new WebSocketService();
export default wsService;
