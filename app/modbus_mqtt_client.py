# modbus_mqtt_client.py

"""
📌 Modbus 與 MQTT 連線管理模組
統一管理連線資訊、建立連線物件、避免重複連線
同時提供自動重連的功能
"""

from pymodbus.client import ModbusTcpClient
import paho.mqtt.client as mqtt
import threading
import time

# ==============================
# 🟡 Modbus 參數（統一管理）
# ==============================
MODBUS_HOST = 'modbus gateway ip'
MODBUS_PORT = 502

# ==============================
# 🟠 MQTT 參數（統一管理）
# ==============================
MQTT_BROKER = 'ha ip'
MQTT_PORT = 1883
MQTT_USERNAME = 'your' 
MQTT_PASSWORD = 'your' 

# ==============================
# 🔵 Modbus 連線管理類別（單例）
# ==============================
class ModbusManager:
    """
    用來管理單一個 Modbus TCP 連線（保持連線 & 自動重連）
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.lock = threading.Lock()
        self.client = ModbusTcpClient(host=self.host, port=self.port)
        self._connect()

    def _connect(self):
        """
        嘗試連接 Modbus 伺服器
        """
        if not self.client.is_socket_open():
            if self.client.connect():
                print(f"✅ Modbus 已連線: {self.host}:{self.port}")
            else:
                print(f"⚠️ Modbus 連線失敗: {self.host}:{self.port}")

    def get_client(self):
        """
        提供 Modbus client 實例（保持連線）
        """
        with self.lock:
            if not self.client.is_socket_open():
                print("⚠️ Modbus 連線中斷，自動重新連線...")
                self.client.close()
                self.client.connect()
            return self.client

    def close(self):
        """
        結束連線
        """
        with self.lock:
            self.client.close()

# ==============================
# 🟣 MQTT 客戶端（共用）
# ==============================
def get_mqtt_client():
    """
    建立 MQTT 客戶端（共用設定）
    """
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    return client

# ==============================
# 🟤 單例管理器（外部使用）
# ==============================
modbus_manager = ModbusManager(MODBUS_HOST, MODBUS_PORT)
