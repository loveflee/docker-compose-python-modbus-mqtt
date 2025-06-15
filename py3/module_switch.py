# switch_control.py

import time
from pymodbus.client import ModbusTcpClient
import paho.mqtt.client as mqtt

# Modbus 參數
MODBUS_HOST = '192.168.88.190'
MODBUS_PORT = 502
MODBUS_SLAVE_ID = 3
COIL_START_ADDRESS = 0
COIL_COUNT = 8

# MQTT 參數
MQTT_BROKER = '192.168.88.106'
MQTT_PORT = 1883
MQTT_USERNAME = 'mqtt'
MQTT_PASSWORD = 'mqtt'

# 初始化
modbus_client = ModbusTcpClient(MODBUS_HOST, port=MODBUS_PORT)
mqtt_client = mqtt.Client(protocol=mqtt.MQTTv311)  # 修正 deprecated warning
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

def update_coil(index, state):
    """寫入 Modbus Coil 並發布 MQTT 狀態"""
    try:
        if not modbus_client.is_socket_open():
            modbus_client.connect()
        modbus_client.write_coil(COIL_START_ADDRESS + index, state, slave=MODBUS_SLAVE_ID)
        payload = "ON" if state else "OFF"
        mqtt_client.publish(f"modbus/coils/status/{index}", payload=payload, retain=True)
        print(f"✅ Coil {index} 設定為 {payload}")
    except Exception as e:
        print(f"❌ 寫入 Coil {index} 發生錯誤: {e}")

def on_connect(client, userdata, flags, rc, properties=None):
    print("✅ Switch Control 已連線 MQTT")
    client.subscribe("modbus/coils/command/+")
    print("✅ 已訂閱 modbus/coils/command/+")

def on_message(client, userdata, msg):
    try:
        coil_index = int(msg.topic.split('/')[-1])
        state = msg.payload.decode().upper() == "ON"
        update_coil(coil_index, state)
    except Exception as e:
        print(f"⚠️ 處理訊息錯誤: {e}")

def run():
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()

    if not modbus_client.connect():
        print("⚠️ 無法連接到 Modbus 伺服器")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Switch Control 結束")
    finally:
        modbus_client.close()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == "__main__":
    run()
