"""
📌 Temp/Humidity Module
This module reads Modbus temperature and humidity values and publishes them to MQTT.
It also registers them in Home Assistant using MQTT Discovery.
模組功能：
- 從 Modbus 讀取溫濕度資料
- 發佈至 MQTT 主題
- 自動註冊至 Home Assistant
"""

import time
import json
import modbus_mqtt_client

# ========================
# 🟡 常數定義（設定參數）
# ========================

REGISTER_HUMIDITY = 0x0000         # 濕度的 Modbus 寄存器地址
REGISTER_TEMPERATURE = 0x0001      # 溫度的 Modbus 寄存器地址
POLL_INTERVAL = 20                 # 資料輪詢間隔（秒）

COMPONENT = "sensor"               # Home Assistant 元件類型（固定為 sensor）
NODE_ID = "hy01"                   # 節點 ID，用來識別不同裝置（需唯一）

# ========================
# 🟠 發佈 Home Assistant Discovery 設定
# ========================

def publish_discovery_config(mqtt_client, slave_id):
    """
    Publish MQTT Discovery config for temperature and humidity sensors.
    發佈 Home Assistant Discovery 設定，讓 HA 自動註冊溫濕度感測器
    """
    device_name = f"{NODE_ID}_slave{slave_id}"  # 裝置名稱，如 hy01_slave3

    sensors = [
        {
            "object_id": f"{NODE_ID}_slave{slave_id}_temperature",  # 實體 ID：sensor.hy01_slave3_temperature
            "name": f"{NODE_ID} Slave {slave_id} Temperature",      # 顯示名稱
            "state_topic": f"{NODE_ID}/{slave_id}/temperature/state",  # MQTT 狀態主題
            "unit": "°C",
            "device_class": "temperature",
            "unique_id": f"{NODE_ID}_slave{slave_id}_temperature"
        },
        {
            "object_id": f"{NODE_ID}_slave{slave_id}_humidity",     # 實體 ID：sensor.hy01_slave3_humidity
            "name": f"{NODE_ID} Slave {slave_id} Humidity",
            "state_topic": f"{NODE_ID}/{slave_id}/humidity/state",
            "unit": "%",
            "device_class": "humidity",
            "unique_id": f"{NODE_ID}_slave{slave_id}_humidity"
        }
    ]

    for sensor in sensors:
        topic = f"homeassistant/{COMPONENT}/{NODE_ID}/{sensor['object_id']}/config"
        payload = {
            "name": sensor["name"],
            "state_topic": sensor["state_topic"],
            "unit_of_measurement": sensor["unit"],
            "device_class": sensor["device_class"],
            "unique_id": sensor["unique_id"],
            "object_id": sensor["object_id"],
            "device": {
                "identifiers": [device_name],
                "name": device_name,
                "model": "Modbus Temp/Humidity Sensor",
                "manufacturer": "YourCompany"
            }
        }

        mqtt_client.publish(topic, json.dumps(payload), retain=True)
        print(f"📢 Published HA config: {topic}")


# ========================
# 🟣 讀取溫溼度數據並發佈
# ========================

def read_temp_humidity(modbus_manager, slave_id, mqtt_client):
    """
    Read humidity and temperature from Modbus and publish to MQTT.
    從 Modbus 讀取濕度與溫度資料，發佈至 MQTT
    """
    try:
        modbus_client = modbus_manager.get_client()
        result = modbus_client.read_holding_registers(
            address=REGISTER_HUMIDITY,
            count=2,  # 一次讀兩個值：濕度 + 溫度
            slave=slave_id
        )

        if result.isError():
            print(f"⚠️ Modbus read error (slave {slave_id})")
            return

        humidity_raw = result.registers[0]
        temperature_raw = result.registers[1]

        humidity = humidity_raw / 10.0         # 例如 635 => 63.5%
        temperature = temperature_raw / 10.0   # 例如 298 => 29.8°C

        mqtt_client.publish(f"{NODE_ID}/{slave_id}/humidity/state", payload=humidity, retain=True)
        mqtt_client.publish(f"{NODE_ID}/{slave_id}/temperature/state", payload=temperature, retain=True)

        print(f"✅ slave {slave_id} => Temperature: {temperature}°C, Humidity: {humidity}%")

    except Exception as e:
        print(f"❌ Failed to read temp/humidity (slave {slave_id}): {e}")


# ========================
# 🟤 MQTT 連線事件處理
# ========================

def on_connect(client, userdata, flags, rc, properties=None):
    """
    Called when MQTT is connected.
    MQTT 連線成功時，註冊 HA Discovery 設定
    """
    slave_id = userdata["slave_id"]
    print(f"✅ Connected to MQTT (slave {slave_id})")
    publish_discovery_config(client, slave_id)


# ========================
# 🔵 主程式進入點
# ========================

def run(slave_id, modbus_manager):
    """
    Start MQTT client and begin polling temperature/humidity data.
    啟動 MQTT 客戶端，並定期讀取溫濕度資料
    """
    mqtt_client = modbus_mqtt_client.get_mqtt_client()
    mqtt_client.user_data_set({"slave_id": slave_id})
    mqtt_client.on_connect = on_connect

    mqtt_client.connect(modbus_mqtt_client.MQTT_BROKER, modbus_mqtt_client.MQTT_PORT, 60)
    mqtt_client.loop_start()

    try:
        while True:
            read_temp_humidity(modbus_manager, slave_id, mqtt_client)
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print(f"🛑 Stopping Temp/Humidity module (slave {slave_id})")
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
