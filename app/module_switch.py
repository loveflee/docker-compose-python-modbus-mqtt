"""
📌 Switch Module
控制 Modbus Coil，透過 Home Assistant MQTT Discovery 自動註冊並與 HA 同步狀態
"""

import time
import json
import modbus_mqtt_client

# ========================
# 🟡 常數定義
# ========================
COIL_START_ADDRESS = 0          # Modbus Coil 起始位址
COIL_COUNT = 8                  # Coil 數量（通常為 8 或自定義）

COMPONENT = "switch"            # HA 元件類型（switch）
NODE_ID = "hy01"                # 裝置節點 ID（HA 用來識別設備，例如 hy01）

# ========================
# 🟠 發佈 Home Assistant Discovery 設定
# ========================
def publish_discovery_config(mqtt_client, slave_id):
    """
    發佈每個 coil 的 HA Discovery 設定，包含 slave_id 於 topic/object_id
    Publish Home Assistant Discovery config for each coil
    """
    for index in range(COIL_COUNT):
        object_id = f"{NODE_ID}_slave{slave_id}_coil{index}"  # 實體 ID
        topic = f"homeassistant/{COMPONENT}/{object_id}/config"  # Discovery 設定主題

        config_payload = {
            "name": f"{object_id}",  # 顯示名稱（可讀）
            "command_topic": f"{NODE_ID}/coil/{slave_id}/{index}/set",  # HA 發送控制訊息的主題
            "state_topic": f"{NODE_ID}/coil/{slave_id}/{index}/state",  # HA 讀取狀態的主題
            "payload_on": "ON",         # 開的 payload
            "payload_off": "OFF",       # 關的 payload
            "unique_id": object_id,     # HA 唯一 ID
            "object_id": object_id,     # HA Entity ID 中的 object_id 部分
            "device": {
                "identifiers": [f"{NODE_ID}_slave{slave_id}"],      # HA 裝置識別碼
                "name": f"{NODE_ID}_slave{slave_id}",               # 顯示裝置名稱
                "model": "Modbus Coil Controller",                  # 型號
                "manufacturer": "YourCompany"                       # 製造商
            }
        }

        mqtt_client.publish(topic, json.dumps(config_payload), retain=True)
        print(f"📢 發佈 HA 設定：{topic}")

# ========================
# 🟣 更新 Coil 狀態與狀態上報
# ========================
def update_coil(modbus_manager, slave_id, mqtt_client, index, state):
    """
    寫入 Coil 並向 HA 回報狀態
    Write value to Modbus coil and report to HA
    """
    try:
        modbus_client = modbus_manager.get_client()
        modbus_client.write_coil(COIL_START_ADDRESS + index, state, slave=slave_id)

        payload = "ON" if state else "OFF"
        mqtt_client.publish(f"{NODE_ID}/coil/{slave_id}/{index}/state", payload=payload, retain=True)
        print(f"✅ Coil {index} 設定為 {payload}")
    except Exception as e:
        print(f"❌ 寫入 Coil {index} 發生錯誤: {e}")

# ========================
# 🟢 MQTT 連線事件
# ========================
def on_connect(client, userdata, flags, rc, properties=None):
    """
    當 MQTT 連線成功時，訂閱所有 coil 的控制主題，並發佈 Discovery 設定
    On MQTT connect, subscribe to all control topics and publish discovery config
    """
    slave_id = userdata["slave_id"]
    print(f"✅ MQTT 已連線（slave {slave_id}）")

    for index in range(COIL_COUNT):
        topic = f"{NODE_ID}/coil/{slave_id}/{index}/set"
        client.subscribe(topic)
        print(f"✅ 訂閱控制主題：{topic}")

    publish_discovery_config(client, slave_id)

# ========================
# 🔵 MQTT 控制訊息處理
# ========================
def on_message(client, userdata, msg):
    """
    處理從 HA 收到的開關控制訊息
    Handle incoming ON/OFF control message from HA
    """
    try:
        parts = msg.topic.split('/')  # topic: hy01/coil/3/0/set
        slave_id = int(parts[2])      # 取得 slave_id = 3
        coil_index = int(parts[3])    # 取得 index = 0
        state = msg.payload.decode().upper() == "ON"  # 判斷 ON / OFF

        update_coil(userdata["modbus_manager"], slave_id, client, coil_index, state)
    except Exception as e:
        print(f"⚠️ 處理控制命令錯誤: {e}")

# ========================
# 🟤 主程式進入點
# ========================
def run(slave_id, modbus_manager):
    """
    啟動模組主程式，連線至 MQTT 並保持執行
    Start main loop, connect to MQTT and stay running
    """
    mqtt_client = modbus_mqtt_client.get_mqtt_client()
    mqtt_client.user_data_set({
        "slave_id": slave_id,
        "modbus_manager": modbus_manager
    })

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(
        modbus_mqtt_client.MQTT_BROKER,
        modbus_mqtt_client.MQTT_PORT,
        60
    )
    mqtt_client.loop_start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Switch Module 結束")
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()