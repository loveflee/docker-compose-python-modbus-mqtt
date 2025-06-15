# module_temp.py

import time
from pymodbus.client import ModbusTcpClient
import paho.mqtt.client as mqtt

MODBUS_HOST = '192.168.88.190'
MODBUS_PORT = 502
MODBUS_SLAVE_ID = 1

MQTT_BROKER = '192.168.88.106'
MQTT_PORT = 1883
MQTT_USERNAME = 'mqtt'
MQTT_PASSWORD = 'mqtt'

modbus_client = ModbusTcpClient(MODBUS_HOST, port=MODBUS_PORT)
mqtt_client = mqtt.Client(protocol=mqtt.MQTTv311)
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

def read_temp_humidity():
    try:
        if not modbus_client.is_socket_open():
            modbus_client.connect()
        result = modbus_client.read_holding_registers(0, 2, slave=MODBUS_SLAVE_ID)
        if result.isError():
            print("❌ Temp Module: 讀取失敗")
            return None, None
        temp = result.registers[0] / 10.0
        humidity = result.registers[1] / 10.0
        return temp, humidity
    except Exception as e:
        print(f"❌ Temp Module: 發生錯誤: {e}")
        return None, None

def publish_temp_humidity(temp, humidity):
    mqtt_client.publish("modbus/sensors/temperature", payload=temp, retain=True)
    mqtt_client.publish("modbus/sensors/humidity", payload=humidity, retain=True)
    print(f"✅ Temp Module: 發佈 Temp: {temp}°C, Humidity: {humidity}%")

def run(update_interval=20):
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()

    if not modbus_client.connect():
        print("⚠️ Temp Module: 無法連接 Modbus")

    try:
        while True:
            temp, humidity = read_temp_humidity()
            if temp is not None and humidity is not None:
                publish_temp_humidity(temp, humidity)
            time.sleep(update_interval)
    except KeyboardInterrupt:
        print("🛑 Temp Module 結束")
    finally:
        modbus_client.close()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
