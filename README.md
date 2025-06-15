
* ChatGPT 協助說明

---

## 🇹🇼 中文版：Modbus TCP ↔ MQTT 整合容器

# docker-compose-python-modbus-mqtt

> 📦 Docker Compose 專案：Python + Modbus TCP + your 整合
> ✨ 本專案 README 由 [ChatGPT](https://openai.com/chatgpt) 自動生成與優化

---

## 📘 專案簡介

本專案透過 `docker-compose` 建立一個輕量級 Python 環境，能從 Modbus TCP 裝置讀取資料，並轉發至 MQTT Broker（例如 Home Assistant）。
適合整合工控設備、自動化場景與智慧家庭。

目前支援模組：

* `module_switch.py`：控制繼電器 / 開關狀態
* `module_temp.py`：讀取溫度

---

## 🚀 快速啟動

### 1️⃣ 安裝 Python 套件（於 Docker 內部執行）

```bash
docker compose run python:3.11-slim
pip install -r requirements.txt
# 或手動安裝：
pip install paho-mqtt==2.1.0 pymodbus==3.5.0
```

### 2️⃣ 啟動服務

```bash
docker compose up -d
```

---

## 📁 專案結構

```
.
├── docker-compose.yaml      # Docker Compose 配置
├── Dockerfile               # 建立 Python 容器映像
├── requirements.txt         # Python 套件需求
└── app/
    ├── main.py              # 主控制器，負責模組啟用/執行
    ├── module_switch.py     # 開關控制模組
    ├── module_temp.py       # 溫度模組
    └── modbus_mqtt_client.py# Modbus 與 MQTT 客戶端管理
```

---

## ⚙️ 模組設定說明（`main.py`）

你可以透過 `main.py` 啟用或停用模組，並設定各自的 Modbus 站號：

```python
modules = {
  "switch": {"enable": True, "slave_id": 3},
  "temp":   {"enable": False, "slave_id": 1}
}
```

* `enable: True` → 啟用模組（會與指定的站號連線並回報 MQTT）
* `enable: False` → 停用模組
* `slave_id` → 需與你實際設備的 **Modbus 站號一致**

---

## 🔌 `modbus_mqtt_client.py` 使用說明

### 📌 檔案功能：

* 管理 **Modbus TCP** 與 **MQTT** 的共用連線
* 支援自動重連、鎖定防止重複操作
* 提供共用的 MQTT 客戶端與 Modbus 實例供模組呼叫

### 🔧 MQTT 參數設定（請依你自己的 Home Assistant 設定）

```python
# MQTT Broker 應設為安裝 Home Assistant 中的 Mosquitto broker 插件
MQTT_BROKER = '填入你的 Home Assistant IP'
MQTT_PORT = 1883
MQTT_USERNAME = 'your'
MQTT_PASSWORD = 'your'
```

### 🔧 Modbus 設定

```python
MODBUS_HOST = '你的 Modbus Gateway IP'
MODBUS_PORT = 502
```

> ✅ MQTT & Modbus 的連線資訊皆集中在此檔，便於統一管理與修改。

---

## ❗ 注意事項

* **MQTT Broker** 請使用 Home Assistant 的 [Mosquitto broker 插件](https://github.com/home-assistant/addons/blob/master/mosquitto/DOCS.md)，並填入 Home Assistant 的 IP。
* 每個模組的 `slave_id` 必須對應你實際的 Modbus 設備站號。


---

## 🧠 本專案由 ChatGPT 協助撰寫與優化

本 README 內容由 [OpenAI ChatGPT](https://openai.com/chatgpt) 撰寫與調整，若你日後新增模組或擴充功能，也可以請 ChatGPT 幫你改寫。

---

---

## 🇺🇸 English Version: Modbus TCP ↔ MQTT Integration with Python & Docker

# docker-compose-python-modbus-mqtt

> 📦 A lightweight Modbus TCP to MQTT integration via Python
> ✨ README generated and refined by [ChatGPT](https://openai.com/chatgpt)

---

## 📘 Project Overview

This project uses `docker-compose` to run a minimal Python environment for:

* Reading data from **Modbus TCP** devices
* Publishing to an **MQTT Broker** (e.g., Home Assistant's Mosquitto add-on)

Currently supported modules:

* `module_switch.py`: Relay / switch control
* `module_temp.py`: Temperature reading 

---

## 🚀 Quick Start

### 1️⃣ Install Python packages (inside container)

```bash
docker compose run python:3.11-slim
pip install -r requirements.txt
# Or manually:
pip install paho-mqtt==2.1.0 pymodbus==3.5.0
```

### 2️⃣ Start the container

```bash
docker compose up -d
```

---

## 📁 Project Structure

```
.
├── docker-compose.yaml      # Docker Compose file
├── Dockerfile               # Docker build file
├── requirements.txt         # Required packages
└── app/
    ├── main.py              # Main entrypoint and module loader
    ├── module_switch.py     # Relay control module
    ├── module_temp.py       # Temperature module 
    └── modbus_mqtt_client.py# Shared Modbus & MQTT connection handler
```

---

## ⚙️ Module Configuration (in `main.py`)

Each module must be explicitly enabled and assigned a proper Modbus slave ID:

```python
modules = {
  "switch": {"enable": True, "slave_id": 3},
  "temp":   {"enable": False, "slave_id": 1}
}
```

* `enable: True` → Enables the module
* `enable: False` → Disables the module
* `slave_id` → Must match the Modbus slave address of your physical device

---

## 🔌 `modbus_mqtt_client.py` Usage

### Purpose:

* Central management of **Modbus TCP** and **MQTT** clients
* Thread-safe, auto-reconnect logic
* Provides shared MQTT client and Modbus client to all modules

### MQTT Configuration

```python
# Broker = your Home Assistant IP with Mosquitto add-on installed
MQTT_BROKER = 'your-home-assistant-ip'
MQTT_PORT = 1883
MQTT_USERNAME = 'your'
MQTT_PASSWORD = 'your'
```

### Modbus Configuration

```python
MODBUS_HOST = 'your-modbus-gateway-ip'
MODBUS_PORT = 502
```

> ✅ All communication settings are centralized in this file for easier adjustments.

---

## ❗ Important Notes

* The MQTT Broker should be your **Home Assistant** Mosquitto add-on.
* Make sure your module `slave_id` matches the actual slave ID of your Modbus devices.


---

## 🧠 README generated by ChatGPT

This documentation was fully written and optimized using [ChatGPT](https://openai.com/chatgpt).
Future updates or new modules can also be described and generated through ChatGPT.

---

若你希望我直接幫你輸出為 `README.md` 檔案內容格式，請告訴我，我可以一次匯出完整檔案文字。
