以下是完善後的 GitHub `README.md` 文件，先提供 **繁體中文版本**，接著是 **英文版本**。文末附有 ChatGPT 出處說明。

---

## 📘 繁體中文說明

# docker-compose-python-modbus-mqtt

本專案為使用 Python 3.11 製作的 Modbus TCP + MQTT 整合應用。
可讀取來自 Modbus Gateway 的數據，並透過 MQTT 發佈至 Home Assistant 等平台，支援 HA Discovery 自動註冊。

---

### 🐳 Docker 環境快速啟動

```bash
docker compose run python:3.11-slim
```

安裝所需 Python 套件：

```bash
pip install paho-mqtt==2.1.0 pymodbus==3.5.0
```

---

### ⚙️ 系統架構

```plaintext
[Modbus Gateway] → [Python Modbus Client] → [MQTT Broker] → [Home Assistant]
```

* 支援 Modbus TCP 功能碼 3（Holding Registers）、4（Input Registers）
* 可同時支援多個模組（如 JKBMS、Coil 控制器、串列設備等）
* 使用 `main.py` 啟動並集中管理模組

---

### 📁 專案結構說明

```
app/
├── main.py                 # 程式入口，集中載入模組
├── modbus_mqtt_client.py   # 管理 Modbus & MQTT 連線
├── module_jkbms.py         # JKBMS Modbus 數據讀取模組
├── jkbms_address.py        # JKBMS 地址定義表（供 module_jkbms 使用）
├── ... 更多模組 ...
```

---

### 🔧 啟用模組設定

在 `main.py` 的 `modules` 設定中：

```python
modules = {
    "jkbms": {
        "enable": True,           # 啟用該模組
        "slave_id": 3             # 設定其 Modbus 站號
    },
    "switch": {
        "enable": False           # 停用該模組
    }
}
```

---

### 💡 功能特色

* ✅ 支援多模組並行執行
* ✅ Modbus 錯誤自動重連
* ✅ MQTT 主動回報與 HA Discovery 註冊
* ✅ 地址表可獨立定義，便於維護與擴充

---

### 📜 作者與貢獻

本專案由 [ChatGPT](https://openai.com/chatgpt) 協助產出程式架構與文件說明，手動微調與測試由使用者完成。
歡迎提 issue 或 fork 本專案擴充其他設備支援！

---

## 📘 English Description

# docker-compose-python-modbus-mqtt

This project integrates **Modbus TCP and MQTT** using Python 3.11, designed to read data from Modbus gateways and publish them via MQTT for platforms like Home Assistant. MQTT Discovery is supported for automatic entity creation.

---

### 🐳 Quick Start with Docker

```bash
docker compose run python:3.11-slim
```

Install required dependencies:

```bash
pip install paho-mqtt==2.1.0 pymodbus==3.5.0
```

---

### ⚙️ System Architecture

```plaintext
[Modbus Gateway] → [Python Modbus Client] → [MQTT Broker] → [Home Assistant]
```

* Supports Modbus Function Codes 3 and 4
* Multi-module supported (JKBMS, coil controller, serial sensors...)
* Modules are managed and launched via `main.py`

---

### 📁 Project Structure

```
app/
├── main.py                 # Entry point
├── modbus_mqtt_client.py   # Modbus + MQTT connection manager
├── module_jkbms.py         # JKBMS Modbus data reader
├── jkbms_address.py        # Address definitions for JKBMS
├── ... more modules ...
```

---

### 🔧 Enable Modules

Inside `main.py`:

```python
modules = {
    "jkbms": {
        "enable": True,          # Enable this module
        "slave_id": 3
    },
    "switch": {
        "enable": False          # Disable this module
    }
}
```

---

### 💡 Features

* ✅ Modular architecture with threading
* ✅ Automatic Modbus reconnect
* ✅ MQTT + Home Assistant Discovery support
* ✅ Easy-to-extend address list

---

### 📜 Author & Credits

This project was generated with the assistance of [ChatGPT](https://openai.com/chatgpt) by OpenAI, including the code structure and documentation.
Final logic, testing, and deployment were managed manually by the user.
Feel free to fork and contribute new modules!

---

需要我幫你自動上傳 `README.md` 到 GitHub repo 嗎？或者協助製作 `docker-compose.yml`？隨時告訴我。
