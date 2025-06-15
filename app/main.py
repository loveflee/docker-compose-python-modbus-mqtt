# main.py
"""
📌 主程式
統一啟動所需的模組（switch, temp, ...）
並統一管理 Modbus Slave ID 及 ModbusManager
"""
from pymodbus.server.async_io import StartTcpServer
from pymodbus.datastore import ModbusServerContext
import importlib
import threading
import modbus_mqtt_client
import module_switch
import module_temp
# 新增這行來導入 modbus_read_coils
#import modbus_read_coils
# module_03 8dodi 監視乾接點輪巡每5秒一次修改在module_03.py time.sleep(5)

def main():
    # ========================
    # 🟡 模組啟用/停用與站號設定
    # ========================
    modules = {
      "switch": {"enable": True, "slave_id": 3},
      "temp": {"enable": False, "slave_id": 1}
    }

    # ========================
    # 🔵 首次啟動執行一次 modbus_read_coils
    # ========================
#    print("✅ 首次執行 modbus_read_coils.py")
$    coil_status = modbus_read_coils.read_coils()
$    if coil_status:
$        modbus_read_coils.publish_coil_status(coil_status)
$        print("✅ 首次同步狀態完成，已上報MQTT！")
$    else:
$        print("⚠️ 首次讀取線圈失敗，未發佈MQTT")

    # ========================
    # 🟠 建立執行緒並啟動模組
    # ========================
    threads = []


    if modules["switch"]["enable"]:
        t = threading.Thread(
            target=module_switch.run,
            args=(modules["switch"]["slave_id"], modbus_mqtt_client.modbus_manager),
            name="SwitchModule"
        )
        threads.append(t)


    if modules["temp"]["enable"]:
        t = threading.Thread(
            target=module_temp.run,
            args=(modules["temp"]["slave_id"], modbus_mqtt_client.modbus_manager),
            name="TempModule"
        )
        threads.append(t)


    # ========================
    # 🔵 啟動所有模組
    # ========================
    for t in threads:
        t.start()

    # ========================
    # 🔴 等待所有模組結束（通常常駐執行）
    # ========================
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
