# main.py

import threading
import module_switch
import module_temp

def main():
    # 模組啟用/停用開關（以站號或名稱區分）
    modules = {
        "switch": True,
        "temp": True,
        "humidity": False  # 如果未來有其他模組
    }

    threads = []

    if modules.get("switch"):
        t = threading.Thread(target=module_switch.run, name="SwitchModule")
        threads.append(t)

    if modules.get("temp"):
        t = threading.Thread(target=module_temp.run, args=(20,), name="TempModule")
        threads.append(t)

    # 依序啟動所有模組
    for t in threads:
        t.start()

    # 等待所有模組結束（一般會常駐）
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
