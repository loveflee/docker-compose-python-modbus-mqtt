# 使用官方 Python 映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 複製需求檔案
COPY requirements.txt .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 不複製程式碼到 image（因為 volumes 掛載）
# COPY app .   <-- 這行刪除

# 預設執行指令
CMD ["python", "main.py"]

# 使用官方 Python 映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 複製需求檔案
COPY requirements.txt .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 不複製程式碼到 image（因為 volumes 掛載）
# COPY app .   <-- 這行刪除

# 預設執行指令
CMD ["python", "main.py"]
