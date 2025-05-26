# 使用官方 Python 运行时作为父镜像
FROM python:3.13.3-alpine

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到容器中的 /app
COPY . /app

# 安装任何所需的包
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口 3521
EXPOSE 3521

# 运行 server.py 当容器启动时
CMD ["python", "-m", "src.server"]