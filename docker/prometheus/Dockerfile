FROM prom/prometheus:v2.40.0

# 标签和元数据
LABEL maintainer="LJWX Team"
LABEL version="1.2.6"
LABEL description="LJWX定制化Prometheus监控配置"

# 切换到root用户进行配置
USER root

# 复制定制化配置文件
COPY config/prometheus /etc/prometheus

# 设置正确的文件权限
RUN chown -R prometheus:prometheus /etc/prometheus && \
    chmod -R 644 /etc/prometheus/*

# 创建数据目录
RUN mkdir -p /prometheus && \
    chown -R prometheus:prometheus /prometheus

# 环境变量配置
ENV TZ=Asia/Shanghai

# 切换回prometheus用户
USER prometheus

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:9090/-/ready || exit 1

# 暴露端口
EXPOSE 9090

# 启动命令
CMD ["--config.file=/etc/prometheus/prometheus.yml", \
     "--storage.tsdb.path=/prometheus", \
     "--web.console.libraries=/etc/prometheus/console_libraries", \
     "--web.console.templates=/etc/prometheus/consoles", \
     "--storage.tsdb.retention.time=30d", \
     "--web.enable-lifecycle"] 