FROM grafana/loki:2.9.0

# 标签和元数据
LABEL maintainer="LJWX Team"
LABEL version="1.2.6"
LABEL description="LJWX定制化Loki日志聚合配置"

# 切换到root用户进行配置
USER root

# 复制定制化配置文件
COPY config/loki/loki.yml /etc/loki/local-config.yaml

# 设置正确的文件权限
RUN chown loki:loki /etc/loki/local-config.yaml && \
    chmod 644 /etc/loki/local-config.yaml

# 创建必要的目录
RUN mkdir -p /loki/chunks /loki/rules /loki/boltdb-shipper-active /loki/boltdb-shipper-cache /loki/rules-temp && \
    chown -R loki:loki /loki

# 环境变量配置
ENV TZ=Asia/Shanghai

# 切换回loki用户
USER loki

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3100/ready || exit 1

# 暴露端口
EXPOSE 3100

# 启动命令
CMD ["-config.file=/etc/loki/local-config.yaml"] 