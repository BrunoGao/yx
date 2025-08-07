FROM prom/alertmanager:latest

# 标签和元数据
LABEL maintainer="LJWX Team"
LABEL version="1.2.6"
LABEL description="LJWX定制化AlertManager告警管理配置"

# 切换到root用户进行配置
USER root

# 复制定制化配置文件
COPY config/alertmanager /etc/alertmanager

# 设置正确的文件权限
RUN chown -R alertmanager:alertmanager /etc/alertmanager && \
    chmod -R 644 /etc/alertmanager/*

# 创建数据目录
RUN mkdir -p /alertmanager && \
    chown -R alertmanager:alertmanager /alertmanager

# 环境变量配置
ENV TZ=Asia/Shanghai

# 切换回alertmanager用户
USER alertmanager

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:9093/-/healthy || exit 1

# 暴露端口
EXPOSE 9093

# 启动命令
CMD ["--config.file=/etc/alertmanager/alertmanager.yml", \
     "--storage.path=/alertmanager", \
     "--web.external-url=http://localhost:9093", \
     "--cluster.listen-address="] 