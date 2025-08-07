FROM grafana/promtail:2.9.0

# 标签和元数据
LABEL maintainer="LJWX Team"
LABEL version="1.2.6"
LABEL description="LJWX定制化Promtail日志收集配置"

# 切换到root用户进行配置
USER root

# 复制定制化配置文件
COPY config/promtail/promtail.yml /etc/promtail/config.yml

# 设置正确的文件权限
RUN chown promtail:promtail /etc/promtail/config.yml && \
    chmod 644 /etc/promtail/config.yml

# 创建必要的目录
RUN mkdir -p /tmp && \
    chown -R promtail:promtail /tmp

# 环境变量配置
ENV TZ=Asia/Shanghai

# 切换回promtail用户
USER promtail

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:9080/ready || exit 1

# 暴露端口
EXPOSE 9080

# 启动命令
CMD ["-config.file=/etc/promtail/config.yml"] 