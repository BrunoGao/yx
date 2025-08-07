FROM grafana/grafana:9.5.0

# 标签和元数据
LABEL maintainer="LJWX Team"
LABEL version="1.2.6"
LABEL description="LJWX定制化Grafana监控面板"

# 切换到root用户进行配置
USER root

# 复制定制化配置文件
COPY config/grafana/provisioning /etc/grafana/provisioning
COPY config/grafana/dashboards /var/lib/grafana/dashboards

# 设置正确的文件权限
RUN chown -R grafana:grafana /etc/grafana/provisioning && \
    chown -R grafana:grafana /var/lib/grafana/dashboards && \
    chmod -R 644 /etc/grafana/provisioning/* && \
    chmod -R 644 /var/lib/grafana/dashboards/*

# 创建必要的目录
RUN mkdir -p /var/lib/grafana/plugins && \
    chown -R grafana:grafana /var/lib/grafana/plugins

# 环境变量配置
ENV GF_SECURITY_ADMIN_PASSWORD=admin123
ENV GF_USERS_ALLOW_SIGN_UP=false
ENV GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH=/var/lib/grafana/dashboards/ljwx-ultimate-monitoring.json
ENV GF_FEATURE_TOGGLES_ENABLE=publicDashboards
ENV TZ=Asia/Shanghai

# 切换回grafana用户
USER grafana

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# 暴露端口
EXPOSE 3000 