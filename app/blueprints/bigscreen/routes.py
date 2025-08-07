from flask import render_template, request, jsonify
from . import bigscreen_bp
from ..services.bigscreen_service import BigscreenService
import logging

logger = logging.getLogger(__name__)

# 大屏页面路由
@bigscreen_bp.route("/personal")
def personal():
    deviceSn = request.args.get('deviceSn')
    logger.info(f"访问个人大屏页面，deviceSn: {deviceSn}")
    return render_template("personal.html", deviceSn=deviceSn)

@bigscreen_bp.route("/personal_new")
def personal_new():
    deviceSn = request.args.get('deviceSn')
    logger.info(f"访问新版个人大屏页面，deviceSn: {deviceSn}")
    return render_template("personal_new.html", deviceSn=deviceSn)

@bigscreen_bp.route("/personal_cool")
def personal_cool():
    deviceSn = request.args.get('deviceSn')
    logger.info(f"访问酷炫个人大屏页面，deviceSn: {deviceSn}")
    return render_template("bigscreen_new.html", deviceSn=deviceSn)

@bigscreen_bp.route("/main")
def main():
    customerId = request.args.get('customerId')
    logger.info(f"访问主大屏页面，customerId: {customerId}")
    return render_template("bigscreen_main.html", customerId=customerId)

@bigscreen_bp.route("/optimize")
def optimize():
    customerId = request.args.get('customerId')
    logger.info(f"访问优化大屏页面，customerId: {customerId}")
    return render_template("bigscreen_optimized.html", customerId=customerId)

@bigscreen_bp.route("/index")
def index():
    customerId = request.args.get('customerId')
    logger.info(f"访问首页大屏，customerId: {customerId}")
    return render_template("index.html", customerId=customerId)

@bigscreen_bp.route("/alert")
def alert():
    logger.info("访问告警大屏页面")
    return render_template("alert.html")

@bigscreen_bp.route("/message")
def message():
    logger.info("访问消息大屏页面")
    return render_template("message.html")

@bigscreen_bp.route("/map")
def map_view():
    deviceSn = request.args.get('deviceSn')
    date_str = request.args.get('date_str')
    customerId = request.args.get('customerId')
    logger.info(f"访问地图大屏页面，deviceSn: {deviceSn}, date_str: {date_str}, customerId: {customerId}")
    return render_template("map.html", deviceSn=deviceSn, date_str=date_str, customerId=customerId)

@bigscreen_bp.route("/chart")
def chart():
    logger.info("访问图表大屏页面")
    return render_template("chart.html")

@bigscreen_bp.route("/chat")
def chat():
    logger.info("访问聊天大屏页面")
    return render_template("chat.html")

@bigscreen_bp.route("/track_view")
def track_view():
    logger.info("访问轨迹视图页面")
    return render_template("track_view.html")

@bigscreen_bp.route("/test_body")
def test_body():
    logger.info("访问测试页面")
    return render_template("test_body.html")

@bigscreen_bp.route("/health_table")
def health_table():
    logger.info("访问健康数据表格页面")
    return render_template("health_table.html")

@bigscreen_bp.route("/health_trends")
def health_trends():
    logger.info("访问健康趋势页面")
    return render_template("health_trends.html")

@bigscreen_bp.route("/health_main")
def health_main():
    logger.info("访问健康主页面")
    return render_template("health_main.html")

@bigscreen_bp.route("/health_baseline")
def health_baseline():
    logger.info("访问健康基线页面")
    return render_template("health_baseline.html")

@bigscreen_bp.route("/user_health_data_analysis")
def user_health_data_analysis():
    logger.info("访问健康数据分析页面")
    return render_template("user_health_data_analysis.html")

@bigscreen_bp.route("/health_profile")
def health_profile():
    logger.info("访问健康画像管理页面")
    return render_template("health_profile.html")

@bigscreen_bp.route("/config_management")
def config_management():
    logger.info("访问配置管理页面")
    return render_template("config_management.html")

@bigscreen_bp.route("/device_bind")
def device_bind():
    logger.info("访问设备绑定管理页面")
    return render_template("device_bind.html")

@bigscreen_bp.route("/test")
def test():
    logger.info("访问测试页面")
    return render_template("test.html")

@bigscreen_bp.route("/filter_test")
def filter_test():
    logger.info("访问过滤器测试页面")
    return render_template("filter_test.html")

@bigscreen_bp.route("/personal_health_data")
def personal_health_data():
    logger.info("访问个人健康数据页面")
    return render_template("personal_health_data.html")

@bigscreen_bp.route("/device_analysis")
def device_analysis():
    logger.info("访问设备分析页面")
    return render_template("device_analysis.html")

@bigscreen_bp.route("/device_dashboard")
def device_dashboard():
    logger.info("访问设备监控大屏页面")
    return render_template("device_dashboard.html")

@bigscreen_bp.route("/device_detailed_analysis")
def device_detailed_analysis():
    logger.info("访问设备详细分析页面")
    return render_template("device_detailed_analysis.html")

@bigscreen_bp.route("/personal_3d")
def personal_3d():
    logger.info("访问3D人体模型页面")
    return render_template("personal_3d.html")

@bigscreen_bp.route("/personal_advanced")
def personal_advanced():
    logger.info("访问高级3D人体模型页面")
    return render_template("personal_advanced.html")

@bigscreen_bp.route("/phone_login")
def phone_login():
    logger.info("访问手机登录页面")
    return render_template("phone_login.html")

@bigscreen_bp.route("/system_event_alert")
def system_event_alert():
    logger.info("访问系统事件告警页面")
    return render_template("system_event_alert.html")

# 通用模板路由
@bigscreen_bp.route('/<template>')
def render_template_view(template):
    logger.info(f"访问通用模板页面: {template}")
    return render_template(f"{template}.html") 