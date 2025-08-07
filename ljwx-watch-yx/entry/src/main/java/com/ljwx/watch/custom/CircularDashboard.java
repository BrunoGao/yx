package com.ljwx.watch.custom;

import com.ljwx.watch.utils.DataManager;
import ohos.agp.animation.Animator;
import ohos.agp.animation.AnimatorValue;
import ohos.agp.components.*;
import ohos.agp.render.*;
import ohos.agp.utils.Color;
import ohos.agp.utils.Point;
import ohos.agp.utils.RectFloat;
import ohos.agp.utils.TextAlignment;
import ohos.agp.window.dialog.CommonDialog;
import ohos.app.Context;
import ohos.global.resource.NotExistException;
import ohos.global.resource.Resource;
import ohos.global.resource.ResourceManager;
import ohos.hiviewdfx.HiLog;
import ohos.hiviewdfx.HiLogLabel;
import ohos.media.image.ImageSource;
import ohos.media.image.PixelMap;
import ohos.media.image.common.PixelFormat;
import ohos.eventhandler.EventHandler;
import ohos.eventhandler.EventRunner;

import java.io.IOException;
import java.util.List;

import com.ljwx.watch.ResourceTable;
import ohos.media.image.common.Size;
import ohos.multimodalinput.event.TouchEvent;

public class CircularDashboard extends Component {

    private boolean isPickerShown = false;
    private boolean isRingShown = false;
    private boolean isAnimationStarted = false;

    private DataManager dataManager = DataManager.getInstance();

    private final RectFloat centerRectFloat = new RectFloat();

    private Paint arcPaint;
    private Paint textPaint;

    private String customerName = "灵境万象";

    private RectFloat arcRect;
    private final float strokeWidth = 8.0f;
    private final float gapAngle = 1.0f;
    private boolean isheartRateExceeded = false;
    private boolean isbloodOxygenLow = false;
    private boolean showSimplePage = true;
    private boolean isAnimationComplete = false; // 标志动画是否完成
    private boolean isBluetoothReady = false; // 新增变量来标识蓝牙设备是否准备好
    private float animatedSweepAngle = 0; // 动画当前进度
    private final int[][] gradientColors = {
            {0xFFFF0000, 0xFFFFA500}, // 红色 -> 橙色
            {0xFFFFA500, 0xFFFFFF00}, // 橙色 -> 黄色
            {0xFFFFFF00, 0xFF00FF00}, // 黄色 -> 绿色
            {0xFF00FF00, 0xFF00FFFF}, // 绿色 -> 蓝绿色
            {0xFF00FFFF, 0xFF0000FF}, // 蓝绿色 -> 蓝色
            {0xFF0000FF, 0xFF800080}, // 蓝色 -> 紫色
            {0xFF800080, 0xFFFF1493}, // 紫色 -> 深粉色
            {0xFFFF1493, 0xFFFF0000}  // 深粉色 -> 红色
    };

    private Paint infoPaint; // 新增的 Paint，用于绘制动画文字

    private String heartRateText = "心率";
    private String heartRateValue = "-";

    private String bloodOxygenText = "血氧";
    private String bloodOxygenValue = "-";

    private String temperatureText = "体温";
    private String temperatureValue = "-";

    private String stressText = "压力";
    private String stressValue = "-";

    private String pressureText = "血压";
    private String pressureValue = "-";

    private String pressureHighText = "高压";
    private String pressureHighValue = "-";

    private String pressureLowText = "低压";
    private String pressureLowValue = "-";

    private String stepText = "步数";
    private String stepValue = "-";
    private Boolean isSelected = false;


    private String bloodOxygenFullText = "血氧";
    private String heartRateFullText = "心";


    private int width = 240;
    private int height = 240;

    private String[] deviceNames;
    private Picker devicePicker;
    private Text scanningText;
    private CommonDialog dialog;

    private String appStatus = "灵境万象";

    private static final HiLogLabel LABEL_LOG = new HiLogLabel(3, 0xD001100, "ljwx-log");

    private EventHandler handler = new EventHandler(EventRunner.getMainEventRunner());

    public CircularDashboard(Context context) {
        super(context);
        init();

    }

    public CircularDashboard(Context context, AttrSet attrSet) {
        super(context, attrSet);
        init();
    }


    public void drawLogoInfo(Canvas canvas,float cx, float cy) {

        PixelMap pixelMap = loadPixelMap(getContext(), ResourceTable.Media_icon);
        if (pixelMap != null) {
            Paint paint = new Paint();
            canvas.drawPixelMapHolder(new PixelMapHolder(pixelMap), cx, cy, paint);

            //int inRadius = radius - (circleWidth >> 1);
            double inRadius = 0.1f;
            centerRectFloat.left = (float) (width / 2 - Math.sqrt(2) * inRadius);
            centerRectFloat.top = (float) (height / 2 - Math.sqrt(2) * inRadius);
            centerRectFloat.right = (float) (width / 2 + Math.sqrt(2) * inRadius);
            centerRectFloat.bottom = (float) (height / 2 + Math.sqrt(2) * inRadius);

            // 如果图片比较小，那么根据图片的尺寸放置到正中心
            Size imageSize = pixelMap.getImageInfo().size;
            if (imageSize.width < Math.sqrt(2) * inRadius) {
                centerRectFloat.left = (width - imageSize.width * 1.0f) / 2;
                centerRectFloat.top = (height - imageSize.height * 1.0f) / 2;
                centerRectFloat.right = (width + imageSize.width * 1.0f) / 2;
                centerRectFloat.bottom = (height + imageSize.height * 1.0f) / 2;
            }
            canvas.drawPixelMapHolderRect(new PixelMapHolder(pixelMap), centerRectFloat, paint);
        }
    }
    public PixelMap loadPixelMap(Context context, int resId) {
        ResourceManager resourceManager = context.getResourceManager();
        if (resourceManager == null) {
            return null;
        }

        try (Resource resource = resourceManager.getResource(resId)) {
            ImageSource.SourceOptions sourceOptions = new ImageSource.SourceOptions();
            ImageSource imageSource = ImageSource.create(resource, sourceOptions);
            ImageSource.DecodingOptions decodingOptions = new ImageSource.DecodingOptions();
            decodingOptions.desiredPixelFormat = PixelFormat.ARGB_8888;
            return imageSource.createPixelmap(decodingOptions);
        } catch (IOException | NotExistException e) {
            e.printStackTrace();
        }
        return null;
    }

    private void init() {
        arcPaint = new Paint();
        arcPaint.setAntiAlias(true);
        arcPaint.setStyle(Paint.Style.STROKE_STYLE);
        arcPaint.setStrokeWidth(strokeWidth);
        arcPaint.setStrokeCap(Paint.StrokeCap.ROUND_CAP);

        textPaint = new Paint();
        textPaint.setAntiAlias(true);
        textPaint.setColor(new Color(Color.getIntColor("#FFFFFF")));
        textPaint.setTextAlign(TextAlignment.LEFT);
        textPaint.setTextSize(36);


        infoPaint = new Paint(); // 初始化动画文字 Paint
        infoPaint.setAntiAlias(true);
        infoPaint.setColor(new Color(Color.getIntColor("#FFFFFF")));
        infoPaint.setTextAlign(TextAlignment.CENTER);
        infoPaint.setTextSize(50);

        customerName = dataManager.getCustomerName() != null ? dataManager.getCustomerName() : "灵境万象";
        //HiLog.info(LABEL_LOG,  "UI::customerName:" + customerName);

        //HiLog.info(LABEL_LOG,  "UI::addDrawTask:");

        addDrawTask((canvas, component) -> drawArcComponent(component, canvas));

        //HiLog.info(LABEL_LOG,  "UI::startArcAnimation:");
        startArcAnimation();

        handler.postTask(() -> {
            isAnimationComplete = true;
            invalidate();
        }, 2000); // 1.5 seconds delay
    }

    private void startArcAnimation() {

        AnimatorValue animator = new AnimatorValue();
        animator.setDuration(1500); // 1秒
        animator.setCurveType(Animator.CurveType.LINEAR);

        animator.setValueUpdateListener((animatorValue, value) -> {
            animatedSweepAngle = 360 * value;
            invalidate();
        });

        animator.setStateChangedListener(new Animator.StateChangedListener() {
            @Override
            public void onStart(Animator animator) {}

            @Override
            public void onStop(Animator animator) {
                isAnimationComplete = true;
                invalidate();
            }

            @Override
            public void onCancel(Animator animator) {
                isAnimationComplete = true;
            }

            @Override
            public void onEnd(Animator animator) {
                isAnimationComplete = true;
                invalidate();
            }

            @Override
            public void onPause(Animator animator) {}

            @Override
            public void onResume(Animator animator) {}
        });

        animator.start();
    }

    public void alert(String heartRateValue, boolean isheartRateExceeded) {
        this.heartRateValue = heartRateValue;
        this.isheartRateExceeded = isheartRateExceeded;
        invalidate();
    }

    public void updateDashboard(String heartRateValue, String bloodOxygenValue,String temperatureValue, String pressureHighValue, String pressureLowValue, String stressValue, String stepValue, String appStatus) {
        this.heartRateValue = heartRateValue;
        this.bloodOxygenValue = bloodOxygenValue;
        this.temperatureValue = temperatureValue;
        this.stressValue = stressValue;
        this.stepValue = stepValue;
        this.pressureValue = pressureHighValue + "/" + pressureLowValue;
        this.pressureHighValue = pressureHighValue;
        this.pressureLowValue = pressureLowValue;
        this.appStatus = appStatus;
        invalidate();  // Only call invalidate once after all updates
    }

    private void drawArcComponent(Canvas canvas, Component component) {
        float minDimension = Math.min(component.getWidth(), component.getHeight());
        float radius = minDimension / 2.0f - strokeWidth;
        float cx = component.getWidth() / 2.0f;
        float cy = component.getHeight() / 2.0f;
        arcRect = new RectFloat(cx - radius, cy - radius, cx + radius, cy + radius);

        if (!isAnimationComplete) {
            drawColoredArcAnimation(canvas);
            //drawArcComponentAnimation(canvas, component);
            drawAnimationInfo(canvas, cx, cy);

        } else {
            //drawColoredArc(canvas);
            drawArcComponent1(canvas, component);
            fullPage(canvas, cx, cy);
            /* 

            if("wifi".equals(dataManager.getUploadMethod())){
                fullPage(canvas, cx, cy);
            }else{
                if (!isSelected ){
                    //HiLog.info(LABEL_LOG,  dataManager.getScanStatus() + " isSelected:" + isSelected + " size " + dataManager.getDeviceNames().size());
                    showBluetoothDevicePicker();
                } else{
                    fullPage(canvas, cx, cy);
                }
            }
            */
        }
    }

    private void showBluetoothDevicePicker() {
        float minDimension = Math.min(getWidth(), getHeight());
        float diameter = minDimension - 2 * strokeWidth;

        if (dialog == null) {
            dialog = new CommonDialog(getContext());
            dialog.setSize((int) diameter, (int) diameter);
            dialog.setAutoClosable(true);
            dialog.setTransparent(true);

            DependentLayout layout = new DependentLayout(getContext());
            layout.setWidth((int) diameter);
            layout.setHeight((int) diameter);

            // 初始化 Picker
            devicePicker = new Picker(getContext());
            devicePicker.setWidth((int) diameter);
            devicePicker.setHeight((int) diameter);
            devicePicker.setNormalTextSize(35);
            devicePicker.setNormalTextColor(new Color(Color.getIntColor("#FFA500")));
            devicePicker.setSelectedTextSize(40); // 设置选中项的字体大小
            devicePicker.setSelectedTextColor(new Color(Color.getIntColor("#f36112")));
            devicePicker.setSelectedNormalTextMarginRatio(5.0f);

            // 初始化扫描提示
            scanningText = new Text(getContext());
            scanningText.setText("蓝牙扫描中...");
            scanningText.setTextSize(35);
            scanningText.setTextColor(Color.YELLOW);
            scanningText.setTextAlignment(TextAlignment.CENTER);
            scanningText.setWidth((int) diameter);
            scanningText.setHeight((int) diameter);

            layout.addComponent(devicePicker);
            layout.addComponent(scanningText);
            dialog.setContentCustomComponent(layout);
        }

        // 更新 Picker 数据
        List<String> names = dataManager.getDeviceNames();
        HiLog.info(LABEL_LOG, "UI::deviceNames:" + names.toString());
        deviceNames = names.toArray(new String[0]);

        if (deviceNames.length == 0) {
            // 如果 names 为空，显示 "蓝牙扫描中"
            devicePicker.setVisibility(Component.HIDE);
            scanningText.setVisibility(Component.VISIBLE);
        } else {
            devicePicker.setDisplayedData(deviceNames);
            devicePicker.setVisibility(Component.VISIBLE);
            scanningText.setVisibility(Component.HIDE);

            devicePicker.setTouchEventListener(new TouchEventListener() {
                @Override
                public boolean onTouchEvent(Component component, TouchEvent touchEvent) {
                    if (touchEvent.getAction() == TouchEvent.PRIMARY_POINT_UP) {
                        // 单击事件
                        int newVal = devicePicker.getValue();
                        //HiLog.info(LABEL_LOG, "UI::newVal:" + newVal);
                        if(deviceNames.length==1){
                            newVal = 0;
                        }
                        String selectedDevice = deviceNames[newVal];
                        HiLog.info(LABEL_LOG, "UI::choose to connect:" + selectedDevice);
                        devicePicker.setVisibility(Component.HIDE);  // 确保 Picker 隐藏
                        dialog.hide();
                        isPickerShown = false;
                        isSelected = true;
                        dataManager.setDeviceName(selectedDevice);
                        //HiLog.info(LABEL_LOG, "UI::dataManager.setDeviceName::" + dataManager.getDeviceName());
                    }
                    return true;
                }
            });
        }

        if (!isPickerShown) {
            dialog.show();
            isPickerShown = true;
        }
    }

    private void drawAnimationInfo(Canvas canvas, float cx, float cy) {
        //HiLog.info(LABEL_LOG, "UI::drawAnimationInfo::" );

        canvas.drawText(infoPaint, dataManager.getCustomerName(), cx, cy + 10);
        //System.out.println("jjgao::drawAnimationInfo");
    }
    private void drawColoredArc(Canvas canvas) {
        //if(isRingShown) return;
        float currentAngle = 0;
        float anglePerSegment = 360 / gradientColors.length - gapAngle;

        for (int i = 0; i < gradientColors.length; i++) {
            drawArcSegment(canvas, currentAngle, anglePerSegment, gradientColors[i]);
            currentAngle += anglePerSegment + gapAngle;
        }
        isRingShown = true;
        //System.out.println("jjgao::drawColoredArc");
    }


    private void drawColoredArcAnimation(Canvas canvas) {
        float currentAngle = 0;
        float anglePerSegment = 360 / gradientColors.length - gapAngle;


        for (int i = 0; i < gradientColors.length; i++) {
            if (currentAngle + anglePerSegment > animatedSweepAngle) {
                drawArcSegment(canvas, currentAngle, animatedSweepAngle - currentAngle, gradientColors[i]);
                break;
            } else {
                drawArcSegment(canvas, currentAngle, anglePerSegment, gradientColors[i]);
                currentAngle += anglePerSegment + gapAngle;
            }
        }
    }

    private void drawArcSegment(Canvas canvas, float startAngle, float sweepAngle, int[] colors) {
        float startAngleRad = (float) Math.toRadians(startAngle);
        float endAngleRad = (float) Math.toRadians(startAngle + sweepAngle);

        float startX = (float) (arcRect.getHorizontalCenter() + Math.cos(startAngleRad) * arcRect.getWidth() / 2);
        float startY = (float) (arcRect.getVerticalCenter() + Math.sin(startAngleRad) * arcRect.getHeight() / 2);

        float endX = (float) (arcRect.getHorizontalCenter() + Math.cos(endAngleRad) * arcRect.getWidth() / 2);
        float endY = (float) (arcRect.getVerticalCenter() + Math.sin(endAngleRad) * arcRect.getHeight() / 2);

        Point[] points = {new Point(startX, startY), new Point(endX, endY)};

        Color[] shaderColors = {new Color(colors[0]), new Color(colors[1])};

        Shader shader = new LinearShader(points, null, shaderColors, Shader.TileMode.CLAMP_TILEMODE);
        arcPaint.setShader(shader, Paint.ShaderType.LINEAR_SHADER);

        Arc arc = new Arc(startAngle, sweepAngle, false);
        canvas.drawArc(arcRect, arc, arcPaint);
    }
    private void drawArcComponent1(Canvas canvas, Component component) {
        float minDimension = Math.min(component.getWidth(), component.getHeight());
        float radius = minDimension / 2.0f - strokeWidth;
        float cx = component.getWidth() / 2.0f;
        float cy = component.getHeight() / 2.0f;
        arcRect = new RectFloat(cx - radius, cy - radius, cx + radius, cy + radius);
    
        drawArcSegment(canvas, 0, 40 - gapAngle, gradientColors[0]);
        drawArcSegment(canvas, 45, 40 - gapAngle, gradientColors[1]);
        drawArcSegment(canvas, 90, 40 - gapAngle, gradientColors[2]);
        drawArcSegment(canvas, 135, 40 - gapAngle, gradientColors[3]);
        drawArcSegment(canvas, 180, 40 - gapAngle, gradientColors[4]);
        drawArcSegment(canvas, 225, 40 - gapAngle, gradientColors[5]);
        drawArcSegment(canvas, 270, 40 - gapAngle, gradientColors[6]);
        drawArcSegment(canvas, 315, 40 - gapAngle, gradientColors[7]);

    }
    private void drawArcComponentAnimation(Canvas canvas, Component component) {
        float minDimension = Math.min(component.getWidth(), component.getHeight());
        float radius = minDimension / 2.0f - strokeWidth;
        float cx = component.getWidth() / 2.0f;
        float cy = component.getHeight() / 2.0f;
        arcRect = new RectFloat(cx - radius, cy - radius, cx + radius, cy + radius);
    
        AnimatorValue animator = new AnimatorValue();
        animator.setDuration(2000); // 2 seconds
        animator.setCurveType(Animator.CurveType.LINEAR);
    
        animator.setValueUpdateListener((animatorValue, value) -> {
            float animatedSweepAngle = 360 * value; // Full circle over the duration
            float currentAngle = 0;
            float anglePerSegment = 360 / gradientColors.length - gapAngle;
    
            for (int i = 0; i < gradientColors.length; i++) {
                if (currentAngle + anglePerSegment > animatedSweepAngle) {
                    drawArcSegment(canvas, currentAngle, animatedSweepAngle - currentAngle, gradientColors[i]);
                    break;
                } else {
                    drawArcSegment(canvas, currentAngle, anglePerSegment, gradientColors[i]);
                    currentAngle += anglePerSegment + gapAngle;
                }
            }
            HiLog.info(LABEL_LOG, "Animating: Sweep Angle = " + animatedSweepAngle);
            invalidate(); // Redraw the component
        });
    
        animator.setStateChangedListener(new Animator.StateChangedListener() {
            @Override
            public void onStart(Animator animator) {
                HiLog.info(LABEL_LOG, "Animation started");
            }

            @Override
            public void onStop(Animator animator) {
                HiLog.info(LABEL_LOG, "Animation stopped");
            }

            @Override
            public void onCancel(Animator animator) {
                HiLog.info(LABEL_LOG, "Animation canceled");
            }

            @Override
            public void onEnd(Animator animator) {
                HiLog.info(LABEL_LOG, "Animation ended");
            }

            @Override
            public void onPause(Animator animator) {}

            @Override
            public void onResume(Animator animator) {}
        });
    
        animator.start();
    }


    private void drawChemicalSymbol(Canvas canvas, Paint paint, String symbol, float cx, float cy, int baseSize) {
        float currentX = cx - calculateTextWidth(paint, symbol, baseSize) / 2;
        for (char ch : symbol.toCharArray()) {
            if (Character.isDigit(ch)) {
                paint.setTextSize(Math.round(baseSize * 0.75f * 0.75f)); // 数字
            } else if (Character.isLowerCase(ch) || Character.isUpperCase(ch)) {
                paint.setTextSize(Math.round(baseSize * 0.75f )); // 英文
            } else {
                paint.setTextSize(baseSize); // 中文或其他字符
            }
            String charStr = String.valueOf(ch);
            canvas.drawText(paint, charStr, currentX, cy);
            currentX += paint.measureText(charStr);
        }
        paint.setTextSize(baseSize); // 恢复原始大小
    }

    private float calculateTextWidth(Paint paint, String text, int baseSize) {
        float width = 0;
        for (char ch : text.toCharArray()) {
            if (Character.isDigit(ch)) {
                paint.setTextSize(Math.round(baseSize * 0.75f * 0.75f));
            } else if (Character.isLowerCase(ch) || Character.isUpperCase(ch)) {
                paint.setTextSize(Math.round(baseSize * 0.75f ));
            } else {
                paint.setTextSize(baseSize);
            }
            width += paint.measureText(String.valueOf(ch));
        }
        return width;
    }
    private void drawValueCentered(Canvas canvas, String value, float cx, float cy, int textSize, Color color) {
        textPaint.setTextSize(textSize);
        textPaint.setColor(color);
        float width = textPaint.measureText(value);
        canvas.drawText(textPaint, value, cx - width / 2, cy);
    }

    private void alertPage(Canvas canvas, float cx, float cy) {
        int baseTextSize = 60; // 字体大小为60
        textPaint.setColor(Color.WHITE); // 设置文本颜色为白色

        if(isbloodOxygenLow){
            drawCenteredText(canvas, bloodOxygenFullText, cx, cy - baseTextSize / 2, baseTextSize, Color.RED);
            drawValueCentered(canvas, bloodOxygenValue, cx, cy + 40, baseTextSize, Color.RED); // 红色
        }else if(isheartRateExceeded){
            drawCenteredText(canvas, heartRateFullText, cx, cy - baseTextSize / 2, baseTextSize, Color.RED);
            drawValueCentered(canvas, heartRateValue, cx, cy + 40, baseTextSize, Color.RED); // 红色
        }
        

    }
    private void drawCenteredText(Canvas canvas, String text, float cx, float cy,  int textSize, Color color) {
        textPaint.setTextSize(textSize);
        textPaint.setColor(color);
        float textWidth = textPaint.measureText(text);
        canvas.drawText(textPaint, text, cx - textWidth / 2, cy);
    }

    private void simplePage(Canvas canvas, float cx, float cy) {
        int baseTextSize = 40; // 字体大小为40
        float verticalSpacing = baseTextSize * 1.5f; // 垂直间隔

    
        float totalWidth = drawCenteredTextWithValue(canvas, heartRateFullText, heartRateValue, cx, cy - verticalSpacing, textPaint, baseTextSize, Color.WHITE, Color.RED);

        drawCenteredTextWithValue(canvas, bloodOxygenFullText, bloodOxygenFullText, cx, cy+40, textPaint, baseTextSize, Color.WHITE, Color.GREEN);
    }

    private void simplePage_alert(Canvas canvas, float cx, float cy) {
        int baseTextSize = 40; // 字体大小为40
        float verticalSpacing = baseTextSize * 1.5f; // 垂直间隔

        // 甲烷
        float totalWidth = drawCenteredTextWithValue(canvas, heartRateFullText, heartRateValue, cx, cy - verticalSpacing, textPaint, baseTextSize, Color.RED, Color.RED);

        // 氧气
        drawCenteredTextWithValue(canvas, bloodOxygenFullText, bloodOxygenValue, cx, cy+40, textPaint, baseTextSize, Color.RED, Color.RED);
    }

    private void fullPage(Canvas canvas, float cx, float cy) {
        int baseTextSize = 35; // 字体大小为30
        int unitTextSize = 25; // 单位字体大小为25
        float verticalSpacing = baseTextSize * 3; // 垂直间隔
        String temperatureUnit = "°C";
        String bloodOxygenUnit = "%";
        String stepUnit = "步";
        String stressUnit = "";
        String pressureUnit = "";
        String heartRateUnit = "bpm";
        String copyright = "@" + dataManager.getCustomerName();
        if(dataManager.isLicenseExceeded()){
            copyright = "超出license数量";
        }
        if(dataManager.getIsHealthServiceReady() == false){
            copyright = "服务不可用";
        }
   
        drawCenteredTextWithValueAndUnit(canvas, heartRateText, heartRateValue, heartRateUnit, cx, cy - verticalSpacing, textPaint, baseTextSize, unitTextSize, Color.WHITE, Color.RED);
        if(!dataManager.isSupportStress() && !dataManager.isSupportStep()){
            drawCenteredTextWithValueAndUnit(canvas, pressureHighText, pressureHighValue, pressureUnit, cx  - 100, cy, textPaint, baseTextSize, unitTextSize, Color.WHITE, Color.YELLOW);
        }else{
            drawCenteredTextWithValueAndUnit(canvas, pressureText, pressureValue, pressureUnit, cx - 100, cy, textPaint, baseTextSize, unitTextSize, Color.WHITE, Color.YELLOW);
        }
        drawCenteredTextWithValueAndUnit(canvas, temperatureText, temperatureValue, temperatureUnit, cx + 120, cy, textPaint, baseTextSize, unitTextSize, Color.WHITE, Color.YELLOW);
       
        if(!dataManager.isSupportStress() && !dataManager.isSupportStep()){
            drawCenteredTextWithValueAndUnit(canvas, pressureLowText, pressureLowValue, pressureUnit, cx - 80, cy + verticalSpacing, textPaint, baseTextSize, unitTextSize, Color.WHITE, Color.GREEN); 
        }else if(dataManager.isSupportStress()){
            drawCenteredTextWithValueAndUnit(canvas, stressText, stressValue, stressUnit, cx - 80, cy + verticalSpacing, textPaint, baseTextSize, unitTextSize, Color.WHITE, Color.YELLOW);
        
        }else{
            drawCenteredTextWithValueAndUnit(canvas, stepText, stepValue, stepUnit, cx - 80, cy + verticalSpacing, textPaint, baseTextSize, unitTextSize, Color.WHITE, Color.CYAN);
          }

        drawCenteredTextWithValueAndUnit(canvas, bloodOxygenText, bloodOxygenValue, bloodOxygenUnit, cx + 120, cy + verticalSpacing, textPaint, baseTextSize, unitTextSize, Color.WHITE, Color.GREEN);

        drawCenteredTextWithValueAndUnit(canvas, "", "", copyright, cx, cy + verticalSpacing + verticalSpacing , textPaint, baseTextSize, unitTextSize, Color.WHITE, Color.WHITE);

    }

    private float drawCenteredTextWithValueAndUnit(Canvas canvas, String text, String value, String unit, float cx, float cy, Paint paint, int textSize, int unitTextSize, Color textColor, Color valueColor) {
        paint.setTextSize(textSize);
        float textWidth = paint.measureText(text);
        float valueWidth = paint.measureText(value);

        paint.setTextSize(unitTextSize);
        float unitWidth = paint.measureText(unit);

        float totalWidth = textWidth + valueWidth + unitWidth + 10; // 增加10px间隔

        // 绘制文本
        paint.setTextSize(textSize);
        paint.setColor(textColor);
        float startX = cx - totalWidth / 2;
        canvas.drawText(paint, text, startX, cy);

        // 绘制数值
        paint.setColor(valueColor);
        canvas.drawText(paint, value, startX + textWidth + 10, cy); // 在文本后面添加10px间隔然后绘制数值

        // 绘制单位
        paint.setTextSize(unitTextSize);
        canvas.drawText(paint, unit, startX + textWidth + valueWidth + 10, cy); // 在数值后面添加10px间隔然后绘制单位

        return totalWidth;
    }

    /**
     * 绘制居中的文本和对应的数值。
     *
     * @param canvas 绘制的画布
     * @param text 要绘制的文本
     * @param value 要绘制的数值
     * @param cx 中心x坐标
     * @param cy 中心y坐标
     * @param paint 画笔对象
     * @param textSize 文本大小
     * @param textColor 文本颜色
     * @param valueColor 数值颜色
     * @return 返回绘制内容的总宽度
     */
    private float drawCenteredTextWithValue(Canvas canvas, String text, String value, float cx, float cy, Paint paint, int textSize, Color textColor, Color valueColor) {
        paint.setTextSize(textSize);
        float textWidth = paint.measureText(text);
        float valueWidth = paint.measureText(value);

        float totalWidth = textWidth + valueWidth + 10; // 增加10px间隔

        // 绘制文本
        paint.setColor(textColor);
        float startX = cx - totalWidth / 2;
        canvas.drawText(paint, text, startX, cy);

        // 绘制数值
        paint.setColor(valueColor);
        canvas.drawText(paint, value, startX + textWidth + 10, cy); // 在文本后面添加10px间隔然后绘制数值

        return totalWidth;
    }


    public void setShowSimplePage(boolean showSimplePage) {
        this.showSimplePage = showSimplePage;
    }
}