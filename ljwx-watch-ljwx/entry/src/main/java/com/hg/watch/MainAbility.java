package com.hg.watch;

import com.hg.watch.slice.MainAbilitySlice;
import ohos.agp.window.dialog.ToastDialog;
import ohos.aafwk.ability.Ability;
import ohos.aafwk.content.Intent;
import static com.hg.watch.slice.MainAbilitySlice.MY_PERMISSIONS_REQUEST_LOCATION;
import ohos.bundle.IBundleManager;
import ohos.hiviewdfx.HiLog;
import ohos.hiviewdfx.HiLogLabel;

public class MainAbility extends Ability {
    private MainAbilitySlice mainAbilitySlice;

    private static final HiLogLabel LABEL_LOG = new HiLogLabel(3, 0xD001100, "ljwx-log");
    @Override
    public void onStart(Intent intent) {
        super.onStart(intent);
        //super.setMainRoute(btAbilitySlice.class.getName());
        super.setMainRoute(MainAbilitySlice.class.getName());

    }

    @Override
    public void onRequestPermissionsFromUserResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsFromUserResult(requestCode, permissions, grantResults);
        HiLog.info(LABEL_LOG, "requestCode:" + requestCode);
        switch (requestCode) {
            case MY_PERMISSIONS_REQUEST_LOCATION: {
                // 匹配requestPermissions的requestCode
                if (grantResults.length > 0
                        && grantResults[0] == IBundleManager.PERMISSION_GRANTED) {
                    HiLog.info(LABEL_LOG, "mainAbilitySlice.runBluetooth():" + mainAbilitySlice.getAppType());
                    // 权限被授予之后做相应业务逻辑的处理
                    mainAbilitySlice.runBluetooth();

                } else {
                    // 权限被拒绝
                    new ToastDialog(getContext()).setText("权限被拒绝").show();
                }
                return;
            }
        }
    }
    public MainAbilitySlice getMainAbilitySlice() {
        return mainAbilitySlice;
    }

    public void setMainAbilitySlice(MainAbilitySlice mainAbilitySlice) {
        this.mainAbilitySlice = mainAbilitySlice;
    }


}
