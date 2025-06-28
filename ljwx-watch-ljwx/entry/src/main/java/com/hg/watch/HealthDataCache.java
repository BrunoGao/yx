package com.hg.watch;

import ohos.app.Context;
import ohos.data.DatabaseHelper;
import ohos.hiviewdfx.HiLog;
import ohos.hiviewdfx.HiLogLabel;
import ohos.data.preferences.Preferences;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.ArrayList;
import java.util.List;
import com.hg.watch.utils.DataManager;



public class HealthDataCache{
    private static final HiLogLabel LABEL_LOG = new HiLogLabel(HiLog.LOG_APP, 0x01100, "ljwx-log");
    private static HealthDataCache instance;
    private BlockingQueue<String> cacheQueue;
    private DataManager dataManager = DataManager.getInstance();
    private static final String CACHE_KEY = "health_data_cache";
    private static Preferences preferences;
    private static Context sContext;
    private static final int MAX_CACHE_SIZE = 100;  // 最大缓存条数

    private HealthDataCache() {
        dataManager = DataManager.getInstance();
        int maxSize = Math.min(dataManager.getCacheMaxCount(), MAX_CACHE_SIZE);
        cacheQueue = new ArrayBlockingQueue<>(maxSize);
        loadCache();
    }
       /**
     * 在 Ability 或 Service 启动时，先调用一次 init()，传入它的 Context
     */
    public static void init(Context ctx) {
        // 用 getApplicationContext() 保证不会误持有某个 Ability 的短生命周期 Context
        sContext = ctx.getApplicationContext();
    }

    public static synchronized HealthDataCache getInstance() {
        if (instance == null) {
            instance = new HealthDataCache();
        }
        return instance;
    }

    public void addToCache(String healthData) {
        try {
            if (cacheQueue.size() >= dataManager.getCacheMaxCount()) {
                String oldestData = cacheQueue.poll(); // 移除最旧的数据
                HiLog.info(LABEL_LOG, "HealthDataCache::addToCache 移除最旧数据: " + oldestData);
            }
            boolean added = cacheQueue.offer(healthData);
            if (added) {
                HiLog.info(LABEL_LOG, "HealthDataCache::addToCache 添加新数据成功，当前缓存大小: " + cacheQueue.size());
                saveCache();
            } else {
                HiLog.error(LABEL_LOG, "HealthDataCache::addToCache 添加新数据失败，队列已满");
            }
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "HealthDataCache::addToCache error: " + e.getMessage());
        }
    }

    public List<String> getAllCachedData() {
        List<String> result = new ArrayList<>();
        // 使用peek而不是drainTo，这样不会清空队列```````
        for (String data : cacheQueue) {
            result.add(data);
        }
        HiLog.info(LABEL_LOG, "HealthDataCache::getAllCachedData 获取缓存数据: " + result.size() + "条");
        return result;
    }

    public void clearCache() {
        HiLog.info(LABEL_LOG, "HealthDataCache::clearCache 清空缓存，原大小: " + cacheQueue.size());
        cacheQueue.clear();
        saveCache();
    }
    private static Preferences getPreferences() {
        if (preferences == null) {
            // 这里拿到的就是你在 init() 里传进来的 Context
            DatabaseHelper databaseHelper = new DatabaseHelper(sContext);
            String fileName = "pref";
            preferences = databaseHelper.getPreferences(fileName);
        }
        return preferences;
    }
    public static void storeValue(String key, String value) {
        Preferences prefs = getPreferences();
        prefs.putString(key, value);
        prefs.flush();
    }

    public static String fetchValue(String key, String defaultVal) {
        Preferences prefs = getPreferences();
        String v = prefs.getString(key, defaultVal);
        return v != null ? v : defaultVal;
    }
    private void saveCache() {
        try {
            List<String> cacheList = new ArrayList<>(cacheQueue);
            if(cacheList.isEmpty()){
                // 清空所有缓存键
                for(int i=0;i<10;i++){
                    storeValue(CACHE_KEY+"_"+i,"");
                }
                HiLog.info(LABEL_LOG, "HealthDataCache::saveCache 清空缓存");
                return;
            }
            
            // 分片存储，每片最大7000字符(留余量)
            final int MAX_CHUNK_SIZE=7000;
            String fullCacheStr=String.join("|",cacheList);
            int totalLen=fullCacheStr.length();
            
            if(totalLen<=MAX_CHUNK_SIZE){
                // 单片存储
                storeValue(CACHE_KEY,fullCacheStr);
                // 清空其他片
                for(int i=1;i<10;i++){
                    storeValue(CACHE_KEY+"_"+i,"");
                }
                HiLog.info(LABEL_LOG,"HealthDataCache::saveCache 单片存储,大小:"+totalLen);
            }else{
                // 多片存储
                int chunkCount=(totalLen+MAX_CHUNK_SIZE-1)/MAX_CHUNK_SIZE;
                for(int i=0;i<chunkCount&&i<10;i++){
                    int start=i*MAX_CHUNK_SIZE;
                    int end=Math.min(start+MAX_CHUNK_SIZE,totalLen);
                    String chunk=fullCacheStr.substring(start,end);
                    storeValue(CACHE_KEY+(i==0?"":"_"+i),chunk);
                }
                // 清空未使用的片
                for(int i=chunkCount;i<10;i++){
                    storeValue(CACHE_KEY+(i==0?"":"_"+i),"");
                }
                HiLog.info(LABEL_LOG,"HealthDataCache::saveCache 多片存储,片数:"+chunkCount+",总大小:"+totalLen);
            }
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "HealthDataCache::saveCache error: " + e.getMessage());
        }
    }

    private void loadCache() {
        try {
            // 尝试多片加载
            StringBuilder fullCacheStr=new StringBuilder();
            for(int i=0;i<10;i++){
                String chunk=fetchValue(CACHE_KEY+(i==0?"":"_"+i),"");
                if(!chunk.isEmpty()){
                    fullCacheStr.append(chunk);
                }else if(i>0){
                    break; // 遇到空片且不是第一片，停止加载
                }
            }
            
            String cachedData=fullCacheStr.toString();
            if(!cachedData.isEmpty()){
                String[]items=cachedData.split("\\|");
                int loadedCount=0;
                for(String item:items){
                    if(!item.isEmpty()){
                        boolean added=cacheQueue.offer(item);
                        if(!added){
                            HiLog.warn(LABEL_LOG,"HealthDataCache::loadCache 缓存已满，无法加载更多数据");
                            break;
                        }
                        loadedCount++;
                    }
                }
                HiLog.info(LABEL_LOG,"HealthDataCache::loadCache 加载缓存成功，大小:"+loadedCount+",总字符数:"+cachedData.length());
            }
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "HealthDataCache::loadCache error: " + e.getMessage());
        }
    }
} 