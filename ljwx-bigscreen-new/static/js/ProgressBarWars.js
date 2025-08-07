// 添加 scrollDown 函数
function scrollDown() {
    // 如果需要滚动功能，可以实现具体的滚动逻辑
    // 如果不需要，可以留空或移除相关调用
}

// 修改 init.Scroll 的调用
var init = {
    // ... 其他代码 ...
    Scroll: function() {
        // 移除对 scrollDown 的调用，改为更安全的实现
        return {
            wheel: function(e) {
                e.preventDefault();
                // 如果需要自定义滚动行为，在这里实现
            }
        };
    }
    // ... 其他代码 ...
}; 