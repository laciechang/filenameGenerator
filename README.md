# 文件名生成器 - Filename Generator

## 功能
在「交付」页面中根据项目设置、渲染设置等信息自动提取各类规格并给予输出文件命名

## 特性
- 启动时即可自动获取，随后可根据特定需求修改、填写已列出的各项，并实时预览
- 个别情况下可进行自定义排序，以及删除/恢复某项

## 安装
请将 *filenameGenerator.py* 拷贝至达芬奇指定的脚本存放目录下
macOS: /Users/{你的用户名}/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Deliver
Windows: C:\Users{你的用户名}\AppData\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Deliver
请使用v18及以上版本
在菜单：工作区(Workspace) > 脚本(Scripts) 中即可找到
仅支持在达芬奇内使用，不支持在外部运行

## TIPS
- 「片名」默认为项目名称
- 「音频通道」达芬奇目前实在没太有办法获取是立体声还是5.1之类，所以只有默认最常见的立体声STEREO了（声音采样率位深都给了就是不给Bus也是无奈了）
- 「字幕类型」这里达芬奇就没法告诉工具你的语言了，需要的话就只得手动填写
- 「画面比例」参考「遮幅」设置，区别于文件的「分辨率」
- 「内容版本」可以参考IMF的命名习惯，使用OV（Original Version）VF1（Version File）来帮助你识别不同版本的文件，咱就别写「最终版」这类看不懂前后关系的写法啦
- 「色彩空间」参考了「输出色彩空间」「ACES ODT」等设置