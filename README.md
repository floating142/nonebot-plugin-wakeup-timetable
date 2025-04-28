<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-wakeup-timetable

_✨ 基于 NoneBot2 的 wakeup 课程表插件 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/owner/nonebot-plugin-template.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-wakeup-timetable">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-template.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">

</div>

## 📖 介绍

一个简单的 NoneBot2 插件，基于 [wakeup 课程表](https://www.wakeup.fun/) 导入与查询课表

> [!NOTE]
> 本项目修改自 [nonebot-plugin-ai-timetable](https://github.com/maoxig/nonebot-plugin-ai-timetable)，
> 如果你对项目中部分代码的相似性有疑问，也请随时联系我

## 💿 安装


**使用 pip 安装**
  ```bash
  pip install nonebot-plugin-wakeup-timetable
  ```
  打开 nonebot2 项目根目录下的 pyproject.toml 文件, 在 plugins = [] 部分追加写入
  ```bash
  plugins = ["nonebot_plugin_wakeup_timetable"]
  ```


> [!WARNING]
> 第一次使用[plugin-orm](https://github.com/nonebot/plugin-orm)，或者插件定义的模型有所更新时，需要用`nb orm upgrade`升级数据库


## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

|         config          | type  | default |          example           | usage                                                                                                 |
| :---------------------: | :---: | :-----: | :------------------------: | :---------------------------------------------------------------------------------------------------- |
|      TIMETABLE_PIC      | bool  |  true   |    TIMETABLE_PIC=false     | 可选择某日课表以图片/文字发送，默认以图片发送(true)                                                          |

## 💿依赖

> [!NOTE]
> 插件依赖会在安装时自动安装，如果安装失败，你可以按照以下指令手动再次安装

```python
nb plugin install nonebot_plugin_htmlrender
nb plugin install nonebot_plugin_apscheduler
nb plugin install nonebot_plugin_alconna
nb plugin install nonebot_plugin_orm
```

## 🎉命令

 * 课表帮助：获取帮助

 * 导入课表：解析wakeup课程表分享的链接并导入数据库

 * 查询课表+[参数]：查询[参数]的课表，参数支持[本周/下周、周x、今天/明天/后天、课程名]
  
 ## 📝 TODO

  * [ ] 增加早八，下节课的查询
  * [ ] 实现课程提醒
  * [ ] 优化代码
  * [ ] 在群聊中查看群友课程
        
 ## 🙏 致谢

 * [nonebot-plugin-ai-timetable](https://github.com/maoxig/nonebot-plugin-ai-timetable) - 提供源码及思路~~其实是完全照搬(bushi~~

 * [curriculum-table](https://github.com/shangxueink/koishi-shangxue-apps/tree/main/plugins/curriculum-table) - 提供灵感

 * [nonebot2](https://github.com/nonebot/nonebot2) - 插件开发框架
    
 * [wakeup 课程表](https://www.wakeup.fun/) - 提供课程表及api

 ## 📬 贡献
 
这是我第一次尝试写 NoneBot2 的插件，很多地方写得不够好，欢迎大家指出问题！

如果你发现 Bug、有功能建议、或者想一起完善插件，欢迎提交 Issue 或 PR～


 ## 📄 开源许可

本项目使用 [MIT License](https://www.google.com/search?q=LICENSE) 开源。
