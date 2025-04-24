from nonebot import logger, require
require("nonebot_plugin_alconna")
require("nonebot_plugin_orm")
require("nonebot_plugin_apscheduler")
require("nonebot_plugin_htmlrender")
from .render import query_and_format_table
from .get import update_table_by_share_link
from .utils import send_table, check_user_in_table
from .config import Config
from nonebot.plugin import PluginMetadata, on_command, inherit_supported_adapters
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, ArgPlainText
from nonebot.adapters import Message, Event
from nonebot.exception import FinishedException


__wakeup_timetable__usage__ = '''## wakeup课表帮助:
- 课表帮助: 获取本条帮助
- 导入课表: 使用wakeup课程表分享的链接一键导入
- 查询课表+[参数]: 查询[参数]的课表，参数支持[本周/下周、周x、今天/明天/后天、课程名]
'''

__plugin_meta__ = PluginMetadata(
    name="WakeUp课程表",
    description="基于WakeUp课程表API的课表管理系统",
    homepage="https://github.com/floating142/nonebot-plugin-wakeup-timetable",
    usage=__wakeup_timetable__usage__,
    type="application",
    config=Config,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
)


# 命令注册
help_cmd = on_command("课表帮助", aliases={"课表介绍"}, priority=20)
import_cmd = on_command("导入课表", aliases={"创建课表"}, priority=20)
query_cmd = on_command("课表查询", aliases={"查询课表"}, priority=20)


@help_cmd.handle()
async def _(matcher: Matcher):
    """处理课表帮助命令，根据配置发送课表帮助信息或图片"""
    await send_table(matcher, __wakeup_timetable__usage__)


@import_cmd.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    """接收 WakeUp 分享链接导入课程表"""
    msg = args.extract_plain_text().strip()
    if msg:
        matcher.set_arg("key", args)


@import_cmd.got("key", prompt="请发送 WakeUp 课程表分享链接，或发送 /取消 退出")
async def _(event: Event, matcher: Matcher, key: str = ArgPlainText()):
    uid = event.get_user_id()

    if key.strip() == "/取消":
        await matcher.finish("已取消导入课表操作")

    logger.debug(f"用户 {uid} 提供的导入链接：{key}")
    try:
        await update_table_by_share_link(uid, key)
        await matcher.finish("✅ 课程表导入成功！")
    except FinishedException:
        raise
    except Exception as e:
        logger.error(f"导入失败：{e}")
        await matcher.finish(f"❌ 导入失败：{e}")


@query_cmd.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    """接收查询参数并准备查询"""
    msg = args.extract_plain_text().strip()
    if msg:
        matcher.set_arg("key", args)


@query_cmd.got("key", prompt="请输入查询关键词，例如：周一 / 明天 / 高等数学")
async def _(event: Event, matcher: Matcher, key: str = ArgPlainText()):
    uid = event.get_user_id()
    if not await check_user_in_table(event.get_user_id()):
        await matcher.finish("你还没有导入课表，发送/导入课表来导入吧！")

    logger.debug(f"用户 {uid} 查询关键词：{key}")
    try:
        response = await query_and_format_table(uid, key)
        await send_table(matcher, response)

    except FinishedException:
        raise
    except Exception as e:
        logger.error(f"查询失败：{e}")
        await matcher.finish(f"❌ 查询失败：{e}")
