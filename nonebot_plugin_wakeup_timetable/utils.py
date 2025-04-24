from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import delete, select
from nonebot_plugin_orm import get_session
from .models import WakeUpCourse, WakeUpUser
from .config import Config
from nonebot import get_plugin_config, logger
from nonebot.matcher import Matcher
from nonebot_plugin_alconna import UniMessage
from nonebot_plugin_htmlrender import md_to_pic
from sqlalchemy.orm import selectinload


_cfg = get_plugin_config(Config)


async def query_user_by_uid(user_id: str) -> WakeUpUser:
    """从数据库获取用户信息，不含课程"""
    async with get_session() as session:
        result = await session.execute(
            select(WakeUpUser)
            .options(selectinload(WakeUpUser.courses))
            .where(WakeUpUser.user_id == user_id)
        )
        user: Optional[WakeUpUser] = result.scalar_one_or_none()
        if not user:
            logger.warning(f"用户 {user_id} 不存在")
            raise ValueError("用户信息不存在于数据库中")
        logger.debug(f"获取用户成功：{user.user_id}")
        return user


async def check_user_in_table(user_id: str) -> bool:
    """检查当前uid是否在数据库中"""
    async with get_session() as session:
        query = select(WakeUpUser).where(WakeUpUser.user_id == user_id)

        result = await session.execute(query)
        row = result.fetchone()
    if row is None:
        logger.debug("不存在该用户")
    return row is not None


async def send_table(matcher: Matcher, md: str):
    """根据配置发送图片或纯文本"""
    if _cfg.timetable_pic:
        pic = await md_to_pic(md)
        return await UniMessage.image(raw=pic).send()
    return await matcher.send(md)


async def get_current_week(user_id: str) -> int:
    """计算当前周数"""
    async with get_session() as session:
        usr = await session.get(WakeUpUser, user_id)
    if not usr or not usr.term_start:
        return 1
    delta = datetime.now().date() - usr.term_start.date()
    return max(1, delta.days // 7 + 1)


def get_next_weekday_date(target_weekday: int) -> datetime:
    """获取从今天开始的下一个指定 weekday的日期"""
    today = datetime.now()
    today_weekday = today.isoweekday()
    delta_days = (target_weekday - today_weekday + 7) % 7
    next_day = today + timedelta(days=delta_days)
    return next_day.replace(hour=0, minute=0, second=0, microsecond=0)

def filter_courses_by_week(courses: List[WakeUpCourse], week: int) -> List[WakeUpCourse]:
    """根据周数和单双周过滤课程"""
    return [
        c for c in courses
        if is_in_week(c.week_range, week)
        and match_week_type(c.week_type, week)
    ]

def is_in_week(week_range: str, current_week: int) -> bool:
    """检查当前周是否在指定的周范围内"""
    try:
        start, end = map(int, week_range.split("-"))

        return start <= current_week <= end
    except ValueError:
        return False


def match_week_type(week_type: int, current_week: int) -> bool:
    """检查当前周是否符合指定的周类型"""
    if week_type == 0:
        return True
    elif week_type == 1:
        return current_week % 2 == 1
    elif week_type == 2:
        return current_week % 2 == 0
    return False
