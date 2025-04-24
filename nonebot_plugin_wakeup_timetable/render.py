from datetime import datetime, timedelta
import re
from typing import List
from nonebot.matcher import Matcher
from .utils import (
    filter_courses_by_week,
    get_current_week,
    get_next_weekday_date,
    query_user_by_uid
)
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from nonebot_plugin_orm import get_session
from nonebot import logger, require
from .models import WakeUpCourse, WakeUpUser


__day_pattern__ = r"((星期|周)[一二三四五六日天1234567]|(今|明|后)(天|日))"


async def query_and_format_table(user_id: str, keyword: str) -> str:
    """统一查询课表并返回渲染后的 Markdown 表格"""
    courses = await query_courses(user_id, keyword)
    if not courses:
        raise ValueError("未找到匹配的课程")
    return await build_table(courses)


async def query_courses(uid: str, keyword: str) -> list:
    """查询并过滤课程列表"""
    keyword = keyword.strip()
    user = await query_user_by_uid(uid)
    courses = user.courses
    if not courses:
        logger.info(f"用户 {uid} 无课程数据")
        return []

    week = await get_current_week(uid)
    logger.debug(f"当前周为第 {week} 周，共有 {len(courses)} 门课")

    if re.match(__day_pattern__, keyword):
        weekday = parse_weekday(keyword)
        if weekday > 7:
            weekday %= 7
            week += 1

        date = get_next_weekday_date(weekday)
        return [
            c for c in filter_courses_by_week(courses, week)
            if c.weekday == weekday and
            c.start_date <= date <= c.end_date
        ]

    elif keyword == "本周":
        return filter_courses_by_week(courses, week)

    elif keyword == "下周":
        return filter_courses_by_week(courses, week+1)

    # 待开发功能
    # elif keyword == "下节课":
    # elif keyword == "早八":

    else:
        courses = filter_courses_by_week(courses, week)
        return [
            c for c in courses if keyword in c.course_name
        ]


async def build_table(courses: list) -> str:
    """将课程列表格式化为 Markdown 表格"""
    header = "|星期|时间|课程|地点|老师|\n| :----:| :----:| :----: | :----: | :----:|\n"
    rows = []
    by_day = {}
    for c in courses:
        by_day.setdefault(c.weekday, []).append(c)

    for day in sorted(by_day):
        for c in sorted(by_day[day], key=lambda x: x.time_range):
            rows.append(
                f"|{c.weekday}|{c.time_range}|{c.course_name}|{c.location}|{c.teacher}|")

    return header + "\n".join(rows)


def parse_weekday(text: str) -> int:
    """解析中文或数字星期"""
    weekday_map = {
        "一": 1, "1": 1,
        "二": 2, "2": 2,
        "三": 3, "3": 3,
        "四": 4, "4": 4,
        "五": 5, "5": 5,
        "六": 6, "6": 6,
        "日": 7, "天": 7, "7": 7,
        "今": datetime.now().isoweekday(),
        "明": datetime.now().isoweekday() + 1,
        "后": datetime.now().isoweekday() + 2,
    }
    for char in text:
        if char in weekday_map:
            return weekday_map[char]
    # 默认返回今天
    return datetime.now().isoweekday()
