import json
import re
from typing import Optional, List, Dict, Tuple
import httpx
from datetime import datetime, timedelta
from nonebot.log import logger
from sqlalchemy import delete, select
from nonebot_plugin_orm import get_session
from .models import WakeUpCourse, WakeUpUser

# 服务配置与常量
__URL__ = "https://i.wakeup.fun/share_schedule/get"
__HEADER__ = {
    'Connection': 'keep-alive',
    'Accept-Encoding': 'gzip',
    'User-Agent': 'okhttp/4.12.0',
    'Content-Type': 'application/json',
    'version': '248',
    'Host': 'i.wakeup.fun'
}


async def extract_share_key(text: str) -> Optional[str]:
    """提取分享口令"""
    if match := re.search(r"口令为「(.*?)」", text):
        return match.group(1)
    return None


async def update_table_by_share_link(user_id: str, text: str):
    """通过分享链接导入课程表的统一入口"""
    share_key = await extract_share_key(text)
    if not share_key:
        raise ValueError("分享链接格式错误，未找到有效口令")
    data = await fetch_schedule(share_key, user_id)
    courses = await parse_data(data, user_id)
    term = await parse_start_term(data)
    await import_courses(user_id, term, courses)


async def fetch_schedule(share_key: str, user_id: str) -> str:
    """从 WakeUp 接口拉取原始课程表数据"""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(__URL__, params={"key": share_key}, headers=__HEADER__)

        # HTTP状态码检查
        if resp.status_code != 200:
            raise ValueError(f"接口请求失败: HTTP {resp.status_code}")

        payload = resp.json()
        # logger.debug(f"原始API响应：{payload}")  # 添加调试日志

        # 修正状态检查逻辑
        if payload.get("status") not in (1, "1", 200):
            raise ValueError(f"接口返回错误: {payload.get('message', '未知错误')}")

        data = payload.get("data")
        # 验证数据完整性
        if not data:
            raise ValueError("接口未返回 data 字段")
        return data

    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"fetch_schedule 解析失败: {e}")
        raise ValueError("无效的接口响应格式")

    except Exception as e:
        logger.error(f"fetch_schedule 异常: {e}")
        raise


async def parse_start_term(raw: str) -> datetime:
    """解析学期开始日期"""
    lines = raw.strip().splitlines()
    term_info = json.loads(lines[2])
    return datetime.strptime(term_info["startDate"], "%Y-%m-%d")


async def parse_data(raw: str, user_id: str) -> List[WakeUpCourse]:
    """解析详细课程数据"""
    courses: List[WakeUpCourse] = []
    lines = raw.strip().splitlines()

    try:
        # 解析各部分数据
        time_table = json.loads(lines[1])
        term_info = json.loads(lines[2])
        course_infos = json.loads(lines[3])
        details = json.loads(lines[4])
        # 处理学期开始日期
        term_start = datetime.strptime(term_info["startDate"], "%Y-%m-%d")
        # 建立课程信息映射
        info_map = {c["id"]: c for c in course_infos}

        # 处理每个课程详情
        for d in details:
            # 获取关联的课程信息
            info = info_map.get(d["id"])
            if not info:
                continue
            # 解析时间段
            time_range = _parse_time(d, time_table)
            # 构建课程对象
            course = WakeUpCourse(
                user_id=user_id,
                course_name=info.get("courseName", "未命名课程"),
                weekday=d.get("day", 0),
                time_range=time_range,
                location=d.get("room", "未指定教室"),
                teacher=d.get("teacher", "未指定教师"),
                week_type=d.get("type", 0),
                start_date=term_start +
                timedelta(weeks=d["startWeek"] - 1, days=d["day"] - 1),
                end_date=term_start +
                timedelta(weeks=d["endWeek"] - 1, days=d["day"] - 1),
                week_range=f"{d['startWeek']}-{d['endWeek']}"
            )
            courses.append(course)

    except json.JSONDecodeError as e:
        logger.error(f"JSON解析失败: {str(e)}")

    except Exception as e:
        logger.error(f"parse_data 异常: {e}")
    return courses


def _parse_time(detail: Dict, table: List[Dict]) -> str:
    try:
        start, length = detail['startNode'], detail['step']
        # 查找对应时间段
        slots = [s for s in table if start <= s['node'] < start + length]
        return f"{slots[0]['startTime']}-{slots[-1]['endTime']}" if slots else "未知时段"
    except Exception:
        return "时间解析失败"


async def import_courses(user_id: str, term_start: datetime, courses: List[WakeUpCourse]):
    """将课程与用户绑定并存入数据库"""
    async with get_session() as session:
        try:
            # 清理旧数据
            await session.execute(delete(WakeUpCourse).where(WakeUpCourse.user_id == user_id))
            # 直接添加课程对象
            session.add_all(courses)

            # 更新用户信息
            user = await session.get(WakeUpUser, user_id)
            now = datetime.now()
            if not user:
                user = WakeUpUser(
                    user_id=user_id, term_start=term_start, update_time=now)
                session.add(user)
            else:
                user.term_start = term_start
                user.update_time = now

            await session.commit()
            logger.info(f"用户{user_id}课程导入成功，共{len(courses)}条")
        except Exception as e:
            logger.error(f"课程导入异常: {e}")
