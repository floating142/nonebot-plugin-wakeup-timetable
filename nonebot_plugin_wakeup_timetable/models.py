from datetime import datetime
from typing import List
from nonebot_plugin_orm import Model
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship


class WakeUpUser(Model):
    """WakeUp用户表"""
    __tablename__ = "wakeup_users"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    term_start: Mapped[datetime] = mapped_column(DateTime)  # 学期开始日期
    update_time: Mapped[datetime] = mapped_column(DateTime)  # 最后更新时间
    # 添加课程反向引用
    courses: Mapped[List["WakeUpCourse"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


class WakeUpCourse(Model):
    """WakeUp课程表"""
    __tablename__ = "wakeup_courses"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("wakeup_users.user_id", ondelete="CASCADE"),  # 外键绑定
        nullable=False
    )                                                        # 关联用户ID
    course_name: Mapped[str] = mapped_column(String(128))    # 课程名称
    weekday: Mapped[int] = mapped_column(Integer)            # 星期几（1-7）
    time_range: Mapped[str] = mapped_column(String(32))      # 时间范围
    location: Mapped[str] = mapped_column(String(128))       # 上课地点
    teacher: Mapped[str] = mapped_column(String(64))         # 授课教师
    start_date: Mapped[datetime] = mapped_column(DateTime)   # 开始日期
    end_date: Mapped[datetime] = mapped_column(DateTime)     # 结束日期
    week_type: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False)          # 单双周（0,1,2）
    week_range: Mapped[str] = mapped_column(String(20))      # 周次范围 1-20
    # 课程所属用户
    user: Mapped["WakeUpUser"] = relationship(
        back_populates="courses"
    )
