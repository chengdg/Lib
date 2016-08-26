#coding=utf8

# 时间、日期计算的工具
# 参考自 com.wintim.common.util.DateUtil

import datetime as dt


DATETIME_FORMAT="%Y-%m-%d %H:%M:%S"
DATE_FORMAT="%Y-%m-%d"


# 获得当前的时刻的字符串
def get_current_datetime():
	return dt.datetime.now().strftime(DATETIME_FORMAT)

def now():
	return dt.datetime.now()

# 获得当前日期
def get_current_date():
	return dt.datetime.now().strftime(DATE_FORMAT)

# 将Date转成"yyyy-MM-dd HH:mm:ss"字符串
def datetime2string(at):
	if at == None:
		return None
	return at.strftime(DATETIME_FORMAT)

# 将Date转成"yyyy-MM-dd"字符串
def date2string(at):
	if at == None:
		return None
	return at.strftime(DATE_FORMAT)

# 将"yyyy-MM-dd HH:mm:ss"字符串转成datetime
def parse_datetime(str):
	if str == None:
		return None
	return dt.datetime.strptime(str, DATETIME_FORMAT)

def parse_date(str):
	if str == None:
		return None
	return dt.datetime.strptime(str, DATE_FORMAT)

# 得到n天后的时间
def get_date_after_days(date, days):
	return date + dt.timedelta(days=days)

def cmp_datetime(a, b):
	a_datetime = dt.datetime.strptime(a, '%Y-%m-%d')
	b_datetime = dt.datetime.strptime(b, '%Y-%m-%d')

	if a_datetime > b_datetime:
		return -1
	elif a_datetime < b_datetime:
		return 1
	else:
		return 0