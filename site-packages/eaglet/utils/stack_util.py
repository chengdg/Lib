# coding=utf8
# 获取堆栈信息的工具

import os
import traceback

def get_trace_back():
	stack_entries = traceback.extract_stack()
	stack_entries = filter(lambda entry: ('eaglet' in entry[0] or ((not 'python' in entry[0].lower()) and (not 'cache%sutils' % os.path.sep in entry[0]))), stack_entries)
	buf = []
	for stack_entry in stack_entries:
		filename, line, function_name, text = stack_entry
		if 'eaglet' in filename:
			color = 'black'
		else:
			color = 'red'
		formated_stack_entry = "<span style=color:%s>File `%s`, line %s, in %s</span><br/><span>&nbsp;&nbsp;&nbsp;&nbsp;%s</span>" % (color, filename, line, function_name, text)
		buf.append(formated_stack_entry)
	stack = '<br/>'.join(buf).replace("\\", '/').replace('"', "``").replace("'", '`')
	return stack