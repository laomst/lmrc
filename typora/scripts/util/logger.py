from datetime import datetime

# log_strategy = 'file'
log_strategy = 'console'
# log_strategy = 'disable'

def write_log(msg):
    if log_strategy == 'file':
        _write_file_log(msg)
    elif log_strategy == 'console':
        _write_console_log(msg)

def reset_log():
    if log_strategy == 'file':
        _reset_file_log()

def _write_file_log(msg):
    # 打开文件，指定写入模式 'w'
    with open('/Users/laomst/__code_workspace__/__Laomst/laomst-typora-ext/log.txt', 'a') as file:
        # 写入多行内容
        # 获取当前时间
        current_time = datetime.now()

        # 格式化为字符串
        formatted_time = current_time.strftime("%Y/%m/%d %H:%M:%S")
        file.write('\n' + formatted_time + '\n')
        file.writelines([msg])

def _write_console_log(msg):
    print(msg)

def _reset_file_log():
    # 打开文件，指定写入模式 'w'
    with open('/Users/laomst/__code_workspace__/__Laomst/laomst-typora-ext/log.txt', 'w') as file:
        # 写入多行内容
        # 获取当前时间
        current_time = datetime.now()

        # 格式化为字符串
        formatted_time = current_time.strftime("%Y/%m/%d %H:%M:%S")
        file.write('\n' + formatted_time + '\n')
