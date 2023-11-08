# This code is licensed under the MIT License.
# Please see the LICENSE file in the root of the repository for the full license text.
# Copyright (c) 2023 Konvt

import os
import sys
import logging
import hashlib
import subprocess
import urllib.request

VERSION = 'v-0.0.1'

FMT = { 'BOLD': '\033[1m' }
COL = {
    'RED': '\033[31m', 'GRE': '\033[32m', 'YEL': '\033[33m',
    'BLUE': '\033[34m', 'PURP': '\033[35m', 'CYAN': '\033[36m',
    'RESET': '\033[0m'
}

HIDE_OPT = '--enable-cli'
PROMPT = f'{COL['CYAN']}{FMT['BOLD']}  __  __ _                            __ _   \n' \
          ' |  \\/  (_)                          / _| |  \n'     \
          ' | \\  / |_ _ __   ___  ___ _ __ __ _| |_| |_ \n'     \
          ' | |\\/| | | \'_ \\ / _ \\/ __| \'__/ _` |  _| __|\n' \
          ' | |  | | | | | |  __/ (__| | | (_| | | | |_ \n'      \
          ' |_|  |_|_|_| |_|\\___|\\___|_|  \\__,_|_|  \\__|\n'  \
          f'                                             {COL['RESET']}'

jdk_version = '17'
file_suffix = '.exe'
FILENAME = f'jdk-{jdk_version}_windows-x64_bin{file_suffix}'
jdk_checksum = '4d1d6ec3976fd20bcc34db8fd7cfbe1a8cdd93a0c33182af13b31cd1feef423d'
download_url = f'https://download.oracle.com/java/{jdk_version}/latest/{FILENAME}'

# 遇上意料之外的异常时生成一个日志文件
def exception_logger(exception: Exception, context_mes: str) -> None:
    '''
    遇上异常时生成一个日志文件，通常是 url 连接错误或是其他问题

    exception: 需要输出的异常

    context_mes: 异常抛出位置的上下文环境简述
    '''
    logging.basicConfig(
        filename=os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'logfile.log'
        ),
        level=logging.ERROR,
        format='%(asctime)s: %(levelname)s',
        encoding='utf-8'
    )
    logging.exception(exception)
    error_to_terminal(
        f'An error occurred when {context_mes}.\n'
        f'{COL['YEL']}The log file has been generated.'
    )

# 将非异常的错误信息丢到终端中
def error_to_terminal(message: str, quit_flag: bool = True) -> None:
    '''
    将非异常的错误信息输出到终端

    `message`: 错误信息

    `quit_flag`: 这个错误是否会导致程序终止
    '''
    print(f'{COL['RED']}{message}{COL['RESET']}') # 默认染色为红色
    if quit_flag:
        os.system("pause")
        sys.exit(1) # quit the program

# 向命令行请求一个交互选项结果
def request_condition(request_mes: str, true_mes: str, false_mes: str, quit_flag: bool = True) -> bool:
    '''
    向命令行请求一个交互选项 [y/n]

    `request_mes`: 请求交互时需要输出的提示

    `true_mes`: 得到 y 答复时反馈的信息

    `false_mes`: 得到 n 答复时反馈的信息

    `quit_flag`: 得到 n 答复时是否终止程序
    '''
    condition_str = ''
    while len(condition_str) == 0 or condition_str[0] != 'y' or condition_str[0] != 'n':
        condition_str = input(f'{COL['CYAN']}{request_mes} [y/n]{COL['RESET']}\n>>> ').lower()
        if condition_str[0] == 'n':
            if quit_flag:
                error_to_terminal(f'Quitting due to {false_mes}.')
            elif len(false_mes) > 0:
                print(f'{COL['YEL']}{false_mes}.{COL['RESET']}')
            return False
        elif condition_str[0] == 'y':
            print(true_mes)
            return True

######################################## 以上是 Helper function ########################################

# 通过命令行调用已下载的文件
def install_package(package_name: str, silent_install: bool, path: str = '.') -> None:
    package_name = os.path.join(path, package_name)
    if silent_install:
        print(f'{COL['GRE']}JDK is installing, please wait...{COL['RESET']}')
        try: # 静默安装时使用默认选项
            subprocess.run(fr'{package_name} /s', shell=True, check=True)
            print(f'{COL['GRE']}Installation success.{COL['RESET']}')
        except Exception as e:
            exception_logger(e, 'installing target package')
    else:
        print(f'{COL['GRE']}Check the GUI that is displayed.{COL['RESET']}')
        try:
            subprocess.run(fr'{package_name}', shell=True)
            print(f'{COL['GRE']}Installation done.{COL['RESET']}')
        except Exception as e:
            exception_logger(e, 'installing target package')

# 检查文件是否存在
def check_file_exist(filename: str, path: str = '.') -> bool:
    for file in os.listdir(path):
        if file == filename:
            return True
    return False

# 尝试下载文件
def download_file(url: str, filename: None | str = None, path: str = '.') -> None:
    if filename is None:
        filename = url.split('/')[-1]  # 从 URL 中提取文件名
    filename = os.path.join(path, filename)
    try:
        urllib.request.urlretrieve(url, filename)
        print(f'{COL['GRE']}The file "{filename}" was successfully downloaded.{COL['RESET']}')
    except Exception as e:
        exception_logger(e, f'downloading file "{filename}"')

# 计算文件的 SHA-256 以校验文件完整性
def check_file_integrity(filename: str, checksum: str, path: str = '.') -> bool:
    filename = os.path.join(path, filename)
    try:
        sha256_hash = hashlib.sha256()
        with open(filename, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256_hash.update(chunk)

        return sha256_hash.hexdigest() == checksum
    except Exception as e:
        exception_logger(e, f'checking the intergirty of the file "{filename}"')
        return False # 该语句正常来说不会被执行

def welcome(cli_arg: bool) -> None:
    global PROMPT
    print(PROMPT)
    print(
        f'{COL['CYAN']}Welcome to {FMT['BOLD']}{COL['YEL']}>>> {COL['PURP']}Nether Portal {COL['YEL']}<<<{COL['RESET']}\n'
        f'[version: {VERSION}]\n'
    )
    if VERSION.find('beta') == -1:
        print(
            f'This is a open source program that helps {COL['GRE']}{FMT['BOLD']}Minecraft players{COL['RESET']} '
            'install the JDK environment with one click.\n'
        )
    else:
        print('This is a beta version.')

    global jdk_version
    global file_suffix
    print(f'The installation file will be: "{COL['YEL']}jdk-{jdk_version}{file_suffix}{COL['RESET']}".')

    if not cli_arg:
        cmd_str = input(f'Input {COL['YEL']}"Enter"{COL['RESET']} to continue...\n').lower()
        if cmd_str.find(HIDE_OPT) != -1:
            cli_arg = True

    if cli_arg: # 上面重设过 cli_arg，这里不能使用 else
        print(f'{COL['GRE']}Enable custom options.{COL['RESET']}')

        custom_jdk = input(
            f'{COL['CYAN']}What version of JDK do you want to install?\n'
            f'{FMT['BOLD']}{COL['YEL']}(number only){COL['RESET']} >>> '
        )
        custom_file = f'.{input(
            f'{COL['CYAN']}Input the suffix for the installation file:\n'
            f'{FMT['BOLD']}{COL['YEL']}(excluding the dot){COL['RESET']} >>> '
        )}'
        if custom_jdk != jdk_version or custom_file != file_suffix:
            jdk_version = custom_jdk
            file_suffix = custom_file

            global jdk_checksum
            jdk_checksum = input(f'{COL['CYAN']}Input the SHA-256 value of the JDK installation file:\n{COL['RESET']}')

        if request_condition(
            'Do you want to set the download url?',
            'Input the download url:\n >>> ',
            '',
            quit_flag=False
        ):
            global download_url
            download_url = input()

        print(
            f'{COL['GRE']}Now the installation file is "jdk-{jdk_version}{file_suffix}".\n'
            f'SHA-256 = {jdk_checksum}\n{COL['RESET']}'
        )

if __name__ == "__main__":
    os.chdir(os.path.dirname(sys.argv[0])) # 将工作目录切换回程序所在目录

    welcome(any(HIDE_OPT in arg for arg in sys.argv))

    # 检查本地是否已有同名文件
    if not check_file_exist(FILENAME):
        error_to_terminal(f'File "{FILENAME}" not found!', False)
        request_condition(
            'Do you want to download it now?',
            f'Downloading the file "{FILENAME}", please wait...',
            'refuse to download'
        )
        download_file(download_url, FILENAME)
    else:
        print(f'File "{FILENAME}" found.')

    # 检查文件的 SHA-256 是否与给定的一致
    while not check_file_integrity(FILENAME, jdk_checksum):
        error_to_terminal(f'Incomplete file: "{FILENAME}".', False)
        request_condition(
            'Do you want to download it again?',
            f'Re-downloading the file "{FILENAME}", please wait...',
            f'incomplete file "{FILENAME}"'
        )
        download_file(download_url, FILENAME)
    print(f'File "{FILENAME}" integrity confirmed.')

    # 使用命令行安装文件
    if file_suffix == '.exe':
        install_package(
            FILENAME,
            request_condition(
            'Do you want to install JDK silently?',
            'The installation will be automatically and silently.',
            'An GUI installer will be displayed soon.',
            quit_flag=False
            )
        )
    else: # 测试 msi 命令行安装时始终失败，故暂不支持
        install_package(FILENAME, False)

    if request_condition(
        f'Do you want to remove the file "{FILENAME}"?',
        f'File "{FILENAME}" has been removed',
        'Everything done',
        quit_flag=False
    ):
        os.remove(FILENAME)
        print(f'{COL['YEL']}Everything done.{COL["RESET"]}')
    os.system('pause')
