#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量编码转换工具
将GB2312/GBK编码的C/H文件转换为UTF-8 with BOM编码
适用于Keil和VS2010开发环境
"""

import os
import sys
import argparse
import shutil
from pathlib import Path

# 尝试导入chardet，如果没有则使用简单检测
try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False
    print("提示: 安装chardet库可提高编码检测准确性: pip install chardet")


def detect_encoding(filepath):
    """检测文件编码"""
    try:
        with open(filepath, 'rb') as f:
            raw_data = f.read()
            
        # 检查BOM标记
        if raw_data[:3] == b'\xef\xbb\xbf':
            return 'utf-8-sig'
        elif raw_data[:2] in (b'\xff\xfe', b'\xfe\xff'):
            return 'utf-16'
        
        # 使用chardet检测
        if HAS_CHARDET:
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            confidence = result['confidence']
            
            if encoding and confidence > 0.7:
                # 常见编码映射
                encoding_map = {
                    'gb2312': 'gb2312',
                    'gbk': 'gbk',
                    'gb18030': 'gb18030',
                    'ascii': 'ascii',
                    'utf-8': 'utf-8',
                    'windows-1252': 'windows-1252',
                    'iso-8859-1': 'iso-8859-1',
                }
                return encoding_map.get(encoding.lower(), encoding)
        
        # 简单检测：尝试用不同编码解码
        encodings_to_try = ['gb2312', 'gbk', 'utf-8', 'ascii', 'iso-8859-1']
        for enc in encodings_to_try:
            try:
                raw_data.decode(enc)
                return enc
            except (UnicodeDecodeError, LookupError):
                continue
        
        # 默认返回gb2312（中文Windows常见）
        return 'gb2312'
        
    except Exception as e:
        print(f"检测编码失败 {str(filepath)}: {e}")
        return 'gb2312'


def convert_file(filepath, target_encoding='utf-8-sig', backup=True, backup_dir=None, force=False, base_dir=None, dry_run=False):
    """转换单个文件编码"""
    try:
        # 检测原始编码
        source_encoding = detect_encoding(filepath)

        # 如果已经是目标编码，跳过
        if source_encoding == target_encoding and not force:
            return True, "已是目标编码"

        # 读取文件内容
        with open(filepath, 'rb') as f:
            raw_data = f.read()

        # 保留原始换行符
        newline = None
        if b'\r\n' in raw_data:
            newline = '\r\n'
        elif b'\r' in raw_data:
            newline = '\r'
        else:
            newline = '\n'

        content = raw_data.decode(source_encoding, errors='replace')

        if dry_run:
            return True, f"{source_encoding} -> {target_encoding} (dry-run)"

        # 备份原文件
        if backup:
            if backup_dir:
                # 备份到指定目录（保留原始目录结构）
                if base_dir:
                    rel_path = Path(filepath).relative_to(base_dir)
                else:
                    rel_path = Path(filepath).name
                backup_path = Path(backup_dir) / rel_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(filepath, backup_path)
            else:
                # 备份到原文件旁边
                backup_path = str(filepath) + '.bak'
                shutil.copy2(filepath, backup_path)

        # 写入新编码，保留原始换行符
        with open(filepath, 'w', encoding=target_encoding, newline=newline) as f:
            f.write(content)

        return True, f"{source_encoding} -> {target_encoding}"

    except Exception as e:
        return False, str(e)


def batch_convert(directory, extensions=('*.c', '*.h', '*.cpp', '*.hpp'),
                  target_encoding='utf-8-sig', backup=True, backup_dir=None, recursive=True, force=False, dry_run=False):
    """批量转换目录下的文件"""
    directory = Path(directory)
    
    if not directory.exists():
        print(f"错误: 目录不存在 - {directory}")
        return 0, 0
    
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    # 收集所有文件
    files = []
    for ext in extensions:
        if recursive:
            files.extend(directory.rglob(ext))
        else:
            files.extend(directory.glob(ext))
    
    if not files:
        print(f"未找到匹配的文件 (扩展名: {extensions})")
        return 0, 0
    
    print(f"找到 {len(files)} 个文件待处理")
    print(f"目标编码: {target_encoding}")
    print("-" * 50)
    
    for i, filepath in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {filepath.name}", end=" ... ")
        
        success, message = convert_file(filepath, target_encoding, backup, backup_dir, force, base_dir=directory, dry_run=dry_run)
        
        if success:
            if "已是目标编码" in message:
                print(f"跳过 ({message})")
                skip_count += 1
            else:
                print(f"成功 ({message})")
                success_count += 1
        else:
            print(f"失败 ({message})")
            fail_count += 1
    
    print("-" * 50)
    print(f"转换完成: 成功 {success_count}, 跳过 {skip_count}, 失败 {fail_count}")
    
    return success_count, fail_count


def main():
    parser = argparse.ArgumentParser(
        description='批量编码转换工具 - 将C/H文件转换为UTF-8编码',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s .                          # 转换当前目录
  %(prog)s /path/to/project           # 转换指定目录
  %(prog)s . -r                       # 递归转换子目录
  %(prog)s . --no-backup              # 不创建备份
  %(prog)s . -e "*.c" "*.h"           # 只转换指定扩展名
  %(prog)s . --force                  # 强制转换（即使已是UTF-8）
  %(prog)s . --backup-dir /path/bak   # 备份到指定目录
        """
    )
    
    parser.add_argument('directory', nargs='?', default='.',
                        help='要转换的目录路径 (默认: 当前目录)')
    
    parser.add_argument('-e', '--extensions', nargs='+', default=['*.c', '*.h', '*.cpp', '*.hpp'],
                        help='文件扩展名模式 (默认: *.c *.h *.cpp *.hpp)')
    
    parser.add_argument('-o', '--output-encoding', default='utf-8-sig',
                        choices=['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'utf-16-be'],
                        help='目标编码 (默认: utf-8-sig，即UTF-8 with BOM)')
    
    parser.add_argument('-r', '--recursive', action='store_true', default=True,
                        help='递归处理子目录 (默认: 是)')
    
    parser.add_argument('--no-recursive', action='store_true',
                        help='不递归处理子目录')
    
    parser.add_argument('-b', '--backup', action='store_true', default=True,
                        help='创建备份文件 (默认: 是)')
    
    parser.add_argument('--no-backup', action='store_true',
                        help='不创建备份文件')
    
    parser.add_argument('-f', '--force', action='store_true',
                        help='强制转换（即使已是目标编码）')
    
    parser.add_argument('--backup-dir',
                        help='备份文件保存目录')
    
    parser.add_argument('--dry-run', action='store_true',
                        help='模拟运行，不实际修改文件')
    
    args = parser.parse_args()
    
    # 处理参数
    recursive = not args.no_recursive
    backup = not args.no_backup
    
    print("=" * 50)
    print("批量编码转换工具")
    print("=" * 50)
    print(f"目录: {os.path.abspath(args.directory)}")
    print(f"扩展名: {args.extensions}")
    print(f"目标编码: {args.output_encoding}")
    print(f"递归: {'是' if recursive else '否'}")
    print(f"备份: {'是' if backup else '否'}")
    print(f"强制: {'是' if args.force else '否'}")
    print("=" * 50)
    
    if args.dry_run:
        print("\n[模拟模式] 不会实际修改文件\n")
    
    # 执行转换
    success, fail = batch_convert(
        args.directory,
        args.extensions,
        args.output_encoding,
        backup,
        args.backup_dir,
        recursive,
        args.force,
        args.dry_run
    )
    
    # 返回状态码
    sys.exit(0 if fail == 0 else 1)


if __name__ == '__main__':
    main()
