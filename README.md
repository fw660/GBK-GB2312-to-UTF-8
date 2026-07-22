# Encoding Converter - 批量编码转换工具

将 GB2312/GBK 编码的 C/C++ 源文件批量转换为 UTF-8 with BOM 编码，专为 Keil 和 VS2010 开发环境优化。

## 功能特性

- **智能编码检测**：自动识别文件原始编码（GB2312、GBK、UTF-8 等）
- **批量转换**：支持递归处理整个项目目录
- **安全备份**：转换前自动创建备份，支持保留原始目录结构
- **多格式支持**：默认处理 `.c`、`.h`、`.cpp`、`.hpp` 文件
- **零依赖运行**：无需安装第三方库即可使用（推荐安装 `chardet` 提升检测精度）

## 快速开始

### 方式一：双击运行（推荐 Windows 用户）

1. 将 `convert_to_utf8.bat` 复制到你的项目根目录
2. 双击运行
3. 按提示输入目录路径并确认

### 方式二：命令行运行

```bash
# 转换当前目录
python convert_encoding.py .

# 转换指定项目
python convert_encoding.py /path/to/project
```

## 使用示例

```bash
# 递归转换子目录
python convert_encoding.py . -r

# 只转换 .c 文件
python convert_encoding.py . -e "*.c"

# 不创建备份
python convert_encoding.py . --no-backup

# 强制转换（即使已是 UTF-8）
python convert_encoding.py . --force

# 备份到指定目录
python convert_encoding.py . --backup-dir /path/to/backup

# 模拟运行（不实际修改文件）
python convert_encoding.py . --dry-run
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `directory` | 目标目录路径 | 当前目录 |
| `-e, --extensions` | 文件扩展名模式 | `*.c *.h *.cpp *.hpp` |
| `-o, --output-encoding` | 目标编码 | `utf-8-sig` |
| `-r, --recursive` | 递归处理子目录 | 是 |
| `-b, --backup` | 创建备份文件 | 是 |
| `--backup-dir` | 备份文件保存目录（保留原始目录结构） | 原文件旁 |
| `-f, --force` | 强制转换 | 否 |
| `--dry-run` | 模拟运行 | 否 |

## 编码说明

| 编码 | 说明 | 适用场景 |
|------|------|----------|
| **utf-8-sig** | UTF-8 with BOM | Keil 推荐（文件头添加 `EF BB BF` 标记） |
| **utf-8** | UTF-8 without BOM | 通用场景 |
| **gb2312** | 中文 GB2312 | 旧版遗留项目 |
| **gbk** | 中文 GBK | 扩展字符集 |

## 转换后配置 IDE

### Keil

1. 打开 Keil，进入 `Edit` → `Configuration` → `Editor`
2. 将 `Encoding` 设置为 `UTF-8`
3. 选择支持中文的字体（如 Courier New）

### VS2010

1. 打开 `File` → `Advanced Save Options`
2. 选择 `Unicode (UTF-8 with signature)`

## 常见问题

### 提示"未找到 Python"

需要先安装 Python 3.x：
- 下载地址：https://www.python.org/downloads/
- 安装时勾选 "Add Python to PATH"

### 转换后 Keil 还是乱码

确保已完成 IDE 配置（见上方"转换后配置 IDE"部分）。

### 如何恢复原文件

使用 `--backup-dir` 指定备份目录时，备份文件会按原始目录结构存放：

```
bak/
├── USER/
│   └── main.c       (原始编码备份)
└── HARDWARE/
    └── led.c        (原始编码备份)
```

找到对应目录下的备份文件，替换转换后的文件即可恢复。

### 安装 chardet 提升检测精度

```bash
pip install chardet
```

## 项目结构

```
encoding-converter/
├── convert_encoding.py    # 主程序（Python 脚本）
├── convert_to_utf8.bat    # Windows 批处理（双击运行）
├── test_gb2312.c          # 测试文件（含中文注释）
└── README.md              # 项目说明
```

## 注意事项

1. 转换前建议备份项目
2. 确保所有团队成员使用相同编码
3. 如果项目已在 Git 中，转换后需要提交更改

## License

MIT License
