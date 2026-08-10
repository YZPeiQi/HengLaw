# 数据库数据工具集说明

本目录包含一组用于法律文本处理、结构化提取、MySQL 入库与导出的 Python 脚本。

## 1. 环境要求

- Python 3.9+
- Windows / macOS / Linux（当前项目主要按 Windows 路径习惯编写）
- 可访问的 MySQL 8.x（用于导入与导出脚本）

## 2. 安装依赖

在本目录下执行：

```bash
pip install -r requirements.txt
```

`requirements.txt` 当前包含：
- `mysql-connector-python`
- `PyPDF2`

说明：`tkinter/json/os/threading/csv/pathlib` 等为 Python 标准库，无需额外安装。

## 3. 脚本用途一览

- `PDFtoTXT.py`：批量把 PDF 转为 TXT（图形选择输入/输出目录）
- `去除人民法院案例库.py`：清理 TXT 中“人民法院案例库”等固定字样
- `txt转csv.py`：把一个目录里的多个 TXT 合并为 1 个 CSV（每个 txt 一行）
- `lay_display.py`：调用模型 API 提取结构化字段，输出 JSONL / HTML
- `remove_duplicates.py`：对 JSONL 的 `extractions` 按类别去重
- `MYSQL.py`：GUI 导入工具，把 JSONL 批量写入 MySQL `case_library`
- `product.py`：从 MySQL `case_library` 导出为 `exported_cases.json`

## 4. 推荐处理流程

1. PDF 转 TXT：运行 `PDFtoTXT.py`
2. 文本清理：运行 `去除人民法院案例库.py`
3. TXT 合并 CSV：运行 `txt转csv.py`
4. 模型抽取 JSONL：运行 `lay_display.py`
5. JSONL 去重：运行 `remove_duplicates.py`
6. 导入 MySQL：运行 `MYSQL.py`
7. 导出结果：运行 `product.py`

## 5. 各脚本快速用法

### 5.1 PDF 转 TXT

```bash
python PDFtoTXT.py
```

运行后会弹窗选择：
- 输入文件夹（PDF 所在目录）
- 输出文件夹（TXT 保存目录）

### 5.2 清理“人民法院案例库”字样

单文件默认输出 `_cleaned`：

```bash
python 去除人民法院案例库.py "D:\path\a.txt"
```

单文件指定输出：

```bash
python 去除人民法院案例库.py "D:\path\a.txt" "D:\path\a_clean.txt"
```

批量处理整个目录：

```bash
python 去除人民法院案例库.py "D:\path\txt目录" "D:\path\输出目录"
```

不带参数运行可进入交互模式。

### 5.3 TXT 合并 CSV

```bash
python txt转csv.py -i "D:\path\txt目录" -o "D:\path\merged_output.csv"
```

不传参数会提示输入。

### 5.4 结构化提取（JSONL / HTML）

```bash
python lay_display.py
```

GUI 内需设置：
- API 提供商（dashscope / deepseek）
- API Key
- 输入 CSV
- JSONL 输出目录
- HTML 输出目录

### 5.5 JSONL 去重

```bash
python remove_duplicates.py
```

运行后在 GUI 中选择输入/输出目录。

### 5.6 导入 MySQL

```bash
python MYSQL.py
```

GUI 中填写连接信息并点击“连接并初始化”，再选择 JSONL 目录并执行导入。

注意：`case_library.judgment_result` 字段已按 `TEXT` 处理，避免因内容过长导致 `Data too long`。

### 5.7 从 MySQL 导出 JSON

```bash
python product.py
```

默认导出到当前目录下 `exported_cases.json`。如需改连接参数，编辑脚本底部的 `CaseLibraryExporter(...)`。

## 6. 常见问题

### 6.1 `ModuleNotFoundError`

先确认已安装依赖：

```bash
pip install -r requirements.txt
```

### 6.2 MySQL 导入失败：连接错误

检查：
- MySQL 服务是否启动
- 账号密码是否正确
- 端口是否为 `3306`（或你的实际端口）
- 用户是否有建库建表权限

### 6.3 MySQL 导入失败：字段过长

当前 `MYSQL.py` 已自动校验并修正 `judgment_result` 为 `TEXT`。重新点击“连接并初始化”后再导入。

### 6.4 `tkinter` 不可用

`tkinter` 是标准库，但部分精简 Python 发行版可能未包含。请安装完整 Python 发行版。

## 7. 建议

- 先在少量样本上跑通全流程，再批量处理全部数据。
- 抽取结果可先用 `remove_duplicates.py` 清洗，再入库。
- 对生产库建议先备份后导入。
