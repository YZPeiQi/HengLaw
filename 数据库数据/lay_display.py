# 批量处理材料科学文本提取工具 - 支持DeepSeek和阿里云百炼API

import sys
import os
import json
import textwrap
import csv
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import re
from dataclasses import dataclass
from html import escape
from typing import Any, List
from urllib import error as urlerror
from urllib import request as urlrequest
import requests
from requests.exceptions import RequestException


# 轻量级兼容层：保留 extract/factory/lx 的调用习惯，去掉 langextract 依赖
@dataclass
class _Extraction:
    extraction_class: str
    extraction_text: str
    attributes: dict


@dataclass
class _ExampleData:
    text: str
    extractions: list


@dataclass
class _ExtractionResult:
    text: str
    extractions: list


@dataclass
class _ModelConfig:
    model_id: str
    provider: str
    provider_kwargs: dict


@dataclass
class _Model:
    model_id: str
    api_key: str
    base_url: str


class _Factory:
    ModelConfig = _ModelConfig

    @staticmethod
    def create_model(config: _ModelConfig) -> _Model:
        api_key = (config.provider_kwargs or {}).get("api_key", "")
        base_url = (config.provider_kwargs or {}).get("base_url", "")
        if not api_key:
            raise ValueError("缺少 api_key")
        if not base_url:
            raise ValueError("缺少 base_url")
        return _Model(model_id=config.model_id, api_key=api_key, base_url=base_url.rstrip("/"))


def _extract_json_from_text(raw_text: str) -> Any:
    text = (raw_text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\\s*", "", text)
        text = re.sub(r"\\s*```$", "", text)
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError("模型返回中未找到 JSON 对象")
        return json.loads(match.group(0))


def _chat_completion(model: _Model, messages: List[dict], timeout: int = 60) -> str:
    payload = {
        "model": model.model_id,
        "messages": messages,
        "temperature": 0.1,
    }
    req = urlrequest.Request(
        url=f"{model.base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {model.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlrequest.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except urlerror.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"API请求失败({e.code}): {body[:300]}") from e
    except Exception as e:
        raise RuntimeError(f"API请求异常: {e}") from e


def extract(
    text_or_documents,
    prompt_description,
    examples,
    model,
    fence_output=False,
    use_schema_constraints=False,
    extraction_passes=1,
    max_workers=1,
    max_char_buffer=1000,
):
    del fence_output, use_schema_constraints, extraction_passes, max_workers, max_char_buffer, examples

    source_text = text_or_documents if isinstance(text_or_documents, str) else str(text_or_documents)
    user_prompt = textwrap.dedent(
        f"""
        {prompt_description}

        请仅返回一个 JSON 对象，必须包含以下9个字段：
        case_title, case_date, case_region, court, cited_laws, case_summary, judgment_result, judgment_reason, key_points。

        待处理文本：
        {source_text}
        """
    ).strip()

    raw = _chat_completion(
        model,
        messages=[
            {"role": "system", "content": "你是信息抽取助手。仅返回合法JSON，不要输出解释。"},
            {"role": "user", "content": user_prompt},
        ],
    )

    obj = _extract_json_from_text(raw)
    keys = [
        "case_title",
        "case_date",
        "case_region",
        "court",
        "cited_laws",
        "case_summary",
        "judgment_result",
        "judgment_reason",
        "key_points",
    ]

    extractions = []
    for key in keys:
        value = obj.get(key, None) if isinstance(obj, dict) else None
        if isinstance(value, list):
            text_value = "\n".join(str(v) for v in value)
        elif value is None:
            text_value = "null"
        else:
            text_value = str(value)
        extractions.append(
            _Extraction(
                extraction_class=key,
                extraction_text=text_value,
                attributes={key: value},
            )
        )

    return _ExtractionResult(text=source_text, extractions=extractions)


class _IO:
    @staticmethod
    def save_annotated_documents(documents, output_name, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, output_name)
        with open(out_path, "w", encoding="utf-8") as f:
            for doc in documents:
                payload = {
                    "text": getattr(doc, "text", ""),
                    "extractions": [
                        {
                            "extraction_class": e.extraction_class,
                            "extraction_text": e.extraction_text,
                            "attributes": e.attributes,
                        }
                        for e in doc.extractions
                    ]
                }
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _visualize(jsonl_path: str) -> str:
    rows = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            for item in data.get("extractions", []):
                rows.append(
                    "<tr>"
                    f"<td>{escape(str(item.get('extraction_class', '')))}</td>"
                    f"<td>{escape(str(item.get('extraction_text', '')))}</td>"
                    f"<td>{escape(json.dumps(item.get('attributes', {}), ensure_ascii=False))}</td>"
                    "</tr>"
                )

    return (
        "<html><head><meta charset='utf-8'><title>Extraction Result</title>"
        "<style>body{font-family:Arial,sans-serif;padding:16px;}"
        "table{border-collapse:collapse;width:100%;}th,td{border:1px solid #ddd;padding:8px;vertical-align:top;}"
        "th{background:#f5f5f5;}</style></head><body>"
        "<h2>Extraction Result</h2>"
        "<table><thead><tr><th>Field</th><th>Text</th><th>Attributes</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></body></html>"
    )


class _Data:
    ExampleData = _ExampleData
    Extraction = _Extraction


class _LX:
    data = _Data
    io = _IO

    @staticmethod
    def visualize(path):
        return _visualize(path)


factory = _Factory
lx = _LX()

class MaterialScienceExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("材料科学文本批量提取工具 (支持DeepSeek/百炼)")
        self.root.geometry("850x1000")
        
        # API配置
        self.api_key = None
        self.api_provider = "dashscope"  # 默认百炼API
        
        # 模型选项配置
        self.model_options = {
            "dashscope": [
                ("Qwen QwQ-32B", "qwq-32b-preview"),
                ("Qwen3 Max", "qwen3-max"),
                ("Qwen Plus", "qwen-plus"),
                ("qwen3-vl-32b-thinking", "qwen3-vl-32b-thinking")
            ],
            "deepseek": [
                ("DeepSeek Chat", "deepseek-chat"),
                ("DeepSeek Reasoner", "deepseek-reasoner")
            ]
        }
        
        # API端点配置
        self.api_endpoints = {
            "dashscope": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "deepseek": "https://api.deepseek.com"
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置行和列的权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="材料科学文本批量提取工具 (支持DeepSeek/百炼API)", 
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 15))
        
        # API配置区域
        api_frame = ttk.LabelFrame(main_frame, text="API配置", padding="10")
        api_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 15))
        api_frame.columnconfigure(1, weight=1)
        
        # API提供商选择
        ttk.Label(api_frame, text="API提供商:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_provider_var = tk.StringVar(value="dashscope")
        self.api_provider_combo = ttk.Combobox(
            api_frame,
            textvariable=self.api_provider_var,
            values=["dashscope", "deepseek"],
            state="readonly",
            width=15
        )
        self.api_provider_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 10))
        self.api_provider_combo.bind("<<ComboboxSelected>>", self.on_api_provider_changed)
        
        # API密钥输入
        ttk.Label(api_frame, text="API密钥:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # 密钥输入框架
        key_frame = ttk.Frame(api_frame)
        key_frame.grid(row=1, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        key_frame.columnconfigure(0, weight=1)
        
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(
            key_frame,
            textvariable=self.api_key_var,
            width=40,
            show="*"  # 隐藏密钥显示
        )
        self.api_key_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # 密钥文件浏览按钮
        self.key_file_btn = ttk.Button(
            key_frame,
            text="浏览密钥文件",
            command=self.browse_key_file,
            width=12
        )
        self.key_file_btn.grid(row=0, column=1, sticky=tk.W)
        
        # 显示/隐藏密钥按钮
        self.show_key_var = tk.BooleanVar(value=False)
        self.show_key_check = ttk.Checkbutton(
            key_frame,
            text="显示",
            variable=self.show_key_var,
            command=self.toggle_key_visibility
        )
        self.show_key_check.grid(row=0, column=2, sticky=tk.W, padx=(5, 0))
        
        # API状态显示
        self.api_status_label = ttk.Label(
            api_frame,
            text="API状态: 未验证",
            foreground="orange"
        )
        self.api_status_label.grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        # 验证API按钮
        self.validate_btn = ttk.Button(
            api_frame,
            text="验证API",
            command=self.validate_api_key,
            width=10
        )
        self.validate_btn.grid(row=2, column=3, sticky=tk.E, pady=(5, 0))
        
        # 模型选择区域
        ttk.Label(main_frame, text="选择模型:").grid(row=2, column=0, sticky=tk.W, pady=10)
        
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(
            main_frame,
            textvariable=self.model_var,
            state="readonly",
            width=40
        )
        self.model_combo.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=10, padx=(5, 0))
        
        # 初始化模型列表
        self.update_model_list()
        
        # 输入CSV文件选择
        ttk.Label(main_frame, text="输入CSV文件:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.input_path_var = tk.StringVar()
        self.input_entry = ttk.Entry(
            main_frame,
            textvariable=self.input_path_var,
            width=50
        )
        self.input_entry.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        self.input_browse_btn = ttk.Button(
            main_frame,
            text="浏览",
            command=self.browse_input_file,
            width=8
        )
        self.input_browse_btn.grid(row=3, column=3, sticky=tk.W, pady=5, padx=(5, 0))
        
        # JSONL输出目录选择
        ttk.Label(main_frame, text="JSONL输出目录:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.jsonl_path_var = tk.StringVar()
        self.jsonl_entry = ttk.Entry(
            main_frame,
            textvariable=self.jsonl_path_var,
            width=50
        )
        self.jsonl_entry.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        self.jsonl_browse_btn = ttk.Button(
            main_frame,
            text="浏览",
            command=lambda: self.browse_directory(self.jsonl_path_var),
            width=8
        )
        self.jsonl_browse_btn.grid(row=4, column=3, sticky=tk.W, pady=5, padx=(5, 0))
        
        # HTML输出目录选择
        ttk.Label(main_frame, text="HTML输出目录:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.html_path_var = tk.StringVar()
        self.html_entry = ttk.Entry(
            main_frame,
            textvariable=self.html_path_var,
            width=50
        )
        self.html_entry.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        self.html_browse_btn = ttk.Button(
            main_frame,
            text="浏览",
            command=lambda: self.browse_directory(self.html_path_var),
            width=8
        )
        self.html_browse_btn.grid(row=5, column=3, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 处理选项
        options_frame = ttk.LabelFrame(main_frame, text="处理选项", padding="10")
        options_frame.grid(row=6, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=15)
        options_frame.columnconfigure(1, weight=1)
        
        # 最大处理行数
        ttk.Label(options_frame, text="最大处理行数:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.max_lines_var = tk.StringVar(value="")
        self.max_lines_entry = ttk.Entry(options_frame, textvariable=self.max_lines_var, width=15)
        self.max_lines_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        ttk.Label(options_frame, text="(留空表示处理全部)").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 文本列索引
        ttk.Label(options_frame, text="文本列索引:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.text_column_var = tk.StringVar(value="1")
        self.text_column_entry = ttk.Entry(options_frame, textvariable=self.text_column_var, width=15)
        self.text_column_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        ttk.Label(options_frame, text="(0-based索引，通常0是ID，1是文本)").grid(row=1, column=2, columnspan=2, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 延迟设置（防止API限速）
        ttk.Label(options_frame, text="请求延迟(秒):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.delay_var = tk.StringVar(value="1")
        self.delay_entry = ttk.Entry(options_frame, textvariable=self.delay_var, width=15)
        self.delay_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        ttk.Label(options_frame, text="(文档间延迟，防止API限速)").grid(row=2, column=2, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 进度显示区域
        progress_frame = ttk.LabelFrame(main_frame, text="处理进度", padding="10")
        progress_frame.grid(row=7, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)
        
        # 进度条
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='indeterminate'
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 日志文本框
        self.log_text = tk.Text(
            progress_frame,
            height=10,
            width=85,
            state='disabled',
            wrap=tk.WORD
        )
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 滚动条
        scrollbar = ttk.Scrollbar(progress_frame, command=self.log_text.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.log_text['yscrollcommand'] = scrollbar.set
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=4, pady=(5, 0))
        
        # 开始处理按钮
        self.start_button = ttk.Button(
            button_frame,
            text="开始批量处理",
            command=self.start_processing,
            state='normal',
            width=15
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # 停止按钮
        self.stop_button = ttk.Button(
            button_frame,
            text="停止",
            command=self.stop_processing,
            state='disabled',
            width=10
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 清空日志按钮
        self.clear_button = ttk.Button(
            button_frame,
            text="清空日志",
            command=self.clear_log,
            width=10
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # 测试单个文档按钮
        self.test_button = ttk.Button(
            button_frame,
            text="测试单个文档",
            command=self.test_single_document,
            width=12
        )
        self.test_button.pack(side=tk.LEFT, padx=5)
        
        # 退出按钮
        self.exit_button = ttk.Button(
            button_frame,
            text="退出",
            command=self.root.quit,
            width=10
        )
        self.exit_button.pack(side=tk.LEFT, padx=5)
        
        # 处理控制变量
        self.processing = False
        self.current_thread = None
        self.api_validated = False
        
        # 设置默认路径（可选）
        self.set_default_paths()
    
    def validate_api_key(self):
        """验证API密钥的正确性"""
        api_key = self.api_key_var.get().strip()
        provider = self.api_provider_var.get()
        
        if not api_key:
            messagebox.showwarning("警告", "请输入API密钥")
            self.api_status_label.config(text="API状态: 请输入密钥", foreground="red")
            return False
        
        # 保存原始密钥
        original_key = api_key
        
        # 基本格式检查
        if len(api_key) < 20:
            messagebox.showwarning("警告", "API密钥格式似乎不正确（过短）")
            self.api_status_label.config(text="API状态: 密钥格式错误", foreground="red")
            return False
        
        # 根据提供商检查密钥格式
        if provider == "dashscope":
            # 百炼API密钥通常以"sk-"开头
            if not api_key.startswith("sk-"):
                self.log_message("提示: 百炼API密钥通常以'sk-'开头")
        
        elif provider == "deepseek":
            # DeepSeek API密钥通常也是以"sk-"开头
            if not api_key.startswith("sk-"):
                self.log_message("提示: DeepSeek API密钥通常以'sk-'开头")
        
        # 测试密钥有效性
        self.log_message(f"正在验证{provider} API密钥...")
        self.validate_btn.config(state='disabled', text="验证中...")
        self.root.update()
        
        try:
            # 创建测试配置
            config = factory.ModelConfig(
                model_id=self.model_var.get(),
                provider="OpenAiLanguageModel",
                provider_kwargs={
                    'api_key': api_key,
                    'base_url': self.api_endpoints[provider]
                }
            )
            
            # 尝试创建模型实例
            model = factory.create_model(config)
            
            # 尝试一个简单的测试请求
            test_text = "This is a test message for API validation."
            
            # 使用模型进行简单测试（尝试调用一个简单的方法）
            # 这里我们尝试使用模型生成一个简单的响应来验证密钥
            try:
                # 根据langextract库的API，我们可以尝试一个简单的提取测试
                test_prompt = "Extract test."
                test_example = lx.data.ExampleData(
                    text="Test document.",
                    extractions=[]
                )
                
                # 设置较短的超时时间
                # ...已移至文件顶部...
                
                # 创建一个简单的HTTP请求来测试连接
                test_headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                test_payload = {
                    "model": self.model_var.get(),
                    "messages": [{"role": "user", "content": "Say 'API test successful'"}],
                    "max_tokens": 10
                }
                
                # 发送测试请求
                test_url = self.api_endpoints[provider]
                if provider == "dashscope":
                    # 百炼API使用兼容模式端点
                    response = requests.post(
                        f"{test_url}/chat/completions",
                        headers=test_headers,
                        json=test_payload,
                        timeout=10
                    )
                else:
                    # DeepSeek API
                    response = requests.post(
                        f"{test_url}/chat/completions",
                        headers=test_headers,
                        json=test_payload,
                        timeout=10
                    )
                
                # 检查响应状态
                if response.status_code == 200:
                    self.api_key = original_key
                    self.api_validated = True
                    
                    # 更新状态
                    self.api_status_label.config(
                        text=f"API状态: {provider.upper()}密钥验证成功",
                        foreground="green"
                    )
                    
                    # 解析响应获取模型信息
                    try:
                        response_data = response.json()
                        if "model" in response_data:
                            self.log_message(f"✓ API密钥验证成功！使用模型: {response_data['model']}")
                        else:
                            self.log_message("✓ API密钥验证成功！")
                    except:
                        self.log_message("✓ API密钥验证成功！")
                    
                    messagebox.showinfo("验证成功", f"{provider.upper()} API密钥验证成功！")
                    return True
                else:
                    error_msg = f"API验证失败 (状态码: {response.status_code})"
                    if response.status_code == 401:
                        error_msg = "API密钥无效或已过期"
                    elif response.status_code == 403:
                        error_msg = "API密钥权限不足"
                    elif response.status_code == 404:
                        error_msg = "API端点不存在或模型不可用"
                    elif response.status_code == 429:
                        error_msg = "API请求过于频繁，请稍后重试"
                    
                    self.api_status_label.config(
                        text=f"API状态: 验证失败",
                        foreground="red"
                    )
                    self.log_message(f"✗ {error_msg}")
                    
                    # 尝试获取更多错误信息
                    try:
                        error_data = response.json()
                        if "error" in error_data:
                            error_detail = error_data["error"].get("message", str(error_data))
                            self.log_message(f"错误详情: {error_detail}")
                    except:
                        self.log_message(f"原始响应: {response.text[:200]}")
                    
                    messagebox.showerror("验证失败", error_msg)
                    return False
                    
            except RequestException as e:
                # 网络请求错误
                error_msg = f"网络连接错误: {str(e)}"
                self.api_status_label.config(
                    text=f"API状态: 连接失败",
                    foreground="red"
                )
                self.log_message(f"✗ {error_msg}")
                messagebox.showerror("验证失败", error_msg)
                return False
                
        except Exception as e:
            # 模型创建或配置错误
            error_msg = f"API配置错误: {str(e)}"
            self.api_status_label.config(
                text=f"API状态: 配置错误",
                foreground="red"
            )
            self.log_message(f"✗ {error_msg}")
            messagebox.showerror("验证失败", error_msg)
            return False
        finally:
            self.validate_btn.config(state='normal', text="验证API")
    
    # 以下是其他方法的实现（与之前相同，为节省空间未完整展示）
    # 请保持原有的所有其他方法不变，只修改validate_api_key方法
    
    def on_api_provider_changed(self, event):
        """API提供商变更事件处理"""
        provider = self.api_provider_var.get()
        self.update_model_list()
        
        # 根据提供商更新状态标签
        if provider == "dashscope":
            self.api_status_label.config(text="API状态: 使用阿里云百炼API", foreground="blue")
        else:
            self.api_status_label.config(text="API状态: 使用DeepSeek API", foreground="purple")
        
        self.api_validated = False
        self.log_message(f"已切换到{provider} API，请重新验证API密钥")
    
    def update_model_list(self):
        """更新模型列表"""
        provider = self.api_provider_var.get()
        models = self.model_options.get(provider, [])
        
        # 更新下拉列表
        self.model_combo['values'] = [model_id for _, model_id in models]
        
        # 设置默认值
        if models:
            self.model_var.set(models[0][1])
    
    def browse_key_file(self):
        """浏览API密钥文件"""
        file_path = filedialog.askopenfilename(
            title="选择API密钥文件",
            filetypes=[("文本文件", "*.txt"), ("环境文件", "*.env"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    
                    # 尝试从文件内容中提取API密钥
                    lines = content.split('\n')
                    for line in lines:
                        line = line.strip()
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip().upper()
                            
                            # 根据选择的API提供商确定密钥名称
                            provider = self.api_provider_var.get()
                            if provider == "dashscope":
                                if "DASHSCOPE" in key or "API_KEY" in key:
                                    self.api_key_var.set(value.strip())
                                    self.log_message(f"从文件加载{provider} API密钥")
                                    break
                            elif provider == "deepseek":
                                if "DEEPSEEK" in key or "API_KEY" in key:
                                    self.api_key_var.set(value.strip())
                                    self.log_message(f"从文件加载{provider} API密钥")
                                    break
                    else:
                        # 如果没有找到特定格式，使用整个文件内容
                        if len(content) > 20:  # 假设API密钥长度大于20
                            self.api_key_var.set(content)
                            self.log_message(f"从文件加载API密钥")
            except Exception as e:
                self.log_message(f"读取密钥文件时出错: {e}")
                messagebox.showerror("错误", f"读取密钥文件失败: {e}")
    
    def toggle_key_visibility(self):
        """切换密钥显示/隐藏"""
        if self.show_key_var.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")
    
    def browse_input_file(self):
        """浏览输入文件"""
        file_path = filedialog.askopenfilename(
            title="选择CSV文件",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        if file_path:
            self.input_path_var.set(file_path)
    
    def browse_directory(self, path_var):
        """浏览目录"""
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            path_var.set(dir_path)
    
    def log_message(self, message):
        """添加日志消息"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update_idletasks()
    
    def clear_log(self):
        """清空日志"""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
    
    def set_default_paths(self):
        """设置默认路径"""
        default_base = r"D:\langextract-main\material_extraction"
        
        if not self.jsonl_path_var.get():
            self.jsonl_path_var.set(os.path.join(default_base, "Jsonl_Output"))
        
        if not self.html_path_var.get():
            self.html_path_var.set(os.path.join(default_base, "HTML_Output"))
    
    def validate_inputs(self):
        """验证输入参数"""
        # 验证API密钥
        if not self.api_validated:
            response = messagebox.askyesno("确认", "API密钥未验证，是否继续处理？")
            if not response:
                return False
        
        # 验证输入文件
        if not self.input_path_var.get():
            messagebox.showerror("错误", "请选择输入CSV文件")
            return False
        
        if not os.path.exists(self.input_path_var.get()):
            messagebox.showerror("错误", f"输入文件不存在: {self.input_path_var.get()}")
            return False
        
        # 验证列索引
        try:
            text_column = int(self.text_column_var.get())
            if text_column < 0:
                messagebox.showerror("错误", "文本列索引必须大于等于0")
                return False
        except ValueError:
            messagebox.showerror("错误", "文本列索引必须是整数")
            return False
        
        # 验证最大行数
        max_lines = self.max_lines_var.get()
        if max_lines:
            try:
                max_lines_int = int(max_lines)
                if max_lines_int <= 0:
                    messagebox.showerror("错误", "最大处理行数必须大于0")
                    return False
            except ValueError:
                messagebox.showerror("错误", "最大处理行数必须是整数")
                return False
        
        # 验证延迟时间
        try:
            delay = float(self.delay_var.get())
            if delay < 0:
                messagebox.showerror("错误", "请求延迟必须大于等于0")
                return False
        except ValueError:
            messagebox.showerror("错误", "请求延迟必须是数字")
            return False
        
        # 验证输出目录
        output_dirs = [self.jsonl_path_var.get(), self.html_path_var.get()]
        for directory in output_dirs:
            if not directory:
                messagebox.showerror("错误", "请设置所有输出目录")
                return False
        
        return True
    
    def start_processing(self):
        """开始处理"""
        if not self.validate_inputs():
            return
        
        # 禁用开始按钮，启用停止按钮
        self.start_button.config(state='disabled')
        self.test_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.processing = True
        
        # 启动进度条
        self.progress_bar.start(10)
        
        # 在新线程中运行处理任务
        self.current_thread = threading.Thread(target=self.run_extraction)
        self.current_thread.start()
    
    def stop_processing(self):
        """停止处理"""
        self.processing = False
        self.log_message("正在停止处理...")
        self.start_button.config(state='normal')
        self.test_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_bar.stop()
    
    def test_single_document(self):
        """测试单个文档"""
        if not self.validate_inputs():
            return
        
        # 使用第一个文档进行测试
        try:
            # 读取CSV文件
            csv_path = self.input_path_var.get()
            text_column = int(self.text_column_var.get())
            
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                if len(rows) > 1:
                    # 使用第二行（跳过标题行）
                    if len(rows[1]) > text_column:
                        doc_id = rows[1][0].strip() if rows[1][0].strip() else "test_001"
                        text = rows[1][text_column].strip()
                        
                        self.log_message(f"测试文档 - ID: {doc_id}")
                        self.log_message(f"文本内容: {text[:100]}...")
                        
                        # 在新线程中运行测试
                        test_thread = threading.Thread(
                            target=self.run_single_extraction,
                            args=(doc_id, text)
                        )
                        test_thread.start()
                    else:
                        messagebox.showerror("错误", f"CSV文件第2行没有第{text_column+1}列")
                else:
                    messagebox.showerror("错误", "CSV文件内容不足")
        except Exception as e:
            self.log_message(f"测试失败: {e}")
    
    def run_single_extraction(self, doc_id, text):
        """运行单个文档提取测试"""
        try:
            provider = self.api_provider_var.get()
            model_id = self.model_var.get()
            api_key = self.api_key_var.get().strip()
            
            # 配置模型
            config = factory.ModelConfig(
                model_id=model_id,
                provider="OpenAiLanguageModel",
                provider_kwargs={
                    'api_key': api_key,
                    'base_url': self.api_endpoints[provider]
                }
            )
            
            model = factory.create_model(config)
            self.log_message(f"✓ 成功创建{provider}模型: {model_id}")
            
            # 定义提取提示
            prompt = textwrap.dedent("""
                你是一名资深的律师，专注于案件分析。请仔细阅读以下法律文书，并从中提取核心案件信息。
                请严格按照以下字段和格式要求提取，并以 JSON 格式输出：
                这九个字段("case_title", "case_date", "case_region", "court", "cited_laws", "case_summary", "judgment_result", "judgment_reason", "key_points")必须全部提取并输出，缺一不可。
                {
                  "case_title": "案件标题（如：张三诉李四民间借贷纠纷案）",
                  "case_date": "案件发生或判决时间（必须采用 YYYY-MM-DD 的规范格式）",
                  "case_region": "如：北京市朝阳区",
                  "court": "受理审判的法院名称（如：北京市朝阳区人民法院）",
                  "cited_laws": ["引用的具体法律条文名称及条款", "《中华人民共和国民法典》第一条..."],
                  "case_summary": "基本案情后面的内容",
                  "judgment_result": "判决结果（认为，认定，确认，限100字以内的核心结果总结）",
                  "judgment_reason": "裁判理由后面内容",
                  "key_points": "关键词"
                }
                
                注意：
                1. 这九个字段("case_title", "case_date", "case_region", "court", "cited_laws", "case_summary", "judgment_result", "judgment_reason", "key_points")必须全部提取并输出，缺一不可。
                2. 必须输出纯 JSON 格式（不要包含 markdown 代码块标记，不要包含其他解释性文字）。
                3. 对于文本中未提供或无法确定的字段，请填写 null。
                4. cited_laws 必须是字符串数组格式。
                5. case_date 务必转为 YYYY-MM-DD 的纯日期格式。
            """)
            
            # 定义示例数据（与批量处理相同）
            material_examples = self.get_material_examples()
            
            # 执行提取
            full_text = f"{doc_id}, {text}"
            self.log_message("正在提取实体信息...")
            
            result = extract(
                text_or_documents=full_text,
                prompt_description=prompt,
                examples=material_examples,
                model=model,
                fence_output=False,
                use_schema_constraints=False,
                extraction_passes=1,
                max_workers=1,
                max_char_buffer=1000
            )
            
            # 显示提取结果
            self.log_message("✓ 提取完成！")
            self.log_message(f"提取到的实体数量: {len(result.extractions)}")
            
            for i, extraction in enumerate(result.extractions):
                self.log_message(f"  实体{i+1}: [{extraction.extraction_class}] {extraction.extraction_text[:50]}...")
            
            messagebox.showinfo("测试成功", f"成功提取{len(result.extractions)}个实体")
            
        except Exception as e:
            self.log_message(f"✗ 测试失败: {e}")
            messagebox.showerror("测试失败", f"提取失败: {str(e)}")
    
    def get_material_examples(self):
        """获取材料科学示例数据"""
        return [
            lx.data.ExampleData(
    text="""
2023-07-2-091-008
吕某诉王某房屋买卖合同纠纷案
——购买校舍改建小产权房的房屋买卖合同无效
关键词 民事 房屋买卖合同 校舍改建房 居住权转让 转让会员资格
教育科研设计用地 社会公共教育资源 无效合同
基本案情
原告吕某诉称：其与王某签订《房屋买卖合同书》，购买王某名下
小产权房一套，后得知房屋产权登记的名字仍为王某，原告多次联系王
某，王某拒不协助其办理物业更名手续。故请求判令：1.确认其与王某
签订的《房屋买卖合同》无效；2.王某退还购房款13万元；3.王某支付
资金占用期间使用费；4.王某支付其因无法居住而产生的房屋租赁费用
。
被告王某辩称：其与吕某签订的转让协议实际上转让的是案涉房屋
的会员资格和居住权，买卖合同是对转让协议的补充，实为居住权转让
；吕某不支付房款属于违约，不应由其退还购房款，而应由吕某支付违
约金；吕某已经取得《会员手册》，其清楚房屋的使用性质，如认为合
同有效，则吕某应配合其办理《会员手册》更名手续并赔偿违约金，如
确认合同无效，则双方各承担相应责任。
法院经审理查明：2018年4月24日，卖方王某与买方吕某就签订《房
屋买卖合同书》，约定王某将案涉房屋出卖给吕某，总售价为73万元
，先行支付13万元，其余60万元后续分三次支付。合同签订当日，双方
在案涉房屋的物业管理部门办理了小区《会员手册》更名手续，将《会
员手册》中的王某变更为吕某，并将房屋的所有附属物品交给了吕某。
2018年4月30日前，吕某按合同约定向王某支付了第一期购房款13万元。
案涉房屋系由某学院校区校舍改建而来。《国有建设用地划拨决定
书》载明，该宗地用途为教育科研用地，主体建筑物和附属建筑物性质
均为教学用房、宿舍、食堂及配套设施。
北京市延庆区人民法院于2020年6月19日作出（2020）京0119民初
3092号民事判决：一、确认王某与吕某签订的《房屋买卖合同书》无效
；二、王某返还吕某购房款13万元；三、驳回吕某的其他诉讼请求。该
判决为终审判决。
裁判理由
生效裁判认为，本案的争议焦点为校舍改建房买卖合同的性质和效
力认定。
1.案涉《房屋买卖合同书》的性质
吕某与王某签订的合同，就涉案房屋买卖事宜进行了明确、详细的
约定，该合同载明了房屋坐落，约定了价款、支付时间、支付方式、交
付事宜、违约责任等具体条款，符合房屋买卖合同的基本特征，且纵览
整个合同并无租赁、转让居住权、转让会员资格的相关表述，故无论从
该合同的形式要件还是条款内容上都可以看出，双方真实意思表示系就
涉案房屋进行买卖，而非对居住权或会员资格进行转让，故王某与吕某
签订的《房屋买卖合同书》性质应为房屋买卖合同。
2.案涉《房屋买卖合同书》的效力认定
涉案房屋所属建设用地系某学院经北京市人民政府批准划拨取得
，且只限用于建设某学院某校区项目，建筑物性质均为教育用房、宿舍
、食堂及配套设施，涉案房屋系由校舍改建而来，具有社会公共教育资
源的属性。现王某与吕某对经校舍改建而来的涉案房屋进行买卖，改变
了本应用于社会公共教育事业的划拨建设用地及其上校舍之用途，侵害
了社会公共教育资源，损害了社会公共利益，违背了公序良俗，故王某
与吕某签订的《房屋买卖合同书》应为无效，王某应返还吕某先行支付
的购房款13万元。
王某、吕某均明知涉案房屋系由某学院某校区校舍改建而来，但在
此情况下仍签订《房屋买卖合同书》，故双方对合同无效均负有过错
，吕某无权要求王某支付资金占用期间的使用费用；吕某要求王某支付
房屋租赁费用、房屋维修费用，因吕某并未提交证据证明其存在相关损
失，故对此诉讼请求不予支持。
裁判要旨
1.合同性质的认定应当从合同形式要件和实质要件两方面加以认定
，综合合同内容、双方当事人真实意思表示加以判断。双方签订的合同
内容载明了房屋位置，约定了价款、支付时间、支付方式、交付事宜、
违约责任等具体条款，符合房屋买卖合同的基本特征的，应认定双方之
间签署的合同属于房屋买卖合同。
2.买卖双方就具有社会公共教育资源属性的校舍改建房屋签订房屋
买卖合同，因合同改变了社会公共教育事业的划拨建设用地用途，侵害
了社会公共教育资源，损害了社会公共利益，违背公序良俗，应属无效
。因合同无效产生的各种损失，双方自负责任。
关联索引
《中华人民共和国民法典》第153条（本案适用的是2017年10月1日
施行的《中华人民共和国民法总则》第153条）
《中华人民共和国民法典》第157条（本案适用的是1999年10月1日
起施行的《中华人民共和国合同法》第58条）
一审：北京市延庆区人民法院（2020）京0119民初3092号民事判决
（2020年6月19日）

本案例文本已于2024年2月23日作出调整""",
    extractions=[
        lx.data.Extraction(
            extraction_class="case_title",
            extraction_text="吕某诉王某房屋买卖合同纠纷案",
            attributes={"case_title": "吕某诉王某房屋买卖合同纠纷案"}
        ),
        lx.data.Extraction(
            extraction_class="case_date",
            extraction_text="2023-07-2-091-008",
            attributes={"case_date": "2023-07-02"}
        ),
        lx.data.Extraction(
            extraction_class="case_region",
            extraction_text="北京市延庆区人民法院于2020年6月19日作出（2020）京0119民初\n3092号民事判决：",
            attributes={"case_region": "北京市延庆区"}
        ),
        lx.data.Extraction(
            extraction_class="court",
            extraction_text="北京市延庆区人民法院于2020年6月19日作出（2020）京0119民初\n3092号民事判决：",
            attributes={"court": "北京市延庆区人民法院"}
        ),
        lx.data.Extraction(
            extraction_class="court",
            extraction_text="一审：北京市延庆区人民法院（2020）京0119民初3092号民事判决\n（2020年6月19日）",
            attributes={"court": "北京市延庆区人民法院"}
        ),
        lx.data.Extraction(
            extraction_class="cited_laws",
            extraction_text="《中华人民共和国民法典》第153条（本案适用的是2017年10月1日\n施行的《中华人民共和国民法总则》第153条）\n《中华人民共和国民法典》第157条（本案适用的是1999年10月1日\n起施行的《中华人民共和国合同法》第58条）",
            attributes={"cited_laws": '["《中华人民共和国民法典》第153条", "《中华人民共和国民法典》第157条"]'}
        ),
        lx.data.Extraction(
            extraction_class="case_summary",
            extraction_text="原告吕某诉称：其与王某签订《房屋买卖合同书》，购买王某名下\n小产权房一套，后得知房屋产权登记的名字仍为王某，原告多次联系王\n某，王某拒不协助其办理物业更名手续。故请求判令：1.确认其与王某\n签订的《房屋买卖合同》无效；2.王某退还购房款13万元；3.王某支付\n资金占用期间使用费；4.王某支付其因无法居住而产生的房屋租赁费用\n。\n被告王某辩称：其与吕某签订的转让协议实际上转让的是案涉房屋\n的会员资格和居住权，买卖合同是对转让协议的补充，实为居住权转让\n；吕某不支付房款属于违约，不应由其退还购房款，而应由吕某支付违\n约金；吕某已经取得《会员手册》，其清楚房屋的使用性质，如认为合\n同有效，则吕某应配合其办理《会员手册》更名手续并赔偿违约金，如\n确认合同无效，则双方各承担相应责任。\n法院经审理查明：2018年4月24日，卖方王某与买方吕某就签订《房\n屋买卖合同书》，约定王某将案涉房屋出卖给吕某，总售价为73万元\n，先行支付13万元，其余60万元后续分三次支付。合同签订当日，双方\n在案涉房屋的物业管理部门办理了小区《会员手册》更名手续，将《会\n员手册》中的王某变更为吕某，并将房屋的所有附属物品交给了吕某。\n2018年4月30日前，吕某按合同约定向王某支付了第一期购房款13万元。\n案涉房屋系由某学院校区校舍改建而来。《国有建设用地划拨决定\n书》载明，该宗地用途为教育科研用地，主体建筑物和附属建筑物性质\n均为教学用房、宿舍、食堂及配套设施。",
            attributes={"case_summary": "原告吕某诉称其与王某签订房屋买卖合同购买校舍改建的小产权房，现请求确认合同无效并退还购房款。被告王某辩称实为居住权转让。法院查明案涉房屋为教育科研用地校舍改建，买卖改变了社会公共教育资源用途，损害公共利益。"}
        ),
        lx.data.Extraction(
            extraction_class="judgment_result",
            extraction_text="一、确认王某与吕某签订的《房屋买卖合同书》无效\n；二、王某返还吕某购房款13万元；三、驳回吕某的其他诉讼请求。",
            attributes={"judgment_result": "确认《房屋买卖合同书》无效，王某返还吕某购房款13万元，驳回其他诉讼请求。"}
        ),
        lx.data.Extraction(
            extraction_class="judgment_reason",
            extraction_text="生效裁判认为，本案的争议焦点为校舍改建房买卖合同的性质和效力认定。\n1.案涉《房屋买卖合同书》的性质\n吕某与王某签订的合同，就涉案房屋买卖事宜进行了明确、详细的约定，该合同载明了房屋坐落，约定了价款、支付时间、支付方式、交付事宜、违约责任等具体条款，符合房屋买卖合同的基本特征，且纵览整个合同并无租赁、转让居住权、转让会员资格的相关表述，故无论从该合同的形式要件还是条款内容上都可以看出，双方真实意思表示系就涉案房屋进行买卖，而非对居住权或会员资格进行转让，故王某与吕某签订的《房屋买卖合同书》性质应为房屋买卖合同。\n2.案涉《房屋买卖合同书》的效力认定\n涉案房屋所属建设用地系某学院经北京市人民政府批准划拨取得，且只限用于建设某学院某校区项目，建筑物性质均为教育用房、宿舍、食堂及配套设施，涉案房屋系由校舍改建而来，具有社会公共教育资源的属性。现王某与吕某对经校舍改建而来的涉案房屋进行买卖，改变了本应用于社会公共教育事业的划拨建设用地及其上校舍之用途，侵害了社会公共教育资源，损害了社会公共利益，违背了公序良俗，故王某与吕某签订的《房屋买卖合同书》应为无效，王某应返还吕某先行支付的购房款13万元。\n王某、吕某均明知涉案房屋系由某学院某校区校舍改建而来，但在此情况下仍签订《房屋买卖合同书》，故双方对合同无效均负有过错",
            attributes={"judgment_reason": "合同具有房屋买卖基本特征属于买卖合同。但案涉房屋具有社会公共教育资源属性，买卖行为违背公序良俗，合同无效。因双方均有过错，故不支持其他损失赔偿请求。"}
        ),
        lx.data.Extraction(
            extraction_class="key_points",
            extraction_text="关键词 民事 房屋买卖合同 校舍改建房 居住权转让 转让会员资格\n教育科研设计用地 社会公共教育资源 无效合同",
            attributes={"key_points": "民事 房屋买卖合同 校舍改建房 居住权转让 社会公共教育资源 无效合同"}
        )
    ]
),
            lx.data.ExampleData(
    text="""

2023-16-2-490-002
董某某诉某出版社劳动争议纠纷案
——人事争议案件受案范围及事业单位转企后的劳动争议案件的处理
关键词 民事 劳动争议 人事争议 受案范围 事业单位转企
基本案情
原告某出版社以董某某已辞职，双方已解除人事关系，劳动争议仲
裁委员会认定事实错误，适用法律不当为由起诉请求：确认董某某
1989年辞职行为有效，双方不存在劳动关系。
董某某辩称，某出版社至今没有向其送达解除劳动关系的书面决定
，档案仍在该社，故同意劳动仲裁裁决，不同意某出版社的诉讼请求。
法院经审理查明：某出版社成立于1951年，原为国家新闻出版署所
属的事业单位。某出版社于1998年领取企业法人营业执照，实行自收自
支，独立核算。2002年1月9日，某出版社同时取得《事业单位法人证书
》。2009年2月24日，某出版社注销《事业单位法人证书》。2011年2月
18日，某出版社名称变更为某出版公司。
董某某自1975年开始在某出版社工作，1989年2月，董某某以借调形
式至海南某公司工作，借聘期为三年。1989年8月4日，董某某向某出版
社递交了辞职报告，在报告中表示想获得高级职称证明。同年，某出版
社负责人在该辞职报告上批示人事部门按规定办理。董某某主张自己在
提交辞职报告后，时隔几日又分别给社长和人事处打电话，表示自己不
辞职了。1990年1月，某出版社给董某某开具了高级职称证明。时隔6年
后，董某某于1996年找到某出版社，要求安排工作。某出版社以董某某
已于1989年辞职为由未给董某某安排工作。此后，董某某一直向某出版
社的上级机构某出版总社反映情况。2001年1月，某出版总社出具书面意

见，同意某出版社对董某某辞职一事的处理。随后，董某某于2001年2月
向人事部人事仲裁公正厅仲裁办公室提交了仲裁申请书，因得知某出版
社已领取企业法人营业执照，董某某撤回上述仲裁申请。2002年3月，董
某某向北京市东城区劳动争议仲裁委员会申请劳动仲裁，要求撤销《关
于董某某同志辞职的处理意见》，恢复与某出版社的劳动关系。仲裁机
构支持了董某某的申诉请求，裁决维持某出版社与董某某之间的劳动关
系。某出版社不服而诉至法院，要求确认董某某1989年辞职行为有效
，双方不存在劳动关系。
北京市东城区人民法院于2002年9月20日作出（2002）东民初字第
3023号民事判决：一、确认董某某于一九八九年八月四日已从某出版社
辞职，某出版社于判决生效后十五日内给付董某某人民币一万四千八百
零七元整。二、驳回董某某其他诉讼请求。宣判后，董某某不服提起上
诉。北京市第二中级人民法院于2002年12月13日作出（2002）二中民终
字第9666号民事判决：驳回上诉，维持原判。董某某不服，向检察机关
申请监督。北京市人民检察院就本案向北京市高级人民法院提出抗诉。
北京市第二中级人民法院于2015年10月16日作出（2015）二中民再终字
第09289号民事判决，维持该院（2002）二中民终字第9666号民事判决。
裁判理由
法院生效裁判认为，本案的争议焦点有二，一是本案是否为劳动争
议纠纷，二是董某某的辞职行为是否成立。
关于本案是否为劳动争议纠纷的问题。根据某出版社提交的企业法
人营业执照与事业单位法人证书，1998年至2009年期间，某出版社性质
上应属于实行企业化管理的事业组织。根据《劳动部办公厅关于实行企
业化管理的事业组织与职工发生劳动争议有关问题的复函》的规定，实
行企业化管理的事业组织的全体职工应按照《劳动法》的规定，与所在

单位通过签订劳动合同建立劳动关系。本案中，董某某的仲裁请求是维
持与某出版社的劳动关系，某出版社起诉要求确认董某某于1989年已经
辞职。某出版社与董某某之间的纠纷从1989年递交辞职报告起至2002年
申请劳动仲裁，时间跨度较长，加之1998年某出版社开始实行企业化管
理，本案涉及人事关系与劳动关系的衔接和变更问题。此外，最高人民
法院于2003年8月27日下发《人事争议司法解释》首次将部分人事争议纳
入人民法院的受案范围。本案董某某申请仲裁、某出版社起诉的时间为
2002年，结合当时的法律政策，双方无法就人事争议提起民事诉讼。且
本案二审终审后，董某某于2005年、2007年两次向相关部门申请人事仲
裁，但均未被受理。综合某出版社性质变更情况及本案纠纷发生的背景
，原审以劳动争议纠纷受理并作出判决并无不妥。
关于董某某的辞职行为是否成立的问题。1990年9月8日，人事部发
布《全民所有制事业单位专业技术人员和管理人员辞职暂行规定》，对
事业单位人员辞职的流程作出具体规定，该规定自发布之日起试行。董
某某于1989年8月4日递交辞职报告，某出版社未能及时办理辞职手续。
因《全民所有制事业单位专业技术人员和管理人员辞职暂行规定》实施
于1990年9月8日，并不具有溯及既往的效力，故董某某主张某出版社违
反人事部相关规定，依据不足。本案中，董某某于1989年8月4日向某出
版社递交书面辞职报告并由时任社长批示按规定办理。董某某虽主张撤
回辞职继续借调，但未能提交确实充分的依据，同时结合3年借调期满后
，董某某长期未和某出版社联系的实际情况，可以认为董某某的辞职行
为已经生效。
裁判要旨
1.人事争议纠纷解决有其自身的发展历程，与司法程序接轨后，人
事争议案件受案范围、程序亦有明确规范，判断一个案件是劳动争议还

是人事争议，应结合当事人的诉求及案件客观情况进行。
2.事业单位转企后，劳动者要求继续履行聘用合同或劳动合同的纠
纷宜作为劳动争议案件受理。
关联索引
《最高人民法院关于人民法院审理事业单位人事争议案件若干问题
的规定》第3条
一审：北京市东城区人民法院（2002）东民初字第3023号民事判决
（2002年9月20日）
二审：北京市第二中级人民法院（2002）二中民终字第9666号民事
判决（2002年12月13日）
再审：北京市第二中级人民法院（2015）二中民再终字第09289号民
事判决（2015年10月16日）

本案例文本已于2024年2月24日作出调整""",
    extractions=[
        lx.data.Extraction(
            extraction_class="case_title",
            extraction_text="董某某诉某出版社劳动争议纠纷案",
            attributes={"case_title": "董某某诉某出版社劳动争议纠纷案"}
        ),
        lx.data.Extraction(
            extraction_class="case_date",
            extraction_text="2023-16-2-490-002",
            attributes={"case_date": "2023-12-02"}
        ),
        lx.data.Extraction(
            extraction_class="case_region",
            extraction_text="北京市东城区人民法院于2002年9月20日作出（2002）东民初字第3023号民事判决：",
            attributes={"case_region": "北京市东城区"}
        ),
        lx.data.Extraction(
            extraction_class="court",
            extraction_text="北京市东城区人民法院于2002年9月20日作出（2002）东民初字第3023号民事判决：",
            attributes={"court": "北京市东城区人民法院"}
        ),
        lx.data.Extraction(
            extraction_class="court",
            extraction_text="一审：北京市东城区人民法院（2002）东民初字第3023号民事判决\n（2002年9月20日）",
            attributes={"court": "北京市东城区人民法院"}
        ),
        lx.data.Extraction(
            extraction_class="cited_laws",
            extraction_text="《最高人民法院关于人民法院审理事业单位人事争议案件若干问题\n的规定》第3条",
            attributes={"cited_laws": '["《最高人民法院关于人民法院审理事业单位人事争议案件若干问题的规定》第3条"]'}
        ),
        lx.data.Extraction(
            extraction_class="case_summary",
            extraction_text="原告某出版社以董某某已辞职，双方已解除人事关系，劳动争议仲\n裁委员会认定事实错误，适用法律不当为由起诉请求：确认董某某\n1989年辞职行为有效，双方不存在劳动关系。\n董某某辩称，某出版社至今没有向其送达解除劳动关系的书面决定\n，档案仍在该社，故同意劳动仲裁裁决，不同意某出版社的诉讼请求。\n法院经审理查明：某出版社成立于1951年，原为国家新闻出版署所\n属的事业单位。某出版社于1998年领取企业法人营业执照，实行自收自\n支，独立核算。2002年1月9日，某出版社同时取得《事业单位法人证书\n》。2009年2月24日，某出版社注销《事业单位法人证书》。2011年2月\n18日，某出版社名称变更为某出版公司。\n董某某自1975年开始在某出版社工作，1989年2月，董某某以借调形\n式至海南某公司工作，借聘期为三年。1989年8月4日，董某某向某出版\n社递交了辞职报告，在报告中表示想获得高级职称证明。同年，某出版\n社负责人在该辞职报告上批示人事部门按规定办理。董某某主张自己在\n提交辞职报告后，时隔几日又分别给社长和人事处打电话，表示自己不\n辞职了。1990年1月，某出版社给董某某开具了高级职称证明。时隔6年\n后，董某某于1996年找到某出版社，要求安排工作。某出版社以董某某\n已于1989年辞职为由未给董某某安排工作。此后，董某某一直向某出版\n社的上级机构某出版总社反映情况。2001年1月，某出版总社出具书面意\n见，同意某出版社对董某某辞职一事的处理。随后，董某某于2001年2月\n向人事部人事仲裁公正厅仲裁办公室提交了仲裁申请书，因得知某出版\n社已领取企业法人营业执照，董某某撤回上述仲裁申请。2002年3月，董\n某某向北京市东城区劳动争议仲裁委员会申请劳动仲裁，要求撤销《关\n于董某某同志辞职的处理意见》，恢复与某出版社的劳动关系。仲裁机\n构支持了董某某的申诉请求，裁决维持某出版社与董某某之间的劳动关\n系。某出版社不服而诉至法院，要求确认董某某1989年辞职行为有效\n，双方不存在劳动关系。",
            attributes={"case_summary": "董某某1989年向某出版社递交辞职报告，后主张已口头撤回，1996年要求恢复工作未果，遂起诉要求维持劳动关系；某出版社反诉要求确认辞职有效。"}
        ),
        lx.data.Extraction(
            extraction_class="judgment_result",
            extraction_text="一、确认董某某于一九八九年八月四日已从某出版社辞职，某出版社于判决生效后十五日内给付董某某人民币一万四千八百零七元整。二、驳回董某某其他诉讼请求。",
            attributes={"judgment_result": "一、确认董某某已于1989年辞职；二、驳回董某某其他诉讼请求。判决维持原判。"}
        ),
        lx.data.Extraction(
            extraction_class="judgment_reason",
            extraction_text="法院生效裁判认为，本案的争议焦点有二，一是本案是否为劳动争\n议纠纷，二是董某某的辞职行为是否成立。\n关于本案是否为劳动争议纠纷的问题。根据某出版社提交的企业法\n人营业执照与事业单位法人证书，1998年至2009年期间，某出版社性质\n上应属于实行企业化管理的事业组织。根据《劳动部办公厅关于实行企\n业化管理的事业组织与职工发生劳动争议有关问题的复函》的规定，实\n行企业化管理的事业组织的全体职工应按照《劳动法》的规定，与所在\n单位通过签订劳动合同建立劳动关系。本案中，董某某的仲裁请求是维\n持与某出版社的劳动关系，某出版社起诉要求确认董某某于1989年已经\n辞职。某出版社与董某某之间的纠纷从1989年递交辞职报告起至2002年\n申请劳动仲裁，时间跨度较长，加之1998年某出版社开始实行企业化管\n理，本案涉及人事关系与劳动关系的衔接和变更问题。此外，最高人民\n法院于2003年8月27日下发《人事争议司法解释》首次将部分人事争议纳\n入人民法院的受案范围。本案董某某申请仲裁、某出版社起诉的时间为\n2002年，结合当时的法律政策，双方无法就人事争议提起民事诉讼。且\n本案二审终审后，董某某于2005年、2007年两次向相关部门申请人事仲\n裁，但均未被受理。综合某出版社性质变更情况及本案纠纷发生的背景\n，原审以劳动争议纠纷受理并作出判决并无不妥。\n关于董某某的辞职行为是否成立的问题。1990年9月8日，人事部发\n布《全民所有制事业单位专业技术人员和管理人员辞职暂行规定》，对\n事业单位人员辞职的流程作出具体规定，该规定自发布之日起试行。董\n某某于1989年8月4日递交辞职报告，某出版社未能及时办理辞职手续。\n因《全民所有制事业单位专业技术人员和管理人员辞职暂行规定》实施\n于1990年9月8日，并不具有溯及既往的效力，故董某某主张某出版社违\n反人事部相关规定，依据不足。本案中，董某某于1989年8月4日向某出\n版社递交书面辞职报告并由时任社长批示按规定办理。董某某虽主张撤\n回辞职继续借调，但未能提交确实充分的依据，同时结合3年借调期满后\n，董某某长期未和某出版社联系的实际情况，可以认为董某某的辞职行\n为已经生效。",
            attributes={"judgment_reason": "结合单位改制情况确认具有劳动争议性质并受理；同时董某某未能提供撤回辞职的充分证据，结合三年内未联络单位之事实，认定其辞职生效。"}
        ),
        lx.data.Extraction(
            extraction_class="key_points",
            extraction_text="关键词 民事 劳动争议 人事争议 受案范围 事业单位转企",
            attributes={"key_points": "民事 劳动争议 人事争议 受案范围 事业单位转企"}
        )
    ]
),
                        lx.data.ExampleData(
    text="""
2026-02-1-214-001
何某英虐待案
——虐待罪中“家庭成员”的范围以及按照公诉案件处理的标准
关键词 刑事 虐待罪 家庭成员 共同生活 没有告诉能力 公诉程序
未成年人
基本案情
2018年9月至2019年11月，被害人唐某某（女，时年5岁）因父母离
异，跟随祖父唐某勇以及唐某勇的未婚同居老伴何某英共同生活。在共
同生活期间，被告人何某英多次以唐某某不听话为由，采取打、咬、掐
、烫等方式虐待唐某某，造成唐某某全身多处损伤。经鉴定，唐某某因
外伤致肢体瘢痕的损伤程度为轻伤二级，右前臂皮肤被咬伤、面部及左
脚前掌皮肤被烫伤及背部皮肤挫伤的损伤程度均为轻微伤。案发后，何
某英取得唐某某父亲唐某金的谅解。
四川省江安县人民检察院因被害人没有能力告诉，以被告人何某英
犯虐待罪向江安县人民法院提起公诉。江安县人民法院于2020年5月25日
作出（2020）川1523刑初28号刑事判决：被告人何某英犯虐待罪，判处
有期徒刑一年六个月。宣判后，没有上诉、抗诉，判决已发生法律效力
。
裁判理由
本案的争议焦点有二：一是对被害人唐某某应否认定为虐待罪中的
“家庭成员”，二是本案应否适用公诉程序，由检察机关提起公诉。
第一，应当认定被害人唐某某为虐待罪中的“家庭成员”。《中华
人民共和国刑法》第二百六十条第一款规定：“虐待家庭成员，情节恶
劣的，处二年以下有期徒刑、拘役或者管制。”关于家庭成员的范围
，《中华人民共和国民法典》第一千零四十五条第三款规定：“配偶、
父母、子女和其他共同生活的近亲属为家庭成员。”对于虐待罪中“家
庭成员”的范围，实践中通常按照民法典上述规定予以把握。但是，随
着经济社会发展，家庭关系出现一些新情况，未婚同居现象增多。基于
此，《最高人民法院、最高人民检察院、公安部、司法部关于依法办理
家庭暴力犯罪案件的意见》（法发〔2015〕4号）明确，家庭暴力犯罪不
仅发生在家庭成员之间，还发生在具有监护、扶养、寄养、同居等关系
的共同生活人员之间。出于根据时代发展和社会变迁妥当适用刑法、最
大限度保护未成年人合法权益的考虑，有必要适度拓展虐待罪中“家庭
成员”的范围。对于由其共同生活的父（母）、祖父（母）等近亲属抚
养，并与该近亲属的未婚同居者处于较为稳定的共同生活状态的未成年
人，应当认定为刑法第二百六十条规定的“家庭成员”。
本案中，被告人何某英与唐某某的祖父为未婚同居关系，在唐某某
由祖父照顾期间，何某英也与唐某某共同生活，处于较为稳定的共同生
活状态，故对于何某英而言，唐某某属于刑法第二百六十条规定的“家
庭成员”。
第二，被害人唐某某没有能力告诉，可由检察机关提起公诉。刑法
第二百六十条第三款规定，虐待家庭成员，情节恶劣的，告诉的才处理
，但被害人没有能力告诉，或者因受到强制、威吓无法告诉的除外。在
虐待未成年人犯罪案件中，未成年人往往因年幼没有能力告诉，因此应
当按照公诉程序处理，由检察机关提起公诉，以切实维护未成年人合法
权益。
本案中，被害人唐某某时年5岁，自然无法行使告诉权利，属于“被
害人没有能力告诉”的情形，由检察机关提起公诉，按照公诉案件处理
，符合法律规定。综上，被告人何某英对共同生活的被害人唐某某，多次采取打、咬
、掐、烫等方式进行虐待，致唐某某受轻伤，情节恶劣，构成虐待罪。
唐某某因年幼没有能力告诉，由检察机关提起公诉，符合法律规定。法
院综合全案情节，依法作出如上判决。
裁判要旨
1.由共同生活的父（母）、祖父（母）等近亲属抚养，并与该近亲
属的未婚同居者处于较为稳定的共同生活状态的未成年人，应当认定为
刑法第二百六十条规定的“家庭成员”。前述近亲属的未婚同居者对未
成年人实施虐待行为，情节恶劣的，依法以虐待罪论处。
2.被虐待的未成年人因年幼无法行使告诉权利，属于虐待罪中“被
害人没有能力告诉”的情形，符合刑法第二百六十条第三款规定的，可
以依法由检察机关提起公诉。
关联索引
《中华人民共和国刑法》第260条第1款、第3款
《中华人民共和国民法典》第1045条第3款
《中华人民共和国反家庭暴力法》第37条
一审： 四川省江安县人民法院（2020）川1523刑初28号刑事判决
（2020年5月25日）""",
    extractions=[
        lx.data.Extraction(
            extraction_class="case_title",
            extraction_text="何某英虐待案",
            attributes={"case_title": "何某英虐待案"}
        ),
        lx.data.Extraction(
            extraction_class="case_date",
            extraction_text="2026-02-1-214-001",
            attributes={"case_date": "2026-02-01"}
        ),
        lx.data.Extraction(
            extraction_class="case_region",
            extraction_text="四川省江安县人民法院",
            attributes={"case_region": "四川省江安县"}
        ),
        lx.data.Extraction(
            extraction_class="court",
            extraction_text="江安县人民法院于2020年5月25日作出（2020）川1523刑初28号刑事判决：",
            attributes={"court": "四川省江安县人民法院"}
        ),
        lx.data.Extraction(
            extraction_class="court",
            extraction_text="一审： 四川省江安县人民法院（2020）川1523刑初28号刑事判决",
            attributes={"court": "四川省江安县人民法院"}
        ),
        lx.data.Extraction(
            extraction_class="cited_laws",
            extraction_text="《中华人民共和国刑法》第260条第1款、第3款\n《中华人民共和国民法典》第1045条第3款\n《中华人民共和国反家庭暴力法》第37条",
            attributes={"cited_laws": '["《中华人民共和国刑法》第260条", "《中华人民共和国民法典》第1045条", "《中华人民共和国反家庭暴力法》第37条"]'}
        ),
        lx.data.Extraction(
            extraction_class="case_summary",
            extraction_text="2018年9月至2019年11月，被害人唐某某（女，时年5岁）因父母离异，跟随祖父唐某勇以及唐某勇的未婚同居老伴何某英共同生活。在共同生活期间，被告人何某英多次以唐某某不听话为由，采取打、咬、掐、烫等方式虐待唐某某，造成唐某某全身多处损伤。",
            attributes={"case_summary": "2018年9月至2019年11月，被害人唐某某因父母离异，跟随祖父及其未婚同居女友何某英生活。何某英多次虐待唐某某致其轻伤二级及多处轻微伤。因被害人年幼无告诉能力，检察机关提起公诉。"}
        ),
        lx.data.Extraction(
            extraction_class="judgment_result",
            extraction_text="被告人何某英犯虐待罪，判处有期徒刑一年六个月。",
            attributes={"judgment_result": "被告人何某英犯虐待罪，判处有期徒刑一年六个月。"}
        ),
        lx.data.Extraction(
            extraction_class="judgment_reason",
            extraction_text="本案中，被告人何某英与唐某某的祖父为未婚同居关系，在唐某某由祖父照顾期间，何某英也与唐某某共同生活，处于较为稳定的共同生活状态，故对于何某英而言，唐某某属于刑法第二百六十条规定的“家庭成员”。",
            attributes={"judgment_reason": "何某英与被害人祖父同居并共同抚养被害人，被害人应认定为何某英的“家庭成员”。由于被害人年幼无告诉能力，检察机关提起公诉符合法律规定。"}
        ),
        lx.data.Extraction(
            extraction_class="key_points",
            extraction_text="关键词 刑事 虐待罪 家庭成员 共同生活 没有告诉能力 公诉程序\n未成年人",
            attributes={"key_points": "刑事 虐待罪 家庭成员 共同生活 没有告诉能力 公诉程序 未成年人"}
        )
    ]
),
                        lx.data.ExampleData(
    text="""
2025-01-2-015-001
梁某玲诉温某雄离婚后财产纠纷案
——离婚后财产纠纷可以适用协议管辖
关键词 民事 离婚后财产 解除 婚姻关系 协议管辖
基本案情
原告梁某玲（女）诉称，其与温某雄原系夫妻关系。2022年11月
17日，双方签订了《离婚协议书》。同日，婚姻登记机关颁发了《离婚
证》。《离婚协议书》第六条约定：“如本协议生效后在履行中发生争
议的，双方应协商解决，协商不成的，任何一方均可向女方所在地人民
法院起诉。”双方离婚后，温某雄拒不配合履行协议中有关财产分割的
约定，梁某玲遂向其住所地法院广东省梅州市梅江区人民法院提起诉讼
，请求判令温某雄履行协议。
广东省梅州市梅江区人民法院认为，本案为离婚后财产纠纷，《离
婚协议书》中虽约定由女方所在地人民法院管辖，但约定管辖适用于合
同或者其他财产权益纠纷。离婚协议系具有人身属性的特殊协议，不符
合合同或者其他财产权益纠纷可以约定管辖的情形，故本案不适用约定
管辖，而应当适用一般地域管辖的规定。被起诉人温某雄的住所地不在
广东省梅州市梅江区，故广东省梅州市梅江区人民法院对此案无管辖权
。
广东省梅州市梅江区人民法院于2023年12月21日作出（2023）粤
1402民初3611号民事裁定：对梁某玲的起诉，不予受理。梁某玲不服
，提起上诉。广东省梅州市中级人民法院于2024年1月25日作出
（2024）粤14民终99号民事裁定：一、撤销广东省梅州市梅江区人民法
院（2023）粤1402民初3611号民事裁定；二、本案指令广东省梅州市梅

江区人民法院立案受理。
裁判理由
本案的争议焦点为：当事人解除婚姻关系后单独就财产问题达成管
辖协议条款是否有效。
《中华人民共和国民事诉讼法》第三十五条规定：“合同或者其他
财产权益纠纷的当事人可以书面协议选择被告住所地、合同履行地、合
同签订地、原告住所地、标的物所在地等与争议有实际联系的地点的人
民法院管辖，但不得违反本法对级别管辖和专属管辖。”《最高人民法
院关于适用〈中华人民共和国民事诉讼法〉的解释》第三十四条规定
：“当事人因同居或者在解除婚姻、收养关系后发生财产争议，约定管
辖的，可以适用民事诉讼法第三十五条规定确定管辖。”根据上述规定
，婚姻关系解除后，当事人单独就财产问题发生的争议可以适用协议管
辖制度。
本案中，梁某玲与温某雄之间的婚姻关系已经解除,梁某玲是因双方
离婚后财产分割问题提起诉讼，故本案系财产争议纠纷。根据双方签订
的《离婚协议书》第六条约定，发生争议可向女方即梁某玲所在地人民
法院起诉，双方选择纠纷由与争议有实际联系的地点的人民法院管辖的
意思表示明确,符合上述法律关于协议管辖范围的规定,且未违反级别管
辖和专属管辖的规定,约定管辖法院明确,应认定有效。故本案应当依据
当事人的约定确定管辖。鉴于梁某玲住所地在广东省梅州市梅江区,本案
应当由广东省梅州市梅江区人民法院管辖。
裁判要旨
解除婚姻关系后单独就财产分割问题发生的争议可以适用协议管辖
。离婚后财产纠纷涉及的财产，虽然均为婚姻关系存续期间的夫妻共同
财产，但在婚姻关系解除后，如仅涉及对分割财产问题产生争议，当事

人可以协议选择与争议有实际联系的地点，包括原告住所地、财产所在
地等法院管辖。
关联索引
《中华人民共和国民事诉讼法》（2021年修正）第35条
《最高人民法院关于适用〈中华人民共和国民事诉讼法〉的解释》
（法释〔2022〕11号）第34条
一审： 广东省梅州市梅江区人民法院（2023）粤1402民初3611号裁
定（2023年12月21日）
二审：广东省梅州市中级人民法院（2024）粤14民终99号裁定
（2024年1月25日）""",
    extractions=[
        lx.data.Extraction(
            extraction_class="case_title",
            extraction_text="梁某玲诉温某雄离婚后财产纠纷案",
            attributes={"case_title": "梁某玲诉温某雄离婚后财产纠纷案"}
        ),
        lx.data.Extraction(
            extraction_class="case_date",
            extraction_text="2025-01-2-015-001",
            attributes={"case_date": "2025-01-02"}
        ),
        lx.data.Extraction(
            extraction_class="case_region",
            extraction_text="广东省梅州市梅江区",
            attributes={"case_region": "广东省梅州市"}
        ),
        lx.data.Extraction(
            extraction_class="court",
            extraction_text="广东省梅州市中级人民法院",
            attributes={"court": "广东省梅州市中级人民法院"}
        ),
        lx.data.Extraction(
            extraction_class="court",
            extraction_text="一审： 广东省梅州市梅江区人民法院（2023）粤1402民初3611号裁定（2023年12月21日）",
            attributes={"court": "广东省梅州市中级人民法院"}
        ),
        lx.data.Extraction(
            extraction_class="cited_laws",
            extraction_text="《中华人民共和国民事诉讼法》（2021年修正）第35条\n《最高人民法院关于适用〈中华人民共和国民事诉讼法〉的解释》\n（法释〔2022〕11号）第34条",
            attributes={"cited_laws": '["《中华人民共和国民事诉讼法》第35条", "《最高人民法院关于适用〈中华人民共和国民事诉讼法〉的解释》第34条"]'}
        ),
        lx.data.Extraction(
            extraction_class="case_summary",
            extraction_text="原告梁某玲（女）诉称，其与温某雄原系夫妻关系。2022年11月\n17日，双方签订了《离婚协议书》。同日，婚姻登记机关颁发了《离婚\n证》。《离婚协议书》第六条约定：“如本协议生效后在履行中发生争\n议的，双方应协商解决，协商不成的，任何一方均可向女方所在地人民\n法院起诉。”双方离婚后，温某雄拒不配合履行协议中有关财产分割的\n约定，梁某玲遂向其住所地法院广东省梅州市梅江区人民法院提起诉讼\n，请求判令温某雄履行协议。\n广东省梅州市梅江区人民法院认为，本案为离婚后财产纠纷，《离\n婚协议书》中虽约定由女方所在地人民法院管辖，但约定管辖适用于合\n同或者其他财产权益纠纷。离婚协议系具有人身属性的特殊协议，不符\n合合同或者其他财产权益纠纷可以约定管辖的情形，故本案不适用约定\n管辖，而应当适用一般地域管辖的规定。被起诉人温某雄的住所地不在\n广东省梅州市梅江区，故广东省梅州市梅江区人民法院对此案无管辖权\n。\n广东省梅州市梅江区人民法院于2023年12月21日作出（2023）粤\n1402民初3611号民事裁定：对梁某玲的起诉，不予受理。",
            attributes={"case_summary": "梁某玲与温某雄协议离婚后单就财产分割问题产生争议，梁某玲按《离婚协议书》中的管辖条款向女方所在地法院提起诉讼。一审法院以该协议具人身属性为由裁定不予受理，梁某玲上诉。"}
        ),
        lx.data.Extraction(
            extraction_class="judgment_result",
            extraction_text="一、撤销广东省梅州市梅江区人民法院（2023）粤1402民初3611号民事裁定；二、本案指令广东省梅州市梅江区人民法院立案受理。",
            attributes={"judgment_result": "一审认定离婚协议不适用约定管辖，被告不在辖区内，法院对此案无管辖权，裁定不予受理。"}
        ),
        lx.data.Extraction(
            extraction_class="judgment_reason",
            extraction_text="本案的争议焦点为：当事人解除婚姻关系后单独就财产问题达成管辖协议条款是否有效。\n《中华人民共和国民事诉讼法》第三十五条规定：“合同或者其他财产权益纠纷的当事人可以书面协议选择被告住所地、合同履行地、合同签订地、原告住所地、标的物所在地等与争议有实际联系的地点的人民法院管辖，但不得违反本法对级别管辖和专属管辖。”《最高人民法院关于适用〈中华人民共和国民事诉讼法〉的解释》第三十四条规定：“当事人因同居或者在解除婚姻、收养关系后发生财产争议，约定管辖的，可以适用民事诉讼法第三十五条规定确定管辖。”根据上述规定，婚姻关系解除后，当事人单独就财产问题发生的争议可以适用协议管辖制度。\n本案中，梁某玲与温某雄之间的婚姻关系已经解除,梁某玲是因双方离婚后财产分割问题提起诉讼，故本案系财产争议纠纷。根据双方签订的《离婚协议书》第六条约定，发生争议可向女方即梁某玲所在地人民法院起诉，双方选择纠纷由与争议有实际联系的地点的人民法院管辖的意思表示明确,符合上述法律关于协议管辖范围的规定,且未违反级别管辖和专属管辖的规定,约定管辖法院明确,应认定有效。故本案应当依据当事人的约定确定管辖。鉴于梁某玲住所地在广东省梅州市梅江区,本案应当由广东省梅州市梅江区人民法院管辖。",
            attributes={"judgment_reason": "双方婚姻关系已解除，本案系单就离婚后财产分割问题提起的财产争议纠纷。协议约定的管辖法院符合《民事诉讼法》关于协议管辖的范围规定，并未违反级别和专属管辖规定，因此协议管辖条款有效。"}
        ),
        lx.data.Extraction(
            extraction_class="key_points",
            extraction_text="关键词 民事 离婚后财产 解除 婚姻关系 协议管辖",
            attributes={"key_points": "民事 离婚后财产 解除 婚姻关系 协议管辖"}
        )
    ]
),
            lx.data.ExampleData(
    text="""

2023-09-2-158-017
李某诉吉林市某农副产品开发有限公司等著作权侵权纠纷案
——未经许可将作品作为商标使用侵害著作权的损害赔偿计算
关键词 民事 著作权侵权 损害赔偿 商标使用 许可费用
基本案情
李某创作完成“鹿献灵芝”“为鹿疗伤”“人鹿和谐”等连环画形
式的系列剪纸作品，取名为《老爷岭的传说》，后改名为《老爷岭的故
事》。经李某授权，该系列剪纸作品在吉林珲春高速公路旁形成剪纸石
雕作品，石雕上刻有“李某剪纸”字样。该系列剪纸作品在2009年2月出
版的《剪纸画吉林》、2012年2月出版的《剪纸画关东》《中华剪纸》等
多种书刊上进行过公开发表。吉林市某农副产品开发有限公司设立于
2002年2月，经营范围为大米加工等。2012年6月13日，吉林市某农副产
品开发有限公司与南关区某设计工作室签订《本源设计项目委托合同书
》，约定的设计项目内容为 lkg塑料袋、400 kg抽真空袋、500 kg站立袋、
5kg手提普通米袋、5 kg手提绿色米袋、5 kg有机米袋，设计费为1.5万元
。合同签订后，南关区某设计工作室向吉林市某农副产品开发有限公司
提供了产品外包装的设计图，吉林市某农副产品开发有限公司如约支付
设计费。2012年10月，吉林市某农副产品开发有限公司申请将该设计图
中的“人鹿图案”注册为商标，并于2014年3月14日取得商标注册证，吉
林市某农副产品开发有限公司将该商标用于多种粮食产品的外包装上进
行销售经营。李某诉讼主张吉林市某农副产品开发有限公司停止侵权、
消除影响、赔礼道歉、赔偿210万元损失并支付20万元律师费。
吉林省吉林市中级人民法院于2016年5月5日作出（2015）吉中民二知
初字第52号民事判决：吉林市某农副产品开发有限公司应立即停止侵

权行为、消除影响、赔礼道歉；赔偿李某经济损失8万元（含合理维权支
出）。李某不服，提起上诉。吉林省高级人民法院于2016年12月30日作
出（2016）吉民终545号民事判决，驳回上诉、维持原判。李某不服，向
最高人民法院申请再审。最高人民法院于2017年9月26日作出（2017）最
高法民申2348号民事裁定，驳回了李某的再审申请。
裁判理由
法院生效裁判认为：本案争议焦点是：本案判决的赔偿额是否有事
实和法律依据。
《中华人民共和国著作权法》第四十九条规定，侵犯著作权或者与
著作权有关的权利的，侵权人应当按照权利人的实际损失给予赔偿；实
际损失难以计算的，可以按照侵权人的违法所得给予赔偿。赔偿数额还
应当包括权利人为制止侵权行为所支付的合理开支。权利人的实际损失
或者侵权人的违法所得不能确定的，由人民法院根据侵权行为的情节
，判决给予五十万元以下的赔偿。
考察侵害作品著作权的损害，应着眼于权利人因作品被侵权使用遭
受的损失，或者侵权人因侵权使用作品而增加的收益。由于作品的使用
方式多样，所涉及的著作权权利亦不相同，因此，就同一件作品而言
，不同的侵权行为，可以采取多种方式计算。如根据权利人因侵权所造
成复制品发行减少量或者侵权复制品销售量与权利人发行该复制品单位
利润乘积计算；以报刊、图书出版或者类似方式侵权的，参照国家有关
稿酬的规定计算；参照合理的许可使用费计算等。
本案所涉作品为剪纸美术作品。就美术作品而言，如果侵权行为系
出版行为，可按照权利人因此遭受的稿酬损失计算；如果侵权行为系复
制美术品的方式，一般应按照侵权人的市场利润即复制品数量与单位利
润计算，因为作品是侵权复制品定价的核心，侵权复制品的获利应当视

为来自作品的全部贡献或主要贡献。如果是将美术作品用于宣传其他商
品，如用于广告、装饰装潢等，商品利润与作品价值之间并无直接的因
果关系，不宜将商品利润直接作为作品损失。侵权行为的收益往往表现
在未支付应当支付的成本，即著作权许可费用。
本案所涉侵权行为系擅自将他人作品用作商标的行为。作品被用作
商标，一般有两种情况，一种是通过许可使用合同获得已有作品的授权
，一种是自行或委托他人创作。在使用许可合同中，作品的独创性可能
对商标显著性有影响，作品的知名度对商标的知名度有贡献，均可作为
作品价值的参考要素，体现在许可使用费中。如果是自行创作或委托创
作，一般分为两阶段，商标设计制作和商标交付使用阶段。在商标设计
制作阶段，设计人使用的是作品，其通过创作作品获得相应报酬，因此
商标设计费是作品被用作商标的对价。在商标使用过程中，使用人主要
使用的是商标而非作品，其产生的价值应当主要属于商标价值而非作品
价值了。无论上述哪种情况，对于作品权利人而言，当作品被他人擅自
用作商标，丧失的既非出版稿酬损失，也非美术品损失，而是许可他人
用作商标的费用与机会损失。因此，二审法院认为，不宜以标有商标的
包装袋数量作为侵权复制品的数量，应以作品授权许可费用作为标准计
算本案损失，符合法律规定。
本案当事人并未授权他人将作品用作商标，未举证证明许可使用费
的数额，也未举证类似作品的授权情况。依据著作权法的规定，一审、
二审法院据此认为本案属于损失和违法所得均无法确定的情况，符合法
律规定。
依据《最高人民法院关于审理著作权民事纠纷案件适用法律若干问
题的解释》第二十五条第二款规定，人民法院在确定赔偿数额时，应当
考虑作品类型、合理使用费、侵权行为性质、后果等情节综合确定。本

案中，作品被复制侵权的第一使用人系南关区某设计工作室，其通过为
吉林市某农副产品开发有限公司设计商标获取的费用，是其使用涉案作
品获得的直接利益，可以作为衡量作品损失的参考标准。一般认为，侵
权复制者的成本较低，其授权作品的价格可能低于合法授权作品的价格
，因此，可在参考该费用的基础上，考虑侵权行为的性质、影响等因素
，乘以适当倍数，进行计算。有鉴于此，一审、二审法院综合考虑涉案
作品价值、独创性程度、侵权情节、主观过错程度及诉讼合理支出等因
素，酌定赔偿数额为8万元并无不妥，应予维持。李某关于赔偿数额没有
事实和法律依据的申请再审理由不能成立，法院不予支持。
裁判要旨
1.考察侵害作品著作权的损害，应着眼于权利人因作品被侵权使用
遭受的损失，或者侵权人因侵权使用作品而增加的收益。不同的侵权行
为，可以采取多种方式计算。如根据权利人因侵权所造成复制品发行减
少量或者侵权复制品销售量与权利人发行该复制品单位利润乘积计算z
；以报刊、图书出版或者类似方式侵权的，参照国家有关稿酬的规定计
算；参照合理的许可使用费计算等。
2.侵权复制者的成本一般较低，其授权作品的价格可能低于合法授
权作品的价格，因此，可在参考该费用的基础上，考虑侵权行为的性质
、影响等因素予以确认。
关联索引
《中华人民共和国著作权法》（2020年修正）第54条（本案适用的
是2010年4月1日施行的《中华人民共和国著作权法》第49条）
一审：吉林省吉林市中级人民法院（2015）吉中民二知初字第52号
民事判决（2016年5月5日）
二审：吉林省高级人民法院（2016）吉民终545号民事判决（2016年

12月30日）
申请再审：最高人民法院（2017）最高法民申2348号民事裁定
（2017年9月26日）

本案例文本已于2024年2月26日作出调整""",
    extractions=[
        lx.data.Extraction(
            extraction_class="case_title",
            extraction_text="李某诉吉林市某农副产品开发有限公司等著作权侵权纠纷案",
            attributes={"case_title": "李某诉吉林市某农副产品开发有限公司等著作权侵权纠纷案"}
        ),
        lx.data.Extraction(
            extraction_class="case_date",
            extraction_text="2023-09-2-158-017",
            attributes={"case_date": "2023-09-02"}
        ),
        lx.data.Extraction(
            extraction_class="case_region",
            extraction_text="吉林省吉林市中级人民法院于2016年5月5日作出（2015）吉中民二知初字第52号民事判决：",
            attributes={"case_region": "吉林省吉林市"}
        ),
        lx.data.Extraction(
            extraction_class="court",
            extraction_text="吉林省吉林市中级人民法院于2016年5月5日作出（2015）吉中民二知初字第52号民事判决：",
            attributes={"court": "吉林市中级人民法院"}
        ),
        lx.data.Extraction(
            extraction_class="court",
            extraction_text="一审：吉林省吉林市中级人民法院（2015）吉中民二知初字第52号民事判决（2016年5月5日）",
            attributes={"court": "吉林市中级人民法院"}
        ),
        lx.data.Extraction(
            extraction_class="cited_laws",
            extraction_text="《中华人民共和国著作权法》（2020年修正）第54条（本案适用的是2010年4月1日施行的《中华人民共和国著作权法》第49条）",
            attributes={"cited_laws": '["《中华人民共和国著作权法》第54条"]'}
        ),
        lx.data.Extraction(
            extraction_class="case_summary",
            extraction_text="李某创作完成“鹿献灵芝”“为鹿疗伤”“人鹿和谐”等连环画形式的系列剪纸作品，取名为《老爷岭的传说》，后改名为《老爷岭的故事》。经李某授权，该系列剪纸作品在吉林珲春高速公路旁形成剪纸石雕作品，石雕上刻有“李某剪纸”字样。该系列剪纸作品在2009年2月出版的《剪纸画吉林》、2012年2月出版的《剪纸画关东》《中华剪纸》等多种书刊上进行过公开发表。吉林市某农副产品开发有限公司设立于2002年2月，经营范围为大米加工等。2012年6月13日，吉林市某农副产品开发有限公司与南关区某设计工作室签订《本源设计项目委托合同书》，约定的设计项目内容为 lkg塑料袋、400 kg抽真空袋、500 kg站立袋、5kg手提普通米袋、5 kg手提绿色米袋、5 kg有机米袋，设计费为1.5万元。合同签订后，南关区某设计工作室向吉林市某农副产品开发有限公司提供了产品外包装的设计图，吉林市某农副产品开发有限公司如约支付设计费。2012年10月，吉林市某农副产品开发有限公司申请将该设计图中的“人鹿图案”注册为商标，并于2014年3月14日取得商标注册证，吉林市某农副产品开发有限公司将该商标用于多种粮食产品的外包装上进行销售经营。",
            attributes={"case_summary": "李某创作完成系列剪纸作品并公开。吉林市某农副产品公司委托设计工作室为其产品设计包装并申请包含作品图案的商标，在销售中使用。李某起诉主张停止侵权并索赔损失。"}
        ),
        lx.data.Extraction(
            extraction_class="judgment_result",
            extraction_text="吉林市某农副产品开发有限公司应立即停止侵权行为、消除影响、赔礼道歉；赔偿李某经济损失8万元（含合理维权支出）。",
            attributes={"judgment_result": "判决立即停止侵权行为、消除影响、赔礼道歉；赔偿李某经济损失8万元。驳回再审申请。"}
        ),
        lx.data.Extraction(
            extraction_class="judgment_reason",
            extraction_text="法院生效裁判认为：本案争议焦点是：本案判决的赔偿额是否有事实和法律依据。\n《中华人民共和国著作权法》第四十九条规定，侵犯著作权或者与著作权有关的权利的，侵权人应当按照权利人的实际损失给予赔偿；实际损失难以计算的，可以按照侵权人的违法所得给予赔偿。赔偿数额还应当包括权利人为制止侵权行为所支付的合理开支。权利人的实际损失或者侵权人的违法所得不能确定的，由人民法院根据侵权行为的情节，判决给予五十万元以下的赔偿。\n考察侵害作品著作权的损害，应着眼于权利人因作品被侵权使用遭受的损失，或者侵权人因侵权使用作品而增加的收益。由于作品的使用方式多样，所涉及的著作权权利亦不相同，因此，就同一件作品而言，不同的侵权行为，可以采取多种方式计算。如根据权利人因侵权所造成复制品发行减少量或者侵权复制品销售量与权利人发行该复制品单位利润乘积计算；以报刊、图书出版或者类似方式侵权的，参照国家有关稿酬的规定计算；参照合理的许可使用费计算等。\n本案所涉作品为剪纸美术作品。就美术作品而言，如果侵权行为系出版行为，可按照权利人因此遭受的稿酬损失计算；如果侵权行为系复制美术品的方式，一般应按照侵权人的市场利润即复制品数量与单位利润计算，因为作品是侵权复制品定价的核心，侵权复制品的获利应当视为来自作品的全部贡献或主要贡献。如果是将美术作品用于宣传其他商品，如用于广告、装饰装潢等，商品利润与作品价值之间并无直接的因果关系，不宜将商品利润直接作为作品损失。侵权行为的收益往往表现在未支付应当支付的成本，即著作权许可费用。\n本案所涉侵权行为系擅自将他人作品用作商标的行为。作品被用作商标，一般有两种情况，一种是通过许可使用合同获得已有作品的授权，一种是自行或委托他人创作。在使用许可合同中，作品的独创性可能对商标显著性有影响，作品的知名度对商标的知名度有贡献，均可作为作品价值的参考要素，体现在许可使用费中。如果是自行创作或委托创作，一般分为两阶段，商标设计制作和商标交付使用阶段。在商标设计制作阶段，设计人使用的是作品，其通过创作作品获得相应报酬，因此商标设计费是作品被用作商标的对价。在商标使用过程中，使用人主要使用的是商标而非作品，其产生的价值应当主要属于商标价值而非作品价值了。无论上述哪种情况，对于作品权利人而言，当作品被他人擅自用作商标，丧失的既非出版稿酬损失，也非美术品损失，而是许可他人用作商标的费用与机会损失。因此，二审法院认为，不宜以标有商标的包装袋数量作为侵权复制品的数量，应以作品授权许可费用作为标准计算本案损失，符合法律规定。\n本案当事人并未授权他人将作品用作商标，未举证证明许可使用费的数额，也未举证类似作品的授权情况。依据著作权法的规定，一审、二审法院据此认为本案属于损失和违法所得均无法确定的情况，符合法律规定。\n依据《最高人民法院关于审理著作权民事纠纷案件适用法律若干问题的解释》第二十五条第二款规定，人民法院在确定赔偿数额时，应当考虑作品类型、合理使用费、侵权行为性质、后果等情节综合确定。本案中，作品被复制侵权的第一使用人系南关区某设计工作室，其通过为吉林市某农副产品开发有限公司设计商标获取的费用，是其使用涉案作品获得的直接利益，可以作为衡量作品损失的参考标准。一般认为，侵权复制者的成本较低，其授权作品的价格可能低于合法授权作品的价格，因此，可在参考该费用的基础上，考虑侵权行为的性质、影响等因素，乘以适当倍数，进行计算。有鉴于此，一审、二审法院综合考虑涉案作品价值、独创性程度、侵权情节、主观过错程度及诉讼合理支出等因素，酌定赔偿数额为8万元并无不妥，应予维持。李某关于赔偿数额没有事实和法律依据的申请再审理由不能成立，法院不予支持。",
            attributes={"judgment_reason": "擅自将他人美术作品作为商标使用，应以作品授权许可费用作为标准计算损失。本案中损失和违法所得均难以确定，法院参考设计费收益并综合考虑侵权情节酌定赔偿数额并无不妥。"}
        ),
        lx.data.Extraction(
            extraction_class="key_points",
            extraction_text="关键词 民事 著作权侵权 损害赔偿 商标使用 许可费用",
            attributes={"key_points": "民事 著作权侵权 损害赔偿 商标使用 许可费用"}
        )
    ]
)
        ]
    
    def read_csv_texts(self, csv_path, text_column=1, max_lines=None):
        """读取CSV文件中的文本数据"""
        texts = []
        ids = []
        
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    if len(row) > text_column and row[text_column].strip():
                        texts.append(row[text_column].strip())
                        ids.append(row[0].strip() if row[0].strip() else f"doc_{i+1}")
                    if max_lines is not None and len(texts) >= max_lines:
                        self.log_message(f"达到最大行数限制: {max_lines}")
                        break
            self.log_message(f"成功读取 {len(texts)} 个文档")
        except Exception as e:
            self.log_message(f"读取CSV文件时出错: {e}")
        
        return ids, texts
    
    def run_extraction(self):
        """运行批量提取任务"""
        try:
            # 获取参数
            provider = self.api_provider_var.get()
            model_id = self.model_var.get()
            api_key = self.api_key_var.get().strip()
            csv_path = self.input_path_var.get()
            jsonl_dir = self.jsonl_path_var.get()
            html_dir = self.html_path_var.get()
            text_column = int(self.text_column_var.get())
            
            max_lines = None
            if self.max_lines_var.get():
                max_lines = int(self.max_lines_var.get())
            
            delay = float(self.delay_var.get())
            
            # 创建输出目录
            for directory in [jsonl_dir, html_dir]:
                os.makedirs(directory, exist_ok=True)
                self.log_message(f"确保目录存在: {directory}")
            
            # 读取CSV文件
            ids, texts = self.read_csv_texts(csv_path, text_column, max_lines)
            
            if not texts:
                self.log_message("错误: 没有读取到文本数据")
                self.stop_processing()
                return
            
            # 配置模型
            self.log_message(f"正在配置{provider}模型: {model_id}")
            try:
                config = factory.ModelConfig(
                    model_id=model_id,
                    provider="OpenAiLanguageModel",
                    provider_kwargs={
                        'api_key': api_key,
                        'base_url': self.api_endpoints[provider]
                    }
                )
                
                model = factory.create_model(config)
                self.log_message(f"✓ 成功创建{provider}模型: {model_id}")
            except Exception as e:
                self.log_message(f"✗ 创建模型时出错: {e}")
                self.stop_processing()
                return
            
            # 定义提取提示
                    # 定义提取提示
            prompt = textwrap.dedent("""
                Extract legal case information from Chinese judicial documents.
                You must extract exactly 9 core attributes for each case. 
                Use exact text from the source for the 'extraction_text', and provide formatted or summarized text for the 'attributes' as shown in the examples.
                Do not overlap extractions.

                Focus on extracting the following 9 attributes exactly once per document:
                - case_title: The official name/title of the court case.
                - case_date: The date associated with the case, strictly formatted as YYYY-MM-DD.
                - case_region: The geographic region (province/city/district) of the case.
                - court: The full name of the court handling the case.
                - cited_laws: The specific legal statutes, articles, and paragraphs cited.
                - case_summary: A summary of the fundamental facts and background (基本案情).
                - judgment_result: The final ruling or decision of the court (裁判结果).
                - judgment_reason: The logical reasoning and rationale behind the court's decision (裁判理由).
                - key_points: The keywords or main judicial principles (关键词/裁判要旨).
            """)
            
            # 获取示例数据
            material_examples = self.get_material_examples()
            
            # 处理每个文档
            success_count = 0
            fail_count = 0
            
            for i, (doc_id, text) in enumerate(zip(ids, texts)):
                if not self.processing:
                    self.log_message("处理被用户中断")
                    break
                
                self.log_message(f"处理文档 {i+1}/{len(texts)}: ID={doc_id}")
                full_text = f"{doc_id}, {text}"
                
                try:
                    result = extract(
                        text_or_documents=full_text,
                        prompt_description=prompt,
                        examples=material_examples,
                        model=model,
                        fence_output=False,
                        use_schema_constraints=False,
                        extraction_passes=1,
                        max_workers=1,
                        max_char_buffer=1000
                    )
                    
                    # 保存 JSONL 文件
                    jsonl_filename = f"material_extraction_{doc_id}.jsonl"
                    jsonl_filepath = os.path.join(jsonl_dir, jsonl_filename)
                    
                    lx.io.save_annotated_documents(
                        [result], 
                        output_name=jsonl_filename, 
                        output_dir=jsonl_dir
                    )
                    
                    self.log_message(f"✓ JSONL文件已保存: {jsonl_filename}")
                    
                    # 生成并保存 HTML 文件
                    if os.path.exists(jsonl_filepath):
                        try:
                            html_content = lx.visualize(jsonl_filepath)
                            html_filename = f"material_viz_{doc_id}.html"
                            html_filepath = os.path.join(html_dir, html_filename)
                            
                            with open(html_filepath, "w", encoding="utf-8") as f:
                                if hasattr(html_content, 'data'):
                                    f.write(html_content.data)
                                elif hasattr(html_content, '__str__'):
                                    f.write(str(html_content))
                                else:
                                    f.write(html_content)
                            
                            self.log_message(f"✓ HTML文件已保存: {html_filename}")
                            success_count += 1
                            
                        except Exception as e:
                            self.log_message(f"✗ 生成HTML时出错: {e}")
                            fail_count += 1
                    else:
                        self.log_message(f"✗ JSONL文件不存在: {jsonl_filename}")
                        fail_count += 1
                        
                except Exception as e:
                    self.log_message(f"✗ 处理文档 {doc_id} 失败: {e}")
                    fail_count += 1
                
                # 添加延迟，避免API限速
                if i < len(texts) - 1 and self.processing and delay > 0:
                    time.sleep(delay)
            
            # 生成处理摘要
            summary_file = os.path.join(os.path.dirname(jsonl_dir), "processing_summary.txt")
            try:
                with open(summary_file, "w", encoding="utf-8") as f:
                    f.write("材料科学文本批量处理摘要\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"处理时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"API提供商: {provider}\n")
                    f.write(f"模型: {model_id}\n")
                    f.write(f"总文档数: {len(texts)}\n")
                    f.write(f"成功处理: {success_count}\n")
                    f.write(f"处理失败: {fail_count}\n")
                    f.write(f"输入文件: {csv_path}\n")
                    f.write(f"JSONL目录: {jsonl_dir}\n")
                    f.write(f"HTML目录: {html_dir}\n")
                    f.write(f"请求延迟: {delay}秒\n")
                
                self.log_message(f"✓ 处理摘要已保存: {summary_file}")
            except Exception as e:
                self.log_message(f"✗ 保存处理摘要时出错: {e}")
            
            self.log_message("\n" + "=" * 60)
            self.log_message("批量处理完成！")
            self.log_message("=" * 60)
            self.log_message(f"处理摘要:")
            self.log_message(f"  API提供商: {provider}")
            self.log_message(f"  模型: {model_id}")
            self.log_message(f"  总文档数: {len(texts)}")
            self.log_message(f"  成功处理: {success_count}")
            self.log_message(f"  处理失败: {fail_count}")
            
        except Exception as e:
            self.log_message(f"处理过程中出错: {e}")
            import traceback
            self.log_message(traceback.format_exc())
        
        finally:
            self.stop_processing()
            self.progress_bar.stop()

def main():
    """主函数"""
    root = tk.Tk()
    app = MaterialScienceExtractorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()