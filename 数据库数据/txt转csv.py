from __future__ import annotations

import argparse
import csv
from pathlib import Path


def txt_folder_to_csv(input_dir: Path, output_csv: Path, encoding: str = "utf-8") -> int:
	"""将 input_dir 下所有 txt 合并为一个 CSV。

	每个 txt 对应一行，列为：
	- 文件名
	- 文本内容
	"""
	txt_files = sorted(input_dir.glob("*.txt"))

	if not txt_files:
		print(f"未找到 txt 文件: {input_dir}")
		return 0

	output_csv.parent.mkdir(parents=True, exist_ok=True)

	with output_csv.open("w", newline="", encoding="utf-8-sig") as f:
		writer = csv.writer(f)
		writer.writerow(["文件名", "文本内容"])

		count = 0
		for txt_path in txt_files:
			try:
				content = txt_path.read_text(encoding=encoding)
			except UnicodeDecodeError:
				# Fallback for common Windows txt encoding.
				content = txt_path.read_text(encoding="gbk", errors="replace")

			writer.writerow([txt_path.name, content])
			count += 1

	print(f"转换完成，共处理 {count} 个 txt 文件。")
	print(f"输出文件: {output_csv}")
	return count


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		description="将文件夹中的多个 txt 文件合并写入一个 CSV（每个 txt 一行）"
	)
	parser.add_argument(
		"-i",
		"--input-dir",
		help="txt 文件所在文件夹路径，不填则运行时输入",
	)
	parser.add_argument(
		"-o",
		"--output-csv",
		help="输出 CSV 文件路径，不填则默认输出到输入目录下 merged_output.csv",
	)
	parser.add_argument(
		"--encoding",
		default="utf-8",
		help="读取 txt 的编码，默认 utf-8（失败会自动尝试 gbk）",
	)
	return parser


def main() -> None:
	parser = build_parser()
	args = parser.parse_args()

	input_dir_raw = args.input_dir or input("请输入 txt 文件夹路径: ").strip()
	input_dir = Path(input_dir_raw)

	if not input_dir.exists() or not input_dir.is_dir():
		raise SystemExit(f"无效文件夹路径: {input_dir}")

	output_csv = Path(args.output_csv) if args.output_csv else input_dir / "merged_output.csv"
	txt_folder_to_csv(input_dir=input_dir, output_csv=output_csv, encoding=args.encoding)


if __name__ == "__main__":
	main()
