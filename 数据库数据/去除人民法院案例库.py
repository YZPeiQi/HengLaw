import re
import sys
from pathlib import Path


def clean_court_library_text(content):
    """
    清理文本中的“人民法院案例库”相关字样，并返回清理后的文本
    """
    # 定义要移除的模式（支持可能的变体）
    patterns = [
        r'人民法院案例库',           # 标准形式
        r'人民法院\s*案例库',        # 中间有空格
        r'人民法院[·\-]案例库',      # 中间有分隔符
        r'“人民法院案例库”',         # 带中文引号
        r'「人民法院案例库」',       # 带直角引号
        r'<人民法院案例库>',          # 带尖括号
        r'【人民法院案例库】',        # 带方括号
        r'第\s*[一二三四五六七八九十百千万0-9]+\s*页',  # 第X页（包含中文数字或阿拉伯数字）
    ]

    # 组合所有模式
    combined_pattern = '|'.join(patterns)

    # 移除匹配的文本（替换为空字符串）
    cleaned_content = re.sub(combined_pattern, '', content, flags=re.UNICODE)

    # 可选：清理多余的空白（连续空行/空格等）
    # 将多个连续换行减少为最多两个
    cleaned_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_content)
    # 移除行首行尾多余空格（但保留缩进）
    cleaned_content = '\n'.join(line.rstrip() for line in cleaned_content.splitlines())

    return cleaned_content

def remove_court_library_text(input_file, output_file=None, inplace=False, verbose=True):
    """
    从txt文件中移除所有出现的“人民法院案例库”文字
    
    参数:
        input_file: 输入文件路径
        output_file: 输出文件路径（可选，默认在输入文件名后加'_cleaned'）
        inplace: 是否直接修改原文件（为True时忽略output_file）
        verbose: 是否打印处理详情
    """
    try:
        # 读取文件内容
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        cleaned_content = clean_court_library_text(content)
        
        # 确定输出路径
        if inplace:
            output_path = Path(input_file)
        else:
            input_path = Path(input_file)
            if output_file:
                output_path = Path(output_file)
            else:
                output_path = input_path.with_stem(input_path.stem + '_cleaned')
        
        # 写入清理后的内容
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)

        # 输出统计信息
        original_len = len(content)
        cleaned_len = len(cleaned_content)
        removed_count = original_len - cleaned_len

        if verbose:
            print("处理完成！")
            if inplace:
                print(f"已直接修改原文件: {output_path}")
            else:
                print(f"清理后的文件已保存至: {output_path}")
            print(f"原始文本长度: {original_len} 字符")
            print(f"清理后长度: {cleaned_len} 字符")
            print(f"共移除 {removed_count} 字符")
        
        return {
            'input_file': str(input_file),
            'output_file': str(output_path),
            'original_len': original_len,
            'cleaned_len': cleaned_len,
            'removed_count': removed_count,
        }
        
    except FileNotFoundError:
        print(f"错误：文件 '{input_file}' 不存在")
        sys.exit(1)
    except Exception as e:
        print(f"处理过程中发生错误: {e}")
        sys.exit(1)


def process_txt_folder(input_dir, output_dir=None, inplace=False):
    """
    批量处理文件夹中的所有txt文件

    参数:
        input_dir: 输入文件夹路径
        output_dir: 输出文件夹路径（inplace=False时可选）
        inplace: 是否直接覆盖原文件
    """
    input_path = Path(input_dir)
    if not input_path.exists() or not input_path.is_dir():
        print(f"错误：文件夹 '{input_dir}' 不存在")
        sys.exit(1)

    txt_files = sorted([p for p in input_path.iterdir() if p.is_file() and p.suffix.lower() == '.txt'])
    if not txt_files:
        print(f"提示：文件夹 '{input_dir}' 中没有找到txt文件")
        return

    if inplace:
        output_path = input_path
    else:
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = input_path.with_name(input_path.name + '_cleaned')
        output_path.mkdir(parents=True, exist_ok=True)

    print("=" * 50)
    print(f"开始批量处理，共 {len(txt_files)} 个txt文件")
    print(f"输入文件夹: {input_path}")
    if inplace:
        print("输出方式: 直接覆盖原文件")
    else:
        print(f"输出文件夹: {output_path}")
    print("=" * 50)

    total_removed = 0
    success_count = 0
    failed_files = []

    for txt_file in txt_files:
        try:
            target_file = txt_file if inplace else output_path / txt_file.name
            result = remove_court_library_text(
                txt_file,
                output_file=target_file,
                inplace=inplace,
                verbose=False,
            )
            total_removed += result['removed_count']
            success_count += 1
            print(f"[成功] {txt_file.name} -> 共移除 {result['removed_count']} 字符")
        except Exception as e:
            failed_files.append((txt_file.name, str(e)))
            print(f"[失败] {txt_file.name} -> {e}")

    print("\n" + "=" * 50)
    print("批量处理完成")
    print(f"成功: {success_count}/{len(txt_files)}")
    print(f"总计移除字符: {total_removed}")
    if failed_files:
        print(f"失败文件数: {len(failed_files)}")
        for file_name, error in failed_files:
            print(f"- {file_name}: {error}")
    print("=" * 50)

def main():
    """
    主函数 - 处理命令行参数或交互式输入
    """
    # 命令行模式
    if len(sys.argv) >= 2:
        input_path = Path(sys.argv[1])

        if input_path.is_dir():
            if len(sys.argv) >= 3:
                output_dir = sys.argv[2]
                process_txt_folder(input_path, output_dir=output_dir)
            else:
                process_txt_folder(input_path)
        else:
            if len(sys.argv) >= 3:
                output_file = sys.argv[2]
                remove_court_library_text(input_path, output_file=output_file)
            else:
                remove_court_library_text(input_path)
    else:
        # 交互式模式
        print("=" * 50)
        print("文本清理工具 - 移除'人民法院案例库'文字")
        print("=" * 50)
        
        while True:
            print("\n请选择处理对象:")
            print("1. 单个txt文件")
            print("2. 一个文件夹中的全部txt文件")
            mode = input("请输入选项（1/2，输入q退出）: ").strip().lower()

            if mode == 'q':
                print("程序退出")
                break

            if mode not in ('1', '2'):
                print("选项无效，请输入1、2或q")
                continue

            if mode == '1':
                input_file = input("\n请输入要处理的txt文件路径（输入q返回）: ").strip().strip('"')
                if input_file.lower() == 'q':
                    continue

                if not Path(input_file).exists():
                    print(f"文件 '{input_file}' 不存在，请重新输入")
                    continue

                print("\n请选择处理方式:")
                print("1. 生成新文件（默认添加'_cleaned'后缀）")
                print("2. 直接修改原文件（请谨慎选择）")
                print("3. 指定输出文件名")

                choice = input("请输入选项（1/2/3，默认1）: ").strip()

                if choice == '2':
                    confirm = input("确认直接修改原文件？此操作不可逆（y/N）: ").strip().lower()
                    if confirm == 'y':
                        remove_court_library_text(input_file, inplace=True)
                    else:
                        print("操作已取消")
                elif choice == '3':
                    output_file = input("请输入输出文件名: ").strip()
                    if output_file:
                        remove_court_library_text(input_file, output_file=output_file)
                    else:
                        print("输出文件名不能为空，使用默认方式")
                        remove_court_library_text(input_file)
                else:
                    remove_court_library_text(input_file)
            else:
                input_dir = input("\n请输入包含txt文件的文件夹路径（输入q返回）: ").strip().strip('"')
                if input_dir.lower() == 'q':
                    continue

                if not Path(input_dir).exists() or not Path(input_dir).is_dir():
                    print(f"文件夹 '{input_dir}' 不存在，请重新输入")
                    continue

                print("\n请选择输出方式:")
                print("1. 输出到新文件夹（默认在原目录旁生成*_cleaned）")
                print("2. 直接覆盖原文件（请谨慎选择）")
                print("3. 指定输出文件夹")

                choice = input("请输入选项（1/2/3，默认1）: ").strip()

                if choice == '2':
                    confirm = input("确认直接覆盖原文件？此操作不可逆（y/N）: ").strip().lower()
                    if confirm == 'y':
                        process_txt_folder(input_dir, inplace=True)
                    else:
                        print("操作已取消")
                elif choice == '3':
                    output_dir = input("请输入输出文件夹路径: ").strip().strip('"')
                    if output_dir:
                        process_txt_folder(input_dir, output_dir=output_dir)
                    else:
                        print("输出文件夹不能为空，使用默认方式")
                        process_txt_folder(input_dir)
                else:
                    process_txt_folder(input_dir)
            
            # 询问是否继续处理其他文件
            cont = input("\n是否继续处理其他文件？(y/N): ").strip().lower()
            if cont != 'y':
                print("程序退出")
                break

if __name__ == "__main__":
    main()