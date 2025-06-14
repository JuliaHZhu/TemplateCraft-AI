# main.py

import os
from typing import List, Dict, Any
from config import SOURCE_DIR
from utils import read_text_file, write_json_file, get_case_dirs
from template_analyzer import EnglishTemplateAnalyzer
from prompt_generator import PromptGenerator
from result_processor import ResultProcessor
from api_client import OpenAIClient  # 导入 OpenAIClient


def process_case(case_dir: str, client: OpenAIClient) -> None:
    """处理单个案例"""
    print(f"Processing case: {os.path.basename(case_dir)}")

    # 读取输入数据
    context = read_text_file(os.path.join(case_dir, "context.txt"))
    topic = read_text_file(os.path.join(case_dir, "topic.txt"))
    high_weight_index = int(read_text_file(os.path.join(case_dir, "high_weight.txt")))

    # 读取模板
    templates = []
    for i in range(1, 5):
        template_file = os.path.join(case_dir, f"template{i}.json")
        template_content = read_text_file(template_file)
        templates.append(template_content)

    # 初始化组件
    analyzer = EnglishTemplateAnalyzer()
    prompt_gen = PromptGenerator()

    # 1. 分析模板
    analyzed_templates = []
    analysis_prompts = prompt_gen.generate_analysis_prompts(templates)

    for prompt in analysis_prompts:
        try:
            analysis_result = client.analyze_template(prompt)
            if 'discourse_structure' in analysis_result and 'content_structure' in analysis_result:
                analyzed_templates.append(analysis_result)
            else:
                print("分析结果缺少必要的结构字段。")
                analyzed_templates.append({})
        except Exception as e:
            print(f"API调用错误: {e}")
            analyzed_templates.append({})

    # 2. 生成仿写 prompt
    paraphrase_prompts = prompt_gen.generate_paraphrase_prompts(
        analyzed_templates, context, topic, high_weight_index
    )

    # 3. 生成仿写段落
    generated_paragraphs = []
    for prompt in paraphrase_prompts:
        try:
            generated_paragraph = client.generate_paragraph(prompt)
            generated_paragraphs.append(generated_paragraph)
        except Exception as e:
            print(f"API调用错误: {e}")
            generated_paragraphs.append("")

    # 4. 处理结果
    processor = ResultProcessor(
        templates, analyzed_templates, generated_paragraphs, high_weight_index
    )

    result_data = processor.format_result_json()

    # 5. 保存结果
    result_file = os.path.join(case_dir, "results.json")
    write_json_file(result_data, result_file)

    print(f"Results saved to: {result_file}")


def main() -> None:
    """主函数：处理所有案例"""
    # 初始化 OpenAI 客户端
    client = OpenAIClient()

    case_dirs = get_case_dirs(SOURCE_DIR)

    if not case_dirs:
        print("No case directories found in source directory.")
        return

    print(f"Found {len(case_dirs)} cases to process.")

    for case_dir in case_dirs:
        process_case(case_dir, client)

    print("All cases processed successfully.")


if __name__ == "__main__":
    main()


