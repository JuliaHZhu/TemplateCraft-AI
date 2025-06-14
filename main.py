import os
from typing import List, Dict, Any
from config import SOURCE_DIR
from utils import read_text_file, write_json_file, read_json_file, get_case_dirs
from template_analyzer import EnglishTemplateAnalyzer
from prompt_generator import PromptGenerator
from api_client import VolcengineAPIClient
from result_processor import ResultProcessor


def process_case(case_dir: str) -> None:
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
    api_client = VolcengineAPIClient()

    # 1. 分析模板
    analyzed_templates = []
    analysis_prompts = prompt_gen.generate_analysis_prompts(templates)

    for prompt in analysis_prompts:
        analysis_result = api_client.analyze_template(prompt)
        analyzed_templates.append(analysis_result)

    # 2. 生成仿写prompt
    paraphrase_prompts = prompt_gen.generate_paraphrase_prompts(
        analyzed_templates, context, topic, high_weight_index
    )

    # 3. 生成仿写段落
    generated_paragraphs = api_client.batch_process(paraphrase_prompts, "generation")

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
    case_dirs = get_case_dirs(SOURCE_DIR)

    if not case_dirs:
        print("No case directories found in source directory.")
        return

    print(f"Found {len(case_dirs)} cases to process.")

    for case_dir in case_dirs:
        process_case(case_dir)

    print("All cases processed successfully.")


if __name__ == "__main__":
    main()