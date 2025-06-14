import os
from typing import List, Dict, Any
from openai import OpenAI
from config import SOURCE_DIR, BASE_URL, ARK_API_KEY
from utils import read_text_file, write_json_file, read_json_file, get_case_dirs
from template_analyzer import EnglishTemplateAnalyzer
from prompt_generator import PromptGenerator
from result_processor import ResultProcessor



def process_case(case_dir: str, client: OpenAI) -> None:
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
            response = client.chat.completions.create(
                model="doubao-seed-1-6-250615",
                messages=[
                    {"role": "system",
                     "content": "你是一个专业的文本分析助手，请按照以下格式分析英文段落：\n```json\n{\n\"discourse_structure\": {...},\n\"content_structure\": {...}\n}\n```"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            analysis_result = analyzer.parse_response(response)
            analyzed_templates.append(analysis_result)
        except Exception as e:
            print(f"API调用错误: {e}")
            analyzed_templates.append({})

    # 2. 生成仿写prompt
    paraphrase_prompts = prompt_gen.generate_paraphrase_prompts(
        analyzed_templates, context, topic, high_weight_index
    )

    # 3. 生成仿写段落
    generated_paragraphs = []
    for prompt in paraphrase_prompts:
        try:
            response = client.chat.completions.create(
                model="doubao-seed-1-6-250615",
                messages=[
                    {"role": "system",
                     "content": "你是一个专业的英文段落生成助手，请根据给定的结构和主题生成一个连贯的英文段落。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            generated_paragraph = response.choices[0].message.content
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
    # 初始化Ark客户端，从环境变量中读取您的API Key
    client = OpenAI(
        # 此为默认路径，您可根据业务所在地域进行配置
        base_url=BASE_URL,
        # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
        api_key=ARK_API_KEY,
    )

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