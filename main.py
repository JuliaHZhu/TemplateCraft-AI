# main.py

import os
import json
from typing import List, Dict, Any
from config import SOURCE_DIR
from utils import read_text_file, write_json_file, get_case_dirs
from template_analyzer import EnglishTemplateAnalyzer
from prompt_generator import PromptGenerator
from result_processor import ResultProcessor
from api_client import OpenAIClient  # 导入 OpenAIClient


def process_case(case_dir: str, client: OpenAIClient) -> None:
    """处理单个案例"""
    case_name = os.path.basename(case_dir)
    print(f"\n{'=' * 50}")
    print(f"开始处理案例: {case_name}")
    print(f"案例路径: {case_dir}")
    print(f"{'=' * 50}")

    try:
        # 读取输入数据
        print("\n[步骤1] 读取输入数据...")

        print("  读取 context.txt...")
        context_path = os.path.join(case_dir, "context.txt")
        print(f"    文件路径: {context_path}")
        if not os.path.exists(context_path):
            print(f"    错误: context.txt 不存在")
            return
        context = read_text_file(context_path)
        print(f"    成功读取，长度: {len(context)} 字符")
        print(f"    内容预览: {context[:100]}...")

        print("  读取 topic.txt...")
        topic_path = os.path.join(case_dir, "topic.txt")
        print(f"    文件路径: {topic_path}")
        if not os.path.exists(topic_path):
            print(f"    错误: topic.txt 不存在")
            return
        topic = read_text_file(topic_path)
        print(f"    成功读取，内容: {topic}")

        print("  读取 high_weight.txt...")
        high_weight_path = os.path.join(case_dir, "high_weight.txt")
        print(f"    文件路径: {high_weight_path}")
        if not os.path.exists(high_weight_path):
            print(f"    错误: high_weight.txt 不存在")
            return
        high_weight_content = read_text_file(high_weight_path)
        print(f"    读取内容: '{high_weight_content}'")
        try:
            high_weight_index = int(high_weight_content.strip())
            print(f"    转换为整数: {high_weight_index}")
            print(f"    类型确认: {type(high_weight_index)}")
        except ValueError as e:
            print(f"    错误: 无法将 '{high_weight_content}' 转换为整数: {e}")
            return

        # 读取模板
        print("\n[步骤2] 读取模板文件...")
        templates = []
        for i in range(1, 5):
            template_file = os.path.join(case_dir, f"template{i}.json")
            print(f"  读取 template{i}.json...")
            print(f"    文件路径: {template_file}")

            if not os.path.exists(template_file):
                print(f"    错误: template{i}.json 不存在")
                return

            try:
                template_content = read_text_file(template_file)
                print(f"    成功读取，长度: {len(template_content)} 字符")

                # 验证是否为有效 JSON
                json.loads(template_content)
                templates.append(template_content)
                print(f"    JSON 格式验证通过")
            except json.JSONDecodeError as e:
                print(f"    错误: template{i}.json 不是有效的 JSON 格式: {e}")
                return
            except Exception as e:
                print(f"    错误: 读取 template{i}.json 失败: {e}")
                return

        print(f"  成功读取 {len(templates)} 个模板文件")

        # 初始化组件
        print("\n[步骤3] 初始化组件...")
        try:
            analyzer = EnglishTemplateAnalyzer()
            print("  EnglishTemplateAnalyzer 初始化成功")

            prompt_gen = PromptGenerator()
            print("  PromptGenerator 初始化成功")
        except Exception as e:
            print(f"  错误: 组件初始化失败: {e}")
            return

        # 1. 分析模板
        print("\n[步骤4] 分析模板...")
        analyzed_templates = []

        try:
            analysis_prompts = prompt_gen.generate_analysis_prompts(templates)
            print(f"  生成了 {len(analysis_prompts)} 个分析提示")
        except Exception as e:
            print(f"  错误: 生成分析提示失败: {e}")
            return

        for i, prompt in enumerate(analysis_prompts, 1):
            print(f"\n  分析模板 {i}/{len(analysis_prompts)}...")
            print(f"    提示长度: {len(prompt)} 字符")
            print(f"    提示预览: {prompt[:200]}...")

            try:
                print("    调用 API 分析模板...")
                analysis_result = client.analyze_template(prompt)
                print(f"    API 调用成功，返回类型: {type(analysis_result)}")

                if isinstance(analysis_result, dict):
                    print(f"    返回字典键: {list(analysis_result.keys())}")

                    if 'discourse_structure' in analysis_result and 'content_structure' in analysis_result:
                        analyzed_templates.append(analysis_result)
                        print("    ✓ 分析结果包含必要的结构字段")
                        # 打印更详细的结构信息
                        discourse = analysis_result.get('discourse_structure', {})
                        content = analysis_result.get('content_structure', {})
                        print(
                            f"      discourse_structure 键: {list(discourse.keys()) if isinstance(discourse, dict) else type(discourse)}")
                        print(
                            f"      content_structure 键: {list(content.keys()) if isinstance(content, dict) else type(content)}")
                    else:
                        print("    ✗ 分析结果缺少必要的结构字段")
                        print(f"    实际返回内容: {analysis_result}")
                        analyzed_templates.append({})
                else:
                    print(f"    ✗ API 返回类型错误，期望 dict，实际 {type(analysis_result)}")
                    print(f"    实际返回内容: {analysis_result}")
                    analyzed_templates.append({})

            except Exception as e:
                print(f"    ✗ API 调用错误: {e}")
                print(f"    错误类型: {type(e).__name__}")
                import traceback
                print(f"    错误堆栈: {traceback.format_exc()}")
                analyzed_templates.append({})

        print(f"  模板分析完成，成功分析 {sum(1 for t in analyzed_templates if t)} 个模板")
        print(f"  analyzed_templates 长度: {len(analyzed_templates)}")

        # 打印每个分析结果的概要
        for i, template in enumerate(analyzed_templates, 1):
            if template:
                print(f"    模板 {i}: 有效 (键: {list(template.keys())})")
            else:
                print(f"    模板 {i}: 无效或空")

        # 2. 生成仿写 prompt
        print("\n[步骤5] 生成仿写提示...")
        print(f"  输入参数:")
        print(f"    analyzed_templates 长度: {len(analyzed_templates)}")
        print(f"    context 长度: {len(context)}")
        print(f"    topic: {topic}")
        print(f"    high_weight_index: {high_weight_index} (类型: {type(high_weight_index)})")

        try:
            paraphrase_prompts = prompt_gen.generate_paraphrase_prompts(
                analyzed_templates, context, topic, high_weight_index
            )
            print(f"  生成了 {len(paraphrase_prompts)} 个仿写提示")

            # 打印每个提示的概要
            for i, prompt in enumerate(paraphrase_prompts, 1):
                print(f"    提示 {i} 长度: {len(prompt)} 字符")

        except Exception as e:
            print(f"  错误: 生成仿写提示失败: {e}")
            print(f"  错误类型: {type(e).__name__}")
            import traceback
            print(f"  错误堆栈: {traceback.format_exc()}")
            return

        # 3. 生成仿写段落
        print("\n[步骤6] 生成仿写段落...")
        generated_paragraphs = []

        for i, prompt in enumerate(paraphrase_prompts, 1):
            print(f"\n  生成段落 {i}/{len(paraphrase_prompts)}...")
            print(f"    提示长度: {len(prompt)} 字符")
            print(f"    提示预览: {prompt[:200]}...")

            try:
                print("    调用 API 生成段落...")
                generated_paragraph = client.generate_paragraph(prompt)
                print(f"    API 调用成功，返回类型: {type(generated_paragraph)}")
                print(f"    生成段落长度: {len(generated_paragraph)} 字符")
                print(f"    段落预览: {generated_paragraph[:100]}...")
                generated_paragraphs.append(generated_paragraph)
            except Exception as e:
                print(f"    ✗ API 调用错误: {e}")
                print(f"    错误类型: {type(e).__name__}")
                generated_paragraphs.append("")

        print(f"  段落生成完成，成功生成 {sum(1 for p in generated_paragraphs if p)} 个段落")

        # 4. 处理结果
        print("\n[步骤7] 处理结果...")
        try:
            processor = ResultProcessor(
                templates, analyzed_templates, generated_paragraphs, high_weight_index
            )
            print("  ResultProcessor 初始化成功")

            result_data = processor.format_result_json()
            print(f"  结果格式化完成，数据类型: {type(result_data)}")
            print(f"  结果键: {list(result_data.keys()) if isinstance(result_data, dict) else 'N/A'}")
        except Exception as e:
            print(f"  错误: 结果处理失败: {e}")
            return

        # 5. 保存结果
        print("\n[步骤8] 保存结果...")
        result_file = os.path.join(case_dir, "results.json")
        print(f"  保存路径: {result_file}")

        try:
            write_json_file(result_data, result_file)
            print("  ✓ 结果保存成功")
        except Exception as e:
            print(f"  ✗ 保存结果失败: {e}")
            return

        print(f"\n✓ 案例 {case_name} 处理完成")

    except Exception as e:
        print(f"\n✗ 处理案例 {case_name} 时发生未预期的错误: {e}")
        print(f"错误类型: {type(e).__name__}")
        import traceback
        print(f"错误堆栈:\n{traceback.format_exc()}")


def main() -> None:
    """主函数：处理所有案例"""
    print("程序启动...")
    print(f"源目录: {SOURCE_DIR}")

    # 检查源目录是否存在
    if not os.path.exists(SOURCE_DIR):
        print(f"错误: 源目录不存在: {SOURCE_DIR}")
        return

    print("源目录存在，继续执行...")

    # 初始化 OpenAI 客户端
    print("\n初始化 OpenAI 客户端...")
    try:
        client = OpenAIClient()
        print("OpenAI 客户端初始化成功")

        # 测试连接
        print("测试 API 连接...")
        if client.test_connection():
            print("✓ API 连接测试成功")
        else:
            print("✗ API 连接测试失败，但继续执行...")

    except Exception as e:
        print(f"✗ OpenAI 客户端初始化失败: {e}")
        return

    # 获取案例目录
    print("\n获取案例目录...")
    try:
        case_dirs = get_case_dirs(SOURCE_DIR)
        print(f"找到 {len(case_dirs)} 个案例目录")

        if not case_dirs:
            print("错误: 在源目录中未找到案例目录")
            return

        for i, case_dir in enumerate(case_dirs, 1):
            print(f"  {i}. {os.path.basename(case_dir)}")

    except Exception as e:
        print(f"获取案例目录失败: {e}")
        return

    # 处理所有案例
    print(f"\n开始处理 {len(case_dirs)} 个案例...")

    success_count = 0
    for i, case_dir in enumerate(case_dirs, 1):
        print(f"\n处理进度: {i}/{len(case_dirs)}")
        try:
            process_case(case_dir, client)
            success_count += 1
        except Exception as e:
            print(f"处理案例失败: {e}")
            continue

    print(f"\n{'=' * 50}")
    print(f"所有案例处理完成")
    print(f"成功处理: {success_count}/{len(case_dirs)} 个案例")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()




