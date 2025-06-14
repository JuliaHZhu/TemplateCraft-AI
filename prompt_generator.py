from typing import List, Dict, Any


class PromptGenerator:
    """Prompt生成器：基于模板分析结果创建多样化的提示词"""

    def generate_analysis_prompts(self, templates: List[str]) -> List[str]:
        """生成用于分析模板的prompt"""
        prompts = []
        for i, template in enumerate(templates):
            prompt = f"""
            Analyze the following English paragraph in two aspects:
            1. Discourse Structure: Identify the function of each sentence, the rhetorical devices used, and the sentence connection patterns.
            2. Content Structure: Extract the core concepts, the direction of argumentation (positive/negative/balanced), and the logical flow.

            Paragraph:
            {template}

            Provide your analysis in JSON format with the following keys:
            - discourse_structure: {{"sentence_count", "sentence_types", "connectives", "rhetoric", "sentence_length"}}
            - content_structure: {{"core_concepts", "related_concepts", "argument_direction", "logical_flow"}}
            """
            prompts.append(prompt)
        return prompts

    def generate_paraphrase_prompts(self, analyzed_templates: List[Dict], context: str, topic: str,
                                    high_weight_index: int) -> List[str]:
        """生成用于仿写的prompt"""
        prompts = []
        for i, template in enumerate(analyzed_templates):
            # 先验证模板结构
            if not self._validate_template_structure(template):
                print(f"警告: 模板 {i} 结构不完整，跳过处理")
                continue

            base_prompt = self._create_base_paraphrase_prompt(template, context, topic)

            # 高权重模板增强
            if i == high_weight_index:
                enhanced_prompt = self._enhance_prompt_for_high_weight(base_prompt, template)
                prompts.append(enhanced_prompt)
            else:
                prompts.append(base_prompt)

        return prompts

    def _validate_template_structure(self, template: Dict) -> bool:
        """验证模板是否包含必要的结构字段"""
        required_fields = ['discourse_structure', 'content_structure']

        for field in required_fields:
            if field not in template:
                print(f"缺少必要字段: {field}")
                print(f"当前模板包含的字段: {list(template.keys())}")
                return False

        # 验证子字段
        discourse_fields = ['sentence_count', 'sentence_types', 'connectives', 'rhetoric']
        content_fields = ['core_concepts', 'argument_direction', 'logical_flow']

        discourse = template.get('discourse_structure', {})
        for field in discourse_fields:
            if field not in discourse:
                print(f"discourse_structure 中缺少字段: {field}")
                return False

        content = template.get('content_structure', {})
        for field in content_fields:
            if field not in content:
                print(f"content_structure 中缺少字段: {field}")
                return False

        return True

    def _create_base_paraphrase_prompt(self, template: Dict, context: str, topic: str) -> str:
        """创建基础仿写prompt"""
        try:
            discourse = template['discourse_structure']
            content = template['content_structure']

            # 安全获取字段值
            sentence_count = discourse.get('sentence_count', 'multiple')
            connectives = discourse.get('connectives', {})
            rhetoric = discourse.get('rhetoric', {})
            sentence_types = discourse.get('sentence_types', {})

            core_concepts = content.get('core_concepts', [])
            argument_direction = content.get('argument_direction', {})
            logical_flow = content.get('logical_flow', 'sequential')

            # 构建连接词描述
            connectives_desc = ', '.join(
                [f'{k} ({v} times)' for k, v in connectives.items() if v > 0]) or 'none specified'

            # 构建修辞手法描述
            rhetoric_desc = ', '.join([f'{k} ({v} times)' for k, v in rhetoric.items() if v > 0]) or 'none specified'

            # 构建句型描述
            sentence_types_desc = ', '.join([f'{k}: {v}' for k, v in sentence_types.items()]) or 'mixed types'

            # 获取论证方向
            arg_direction = argument_direction.get('direction', 'balanced') if isinstance(argument_direction,
                                                                                          dict) else str(
                argument_direction)

            # 构建结构描述
            structure_desc = f"""
Generate a paragraph following this structure:
1. Discourse Structure: 
   - {sentence_count} sentences
   - Connectives: {connectives_desc}
   - Rhetorical devices: {rhetoric_desc}
   - Sentence types: {sentence_types_desc}

2. Content Structure:
   - Core concepts: {', '.join(core_concepts) if core_concepts else 'general concepts'}
   - Argument direction: {arg_direction}
   - Logical flow: {logical_flow}

Context: {context}
Topic: {topic}

Requirements:
- Maintain the above structural features
- Replace specific concepts with topic-related content
- Ensure the paragraph is coherent and well-organized
"""
            return structure_desc

        except Exception as e:
            print(f"创建基础prompt时出错: {e}")
            # 返回简化版本的prompt
            return f"""
Generate a coherent paragraph about {topic} in the context of {context}.
Requirements:
- Use clear and logical structure
- Include relevant examples and explanations
- Maintain academic writing style
"""

    def _enhance_prompt_for_high_weight(self, base_prompt: str, template: Dict) -> str:
        """为高权重模板增强prompt"""
        try:
            discourse = template.get('discourse_structure', {})
            content = template.get('content_structure', {})

            # 提取独特特征
            unique_features = []
            rhetoric = discourse.get('rhetoric', {})

            if rhetoric.get('simile', 0) > 0:
                unique_features.append("simile rhetorical device")
            if rhetoric.get('parallelism', 0) > 0:
                unique_features.append("parallel sentence structure")
            if rhetoric.get('metaphor', 0) > 0:
                unique_features.append("metaphorical expressions")

            logical_flow = content.get('logical_flow', 'sequential')
            features_desc = ', '.join(unique_features) if unique_features else 'clear structure and flow'

            # 添加高权重指令
            enhanced_prompt = base_prompt + f"""

Special Instructions (High Priority Template):
- Pay extra attention to preserving the following features: {features_desc}
- Follow the {logical_flow} logical structure strictly
- Ensure positive statements about the topic account for at least 60% of the paragraph
- Use academic language style
- Make the argument more compelling and well-supported
"""
            return enhanced_prompt

        except Exception as e:
            print(f"增强prompt时出错: {e}")
            return base_prompt + """

Special Instructions (High Priority Template):
- Use more sophisticated language and structure
- Provide stronger arguments and evidence
- Maintain academic writing standards
"""

