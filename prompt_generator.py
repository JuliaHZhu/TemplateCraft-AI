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
            try:
                # 先验证模板结构
                if not self._validate_template_structure(template):
                    print(f"警告: 模板 {i} 结构不完整，使用基础prompt")
                    base_prompt = self._create_fallback_prompt(context, topic)
                else:
                    base_prompt = self._create_base_paraphrase_prompt(template, context, topic)

                # 高权重模板增强
                if i == high_weight_index:
                    enhanced_prompt = self._enhance_prompt_for_high_weight(base_prompt, template)
                    prompts.append(enhanced_prompt)
                else:
                    prompts.append(base_prompt)

            except Exception as e:
                print(f"创建基础prompt时出错: {e}")
                # 使用备用prompt
                fallback_prompt = self._create_fallback_prompt(context, topic)
                prompts.append(fallback_prompt)

        return prompts

    def _validate_template_structure(self, template: Dict) -> bool:
        """验证模板结构的完整性"""
        if not isinstance(template, dict):
            return False

        required_keys = ['discourse_structure', 'content_structure']
        return all(key in template for key in required_keys)

    def _create_base_paraphrase_prompt(self, template: Dict, context: str, topic: str) -> str:
        """创建基础仿写prompt"""
        try:
            discourse = template.get('discourse_structure', {})
            content = template.get('content_structure', {})

            # 安全地获取数值，确保类型转换
            sentence_count = discourse.get('sentence_count', 3)
            if isinstance(sentence_count, str):
                try:
                    sentence_count = int(sentence_count)
                except ValueError:
                    sentence_count = 3

            # 获取句子类型信息
            sentence_types = discourse.get('sentence_types', [])
            if isinstance(sentence_types, dict):
                sentence_types = list(sentence_types.keys())
            elif not isinstance(sentence_types, list):
                sentence_types = ['declarative', 'complex']

            # 获取连接词信息
            connectives = discourse.get('connectives', [])
            if isinstance(connectives, dict):
                connectives = list(connectives.keys())
            elif not isinstance(connectives, list):
                connectives = ['however', 'therefore', 'furthermore']

            # 获取核心概念
            core_concepts = content.get('core_concepts', [])
            if isinstance(core_concepts, str):
                core_concepts = [core_concepts]
            elif not isinstance(core_concepts, list):
                core_concepts = ['innovation', 'strategy']

            # 获取论证方向
            argument_direction = content.get('argument_direction', 'balanced')
            if not isinstance(argument_direction, str):
                argument_direction = 'balanced'

            # 获取逻辑流向
            logical_flow = content.get('logical_flow', 'sequential')
            if not isinstance(logical_flow, str):
                logical_flow = 'sequential'

            prompt = f"""
Generate a coherent paragraph about {topic} in the context of {context}.

Structure Requirements:
- Use approximately {sentence_count} sentences
- Include sentence types: {', '.join(sentence_types)}
- Use connective words like: {', '.join(connectives[:3])}
- Follow {logical_flow} logical flow
- Maintain {argument_direction} argument direction

Content Requirements:
- Focus on these core concepts: {', '.join(core_concepts[:3])}
- Ensure the paragraph flows naturally
- Use academic writing style
- Make the content relevant to the given context

Please generate a well-structured paragraph that follows these requirements.
"""
            return prompt

        except Exception as e:
            print(f"创建基础prompt时出错: {e}")
            return self._create_fallback_prompt(context, topic)

    def _create_fallback_prompt(self, context: str, topic: str) -> str:
        """创建备用的简单prompt"""
        return f"""
Generate a coherent paragraph about {topic} in the context of {context}.

Requirements:
- Write 3-5 sentences
- Use academic writing style
- Ensure logical flow
- Make content relevant to the context
"""

    def _enhance_prompt_for_high_weight(self, base_prompt: str, template: Dict) -> str:
        """为高权重模板增强prompt"""
        try:
            discourse = template.get('discourse_structure', {})
            content = template.get('content_structure', {})

            # 提取独特特征
            unique_features = []
            rhetoric = discourse.get('rhetoric', {})

            if isinstance(rhetoric, dict):
                if rhetoric.get('simile', 0) > 0:
                    unique_features.append("simile rhetorical device")
                if rhetoric.get('parallelism', 0) > 0:
                    unique_features.append("parallel sentence structure")
                if rhetoric.get('metaphor', 0) > 0:
                    unique_features.append("metaphorical expressions")

            logical_flow = content.get('logical_flow', 'sequential')
            if not isinstance(logical_flow, str):
                logical_flow = 'sequential'

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



