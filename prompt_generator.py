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
            base_prompt = self._create_base_paraphrase_prompt(template, context, topic)

            # 高权重模板增强
            if i == high_weight_index:
                enhanced_prompt = self._enhance_prompt_for_high_weight(base_prompt, template)
                prompts.append(enhanced_prompt)
            else:
                prompts.append(base_prompt)

        return prompts

    def _create_base_paraphrase_prompt(self, template: Dict, context: str, topic: str) -> str:
        """创建基础仿写prompt"""
        discourse = template['discourse_structure']
        content = template['content_structure']

        # 构建结构描述
        structure_desc = f"""
        Generate a paragraph following this structure:
        1. Discourse Structure: 
           - {discourse['sentence_count']} sentences
           - Connectives: {', '.join([f'{k} ({v} times)' for k, v in discourse['connectives'].items() if v > 0])}
           - Rhetorical devices: {', '.join([f'{k} ({v} times)' for k, v in discourse['rhetoric'].items() if v > 0])}
           - Sentence types: {', '.join([f'{k}: {v}' for k, v in discourse['sentence_types'].items()])}

        2. Content Structure:
           - Core concepts: {', '.join(content['core_concepts'])}
           - Argument direction: {content['argument_direction']['direction']}
           - Logical flow: {content['logical_flow']}

        Context: {context}
        Topic: {topic}

        Requirements:
        - Maintain the above structural features
        - Replace specific concepts with topic-related content
        - Ensure the paragraph is coherent and well-organized
        """
        return structure_desc

    def _enhance_prompt_for_high_weight(self, base_prompt: str, template: Dict) -> str:
        """为高权重模板增强prompt"""
        discourse = template['discourse_structure']
        content = template['content_structure']

        # 提取独特特征
        unique_features = []
        if discourse['rhetoric'].get('simile', 0) > 0:
            unique_features.append("simile rhetorical device")
        if discourse['rhetoric'].get('parallelism', 0) > 0:
            unique_features.append("parallel sentence structure")

        # 添加高权重指令
        enhanced_prompt = base_prompt + f"""

        Special Instructions (High Priority Template):
        - Pay extra attention to preserving the following features: {', '.join(unique_features)}
        - Follow the {content['logical_flow']} logical structure strictly
        - Ensure positive statements about the topic account for at least 60% of the paragraph
        - Use academic language style
        """
        return enhanced_prompt