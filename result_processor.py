from typing import List, Dict, Any
from template_analyzer import EnglishTemplateAnalyzer


class ResultProcessor:
    """结果处理器：格式化和展示分析与生成结果"""

    def __init__(self, templates: List[str], analyzed_templates: List[Dict], generated_paragraphs: List[str],
                 high_weight_index: int):
        self.templates = templates
        self.analyzed_templates = analyzed_templates
        self.generated_paragraphs = generated_paragraphs
        self.high_weight_index = high_weight_index

    def format_result_json(self) -> Dict:
        """生成JSON格式的结果"""
        results = {
            'templates': [],
            'comparison': []
        }

        for i, (template, analyzed, generated) in enumerate(zip(
                self.templates, self.analyzed_templates, self.generated_paragraphs
        )):
            is_high_weight = i == self.high_weight_index

            # 计算相似度
            similarity = self._calculate_similarity(analyzed, generated)

            template_result = {
                'template_index': i,
                'is_high_weight': is_high_weight,
                'original_text': template,
                'analysis': analyzed,
                'generated_text': generated,
                'similarity_score': similarity
            }

            results['templates'].append(template_result)

        # 添加总体统计信息
        results['statistics'] = self._calculate_statistics(results['templates'])

        return results

    def _calculate_similarity(self, analysis: Dict, generated: str) -> Dict:
        """计算相似度评分"""
        analyzer = EnglishTemplateAnalyzer()
        generated_analysis = {
            'discourse_structure': analyzer.analyze_discourse_structure(generated),
            'content_structure': analyzer.analyze_content_structure(generated)
        }

        # 计算篇章结构相似度
        discourse_similarity = self._compare_discourse_structures(
            analysis['discourse_structure'],
            generated_analysis['discourse_structure']
        )

        # 计算内容结构相似度
        content_similarity = self._compare_content_structures(
            analysis['content_structure'],
            generated_analysis['content_structure']
        )

        # 整体相似度
        overall_similarity = (discourse_similarity * 0.5 + content_similarity * 0.5)

        return {
            'discourse': discourse_similarity,
            'content': content_similarity,
            'overall': overall_similarity
        }

    def _compare_discourse_structures(self, original: Dict, generated: Dict) -> float:
        """比较篇章结构相似度"""
        similarity = 0.0
        count = 0

        # 比较句子数量
        similarity += 1.0 - abs(original['sentence_count'] - generated['sentence_count']) / max(
            original['sentence_count'], generated['sentence_count'], 1)
        count += 1

        # 比较连接词使用
        for conn_type in original['connectives']:
            if conn_type in generated['connectives']:
                similarity += 1.0 - abs(original['connectives'][conn_type] - generated['connectives'][conn_type]) / max(
                    original['connectives'][conn_type], generated['connectives'][conn_type], 1)
                count += 1

        # 比较修辞使用
        for rhet_type in original['rhetoric']:
            if rhet_type in generated['rhetoric']:
                similarity += 1.0 - abs(original['rhetoric'][rhet_type] - generated['rhetoric'][rhet_type]) / max(
                    original['rhetoric'][rhet_type], generated['rhetoric'][rhet_type], 1)
                count += 1

        return similarity / count if count > 0 else 0.0

    def _compare_content_structures(self, original: Dict, generated: Dict) -> float:
        """比较内容结构相似度"""
        similarity = 0.0
        count = 0

        # 比较核心概念重叠度
        core_overlap = len(set(original['core_concepts']) & set(generated['core_concepts'])) / max(
            len(original['core_concepts']), len(generated['core_concepts']), 1)
        similarity += core_overlap
        count += 1

        # 比较论述方向
        if original['argument_direction']['direction'] == generated['argument_direction']['direction']:
            similarity += 1.0
        count += 1

        # 比较逻辑流程
        if original['logical_flow'] == generated['logical_flow']:
            similarity += 1.0
        count += 1

        return similarity / count if count > 0 else 0.0

    def _calculate_statistics(self, template_results: List[Dict]) -> Dict:
        """计算总体统计信息"""
        high_weight_result = next((r for r in template_results if r['is_high_weight']), None)
        normal_results = [r for r in template_results if not r['is_high_weight']]

        return {
            'total_templates': len(template_results),
            'high_weight_template_index': self.high_weight_index,
            'average_overall_similarity': sum(r['similarity_score']['overall'] for r in template_results) / len(
                template_results),
            'high_weight_similarity': high_weight_result['similarity_score']['overall'] if high_weight_result else 0,
            'normal_similarity_avg': sum(r['similarity_score']['overall'] for r in normal_results) / len(
                normal_results) if normal_results else 0
        }