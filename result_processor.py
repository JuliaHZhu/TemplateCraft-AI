from typing import List, Dict, Any, Optional
from template_analyzer import EnglishTemplateAnalyzer


class ResultProcessor:
    """结果处理器：格式化和展示分析与生成结果"""

    def __init__(self, templates: List[str], analyzed_templates: List[Dict], generated_paragraphs: List[str],
                 high_weight_index: int):
        self.templates = templates or []
        self.analyzed_templates = analyzed_templates or []
        self.generated_paragraphs = generated_paragraphs or []
        self.high_weight_index = high_weight_index

        # 数据长度一致性检查
        self._validate_input_data()

    def _validate_input_data(self):
        """验证输入数据的一致性"""
        lengths = [len(self.templates), len(self.analyzed_templates), len(self.generated_paragraphs)]
        if len(set(lengths)) > 1:
            print(f"警告: 输入数据长度不一致: templates={lengths[0]}, analyzed={lengths[1]}, generated={lengths[2]}")
            # 调整到最小长度
            min_length = min(lengths)
            self.templates = self.templates[:min_length]
            self.analyzed_templates = self.analyzed_templates[:min_length]
            self.generated_paragraphs = self.generated_paragraphs[:min_length]

    def format_result_json(self) -> Dict:
        """生成JSON格式的结果"""
        results = {
            'templates': [],
            'comparison': []
        }

        for i, (template, analyzed, generated) in enumerate(zip(
                self.templates, self.analyzed_templates, self.generated_paragraphs
        )):
            try:
                is_high_weight = i == self.high_weight_index

                # 计算相似度（带错误处理）
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

            except Exception as e:
                print(f"处理模板 {i} 时出错: {e}")
                # 添加错误模板的基本信息
                error_result = {
                    'template_index': i,
                    'is_high_weight': i == self.high_weight_index,
                    'original_text': template,
                    'analysis': analyzed,
                    'generated_text': generated,
                    'similarity_score': {'discourse': 0.0, 'content': 0.0, 'overall': 0.0},
                    'error': str(e)
                }
                results['templates'].append(error_result)

        # 添加总体统计信息
        results['statistics'] = self._calculate_statistics(results['templates'])

        return results

    def _calculate_similarity(self, analysis: Dict, generated: str) -> Dict:
        """计算相似度评分"""
        try:
            # 验证分析数据结构
            if not self._validate_analysis_structure(analysis):
                return {'discourse': 0.0, 'content': 0.0, 'overall': 0.0}

            analyzer = EnglishTemplateAnalyzer()
            generated_analysis = {
                'discourse_structure': analyzer.analyze_discourse_structure(generated),
                'content_structure': analyzer.analyze_content_structure(generated)
            }

            # 计算篇章结构相似度
            discourse_similarity = self._compare_discourse_structures(
                analysis.get('discourse_structure', {}),
                generated_analysis.get('discourse_structure', {})
            )

            # 计算内容结构相似度
            content_similarity = self._compare_content_structures(
                analysis.get('content_structure', {}),
                generated_analysis.get('content_structure', {})
            )

            # 整体相似度
            overall_similarity = (discourse_similarity * 0.5 + content_similarity * 0.5)

            return {
                'discourse': round(discourse_similarity, 3),
                'content': round(content_similarity, 3),
                'overall': round(overall_similarity, 3)
            }

        except Exception as e:
            print(f"计算相似度时出错: {e}")
            return {'discourse': 0.0, 'content': 0.0, 'overall': 0.0}

    def _validate_analysis_structure(self, analysis: Dict) -> bool:
        """验证分析结构的完整性"""
        if not isinstance(analysis, dict):
            print("分析结果不是字典格式")
            return False

        required_keys = ['discourse_structure', 'content_structure']
        missing_keys = [key for key in required_keys if key not in analysis]

        if missing_keys:
            print(f"分析结果缺少必要字段: {missing_keys}")
            return False

        return True

    def _compare_discourse_structures(self, original: Dict, generated: Dict) -> float:
        """比较篇章结构相似度"""
        try:
            similarity = 0.0
            count = 0

            # 比较句子数量
            orig_count = original.get('sentence_count', 1)
            gen_count = generated.get('sentence_count', 1)
            if orig_count > 0 and gen_count > 0:
                similarity += 1.0 - abs(orig_count - gen_count) / max(orig_count, gen_count)
                count += 1

            # 比较连接词使用
            orig_conn = original.get('connectives', {})
            gen_conn = generated.get('connectives', {})

            if orig_conn and gen_conn:
                conn_similarity = 0.0
                conn_count = 0

                for conn_type, orig_freq in orig_conn.items():
                    if conn_type in gen_conn and orig_freq > 0:
                        gen_freq = gen_conn[conn_type]
                        conn_similarity += 1.0 - abs(orig_freq - gen_freq) / max(orig_freq, gen_freq)
                        conn_count += 1

                if conn_count > 0:
                    similarity += conn_similarity / conn_count
                    count += 1

            # 比较修辞使用
            orig_rhet = original.get('rhetoric', {})
            gen_rhet = generated.get('rhetoric', {})

            if orig_rhet and gen_rhet:
                rhet_similarity = 0.0
                rhet_count = 0

                for rhet_type, orig_freq in orig_rhet.items():
                    if rhet_type in gen_rhet and orig_freq > 0:
                        gen_freq = gen_rhet[rhet_type]
                        rhet_similarity += 1.0 - abs(orig_freq - gen_freq) / max(orig_freq, gen_freq)
                        rhet_count += 1

                if rhet_count > 0:
                    similarity += rhet_similarity / rhet_count
                    count += 1

            return similarity / count if count > 0 else 0.0

        except Exception as e:
            print(f"比较篇章结构时出错: {e}")
            return 0.0

    def _compare_content_structures(self, original: Dict, generated: Dict) -> float:
        """比较内容结构相似度"""
        try:
            similarity = 0.0
            count = 0

            # 比较核心概念重叠度
            orig_concepts = original.get('core_concepts', [])
            gen_concepts = generated.get('core_concepts', [])

            if orig_concepts and gen_concepts:
                core_overlap = len(set(orig_concepts) & set(gen_concepts)) / max(
                    len(orig_concepts), len(gen_concepts), 1)
                similarity += core_overlap
                count += 1

            # 比较论述方向
            orig_direction = self._safe_get_argument_direction(original)
            gen_direction = self._safe_get_argument_direction(generated)

            if orig_direction and gen_direction:
                if orig_direction == gen_direction:
                    similarity += 1.0
                count += 1

            # 比较逻辑流程
            orig_flow = original.get('logical_flow', '')
            gen_flow = generated.get('logical_flow', '')

            if orig_flow and gen_flow:
                if orig_flow == gen_flow:
                    similarity += 1.0
                count += 1

            return similarity / count if count > 0 else 0.0

        except Exception as e:
            print(f"比较内容结构时出错: {e}")
            return 0.0

    def _safe_get_argument_direction(self, structure: Dict) -> Optional[str]:
        """安全获取论述方向"""
        try:
            arg_direction = structure.get('argument_direction', {})
            if isinstance(arg_direction, dict):
                return arg_direction.get('direction', None)
            elif isinstance(arg_direction, str):
                return arg_direction
            else:
                return None
        except Exception:
            return None

    def _calculate_statistics(self, template_results: List[Dict]) -> Dict:
        """计算总体统计信息"""
        try:
            if not template_results:
                return {
                    'total_templates': 0,
                    'high_weight_template_index': self.high_weight_index,
                    'average_overall_similarity': 0.0,
                    'high_weight_similarity': 0.0,
                    'normal_similarity_avg': 0.0
                }

            high_weight_result = next((r for r in template_results if r.get('is_high_weight', False)), None)
            normal_results = [r for r in template_results if not r.get('is_high_weight', False)]

            # 计算平均相似度
            valid_results = [r for r in template_results if
                             'similarity_score' in r and 'overall' in r['similarity_score']]
            avg_similarity = sum(r['similarity_score']['overall'] for r in valid_results) / len(
                valid_results) if valid_results else 0.0

            # 计算高权重模板相似度
            high_weight_similarity = 0.0
            if high_weight_result and 'similarity_score' in high_weight_result:
                high_weight_similarity = high_weight_result['similarity_score'].get('overall', 0.0)

            # 计算普通模板平均相似度
            valid_normal_results = [r for r in normal_results if
                                    'similarity_score' in r and 'overall' in r['similarity_score']]
            normal_avg = sum(r['similarity_score']['overall'] for r in valid_normal_results) / len(
                valid_normal_results) if valid_normal_results else 0.0

            return {
                'total_templates': len(template_results),
                'high_weight_template_index': self.high_weight_index,
                'average_overall_similarity': round(avg_similarity, 3),
                'high_weight_similarity': round(high_weight_similarity, 3),
                'normal_similarity_avg': round(normal_avg, 3)
            }

        except Exception as e:
            print(f"计算统计信息时出错: {e}")
            return {
                'total_templates': len(template_results),
                'high_weight_template_index': self.high_weight_index,
                'average_overall_similarity': 0.0,
                'high_weight_similarity': 0.0,
                'normal_similarity_avg': 0.0,
                'error': str(e)
            }

