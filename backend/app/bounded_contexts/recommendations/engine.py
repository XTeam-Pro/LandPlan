"""Recommendation Engine - Rule-based system for land development recommendations"""

from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from app.models import Land, LandFeature


class Priority(str, Enum):
    """Priority levels for services"""
    CRITICAL = "critical"  # Must do
    RECOMMENDED = "recommended"  # Should do
    OPTIONAL = "optional"  # Nice to have


@dataclass
class ServiceRecommendation:
    """Single service recommendation"""
    service_id: int
    service_slug: str
    service_name: str
    priority: Priority
    reason: str
    step_order: int = 0


class RecommendationEngine:
    """
    Rule-based engine for generating recommendations.

    Takes land characteristics and outputs ordered list of services to complete.
    """

    # Service slug mappings for rule conditions
    SERVICE_SLUGS = {
        # Water-related
        'water_analysis': 1,
        'water_drilling': 2,
        'water_supply': 3,

        # Cadastral
        'cadastral_survey': 15,
        'boundary_determination': 16,
        'boundary_marking': 20,

        # Legal
        'legal_consultation': 49,
        'purchase_support': 50,
        'full_legal_support': 51,

        # Geology & Preparation
        'geological_survey': 8,
        'soil_testing': 9,

        # Design & Construction
        'architectural_design': 40,
        'engineering_design': 41,
        'construction_project': 42,
        'foundation': 43,
        'building_construction': 44,

        # Drainage
        'drainage_system': 13,

        # Landscaping
        'landscape_design': 17,

        # Appraisal
        'land_appraisal': 18,

        # Category conversion
        'land_category_conversion': 52,
    }

    @classmethod
    def get_recommendations(
        cls,
        land: Land,
        features: LandFeature,
    ) -> Dict[str, Any]:
        """
        Generate recommendations for a land parcel.

        Returns:
            Dict with:
            - services: List of ServiceRecommendation objects
            - plan_steps: Ordered list of execution steps
        """

        recommendations = []

        # ===== RULE 1: Water Supply =====
        if not features.has_water:
            recommendations.extend([
                ServiceRecommendation(
                    service_id=1,
                    service_slug='water_analysis',
                    service_name='Анализ воды',
                    priority=Priority.CRITICAL,
                    reason='Вода отсутствует - необходим анализ скважины или централизованного водоснабжения',
                    step_order=1,
                ),
                ServiceRecommendation(
                    service_id=2,
                    service_slug='water_drilling',
                    service_name='Бурение скважины',
                    priority=Priority.CRITICAL,
                    reason='Нет доступа к воде - необходимо пробурить скважину',
                    step_order=1,
                ),
                ServiceRecommendation(
                    service_id=3,
                    service_slug='water_supply',
                    service_name='Водоснабжение',
                    priority=Priority.CRITICAL,
                    reason='Требуется система водоснабжения на участке',
                    step_order=2,
                ),
            ])

        # ===== RULE 2: Boundaries =====
        # Note: cadastral survey removed from critical — cadastral number is now
        # required at publication. If boundaries not defined, recommend boundary services.
        if not features.boundaries_defined:
            recommendations.extend([
                ServiceRecommendation(
                    service_id=16,
                    service_slug='boundary_determination',
                    service_name='Определение границ',
                    priority=Priority.RECOMMENDED,
                    reason='Границы участка не определены — рекомендуется межевание',
                    step_order=2,
                ),
                ServiceRecommendation(
                    service_id=20,
                    service_slug='boundary_marking',
                    service_name='Разметка границ',
                    priority=Priority.RECOMMENDED,
                    reason='Рекомендуется физическая разметка границ участка',
                    step_order=2,
                ),
            ])

        # ===== RULE 3: Purchase/Legal =====
        if land.deal_type == 'purchase':
            recommendations.extend([
                ServiceRecommendation(
                    service_id=49,
                    service_slug='legal_consultation',
                    service_name='Юридическая консультация',
                    priority=Priority.CRITICAL,
                    reason='При покупке необходима юридическая консультация',
                    step_order=1,
                ),
                ServiceRecommendation(
                    service_id=50,
                    service_slug='purchase_support',
                    service_name='Сопровождение покупки',
                    priority=Priority.CRITICAL,
                    reason='Юридическое сопровождение процесса покупки земли',
                    step_order=1,
                ),
                ServiceRecommendation(
                    service_id=51,
                    service_slug='full_legal_support',
                    service_name='Полное юридическое сопровождение',
                    priority=Priority.RECOMMENDED,
                    reason='Рекомендуется комплексное юридическое сопровождение сделки',
                    step_order=2,
                ),
            ])

        # ===== RULE 4: Appraisal =====
        if land.deal_type in ('purchase', 'lease'):
            recommendations.append(
                ServiceRecommendation(
                    service_id=18,
                    service_slug='land_appraisal',
                    service_name='Оценка земли',
                    priority=Priority.RECOMMENDED,
                    reason='Рекомендуется оценка стоимости земли при покупке/аренде',
                    step_order=2,
                )
            )

        # ===== RULE 5: Soil Preparation for Construction =====
        if not features.build_ready:
            recommendations.extend([
                ServiceRecommendation(
                    service_id=8,
                    service_slug='geological_survey',
                    service_name='Геологическое исследование',
                    priority=Priority.RECOMMENDED,
                    reason='Участок не готов к строительству - нужно исследовать грунт',
                    step_order=3,
                ),
                ServiceRecommendation(
                    service_id=9,
                    service_slug='soil_testing',
                    service_name='Тестирование грунта',
                    priority=Priority.RECOMMENDED,
                    reason='Анализ характеристик грунта перед строительством',
                    step_order=3,
                ),
            ])

        # ===== RULE 6: Design & Construction =====
        recommendations.extend([
            ServiceRecommendation(
                service_id=40,
                service_slug='architectural_design',
                service_name='Архитектурный проект',
                priority=Priority.RECOMMENDED,
                reason='Требуется архитектурный проект для строительства',
                step_order=4,
            ),
            ServiceRecommendation(
                service_id=41,
                service_slug='engineering_design',
                service_name='Инженерный проект',
                priority=Priority.RECOMMENDED,
                reason='Проектирование инженерных коммуникаций',
                step_order=4,
            ),
            ServiceRecommendation(
                service_id=44,
                service_slug='building_construction',
                service_name='Строительство дома',
                priority=Priority.OPTIONAL,
                reason='Непосредственное строительство жилого здания',
                step_order=5,
            ),
        ])

        # ===== RULE 7: Drainage (if no utilities) =====
        if not features.has_gas and not features.has_electricity:
            recommendations.append(
                ServiceRecommendation(
                    service_id=13,
                    service_slug='drainage_system',
                    service_name='Система дренажа',
                    priority=Priority.RECOMMENDED,
                    reason='Рекомендуется устройство дренажной системы на участке',
                    step_order=3,
                )
            )

        # ===== RULE 8: Gasification =====
        if not features.has_gas:
            recommendations.append(
                ServiceRecommendation(
                    service_id=0,  # Will be resolved by slug
                    service_slug='gas_connection',
                    service_name='Подключение газа',
                    priority=Priority.RECOMMENDED,
                    reason='Газ отсутствует — рекомендуется подключение к газовой сети',
                    step_order=3,
                )
            )

        # ===== RULE 9: Electricity =====
        if not features.has_electricity:
            recommendations.append(
                ServiceRecommendation(
                    service_id=0,
                    service_slug='electricity_connection',
                    service_name='Подключение электричества',
                    priority=Priority.RECOMMENDED,
                    reason='Электричество отсутствует — рекомендуется подключение к электросети',
                    step_order=3,
                )
            )

        # ===== RULE 10: Landscaping =====
        recommendations.append(
            ServiceRecommendation(
                service_id=17,
                service_slug='landscape_design',
                service_name='Ландшафтный дизайн',
                priority=Priority.OPTIONAL,
                reason='Рекомендуется ландшафтное благоустройство участка',
                step_order=6,
            )
        )

        # ===== RULE 11: Category Mismatch =====
        # If land_category is 'agricultural' but deal suggests construction/development
        if land.land_category in ('agricultural', 'сельскохозяйственная'):
            # Only add legal consultation if not already added by purchase rule
            existing_slugs = {r.service_slug for r in recommendations}
            if 'legal_consultation' not in existing_slugs:
                recommendations.append(
                    ServiceRecommendation(
                        service_id=49,
                        service_slug='legal_consultation',
                        service_name='Юридическая консультация',
                        priority=Priority.CRITICAL,
                        reason='Категория земли "сельскохозяйственная" - необходима консультация юриста для перевода категории',
                        step_order=1,
                    )
                )
            recommendations.append(
                ServiceRecommendation(
                    service_id=52,
                    service_slug='land_category_conversion',
                    service_name='Перевод категории земли',
                    priority=Priority.CRITICAL,
                    reason='Необходим перевод земли из категории "сельскохозяйственная" для строительства',
                    step_order=2,
                )
            )

        # Sort by priority and step_order
        priority_order = {
            Priority.CRITICAL: 1,
            Priority.RECOMMENDED: 2,
            Priority.OPTIONAL: 3,
        }

        recommendations.sort(
            key=lambda x: (priority_order[x.priority], x.step_order, x.service_name)
        )

        return {
            'services': recommendations,
            'summary': cls._build_summary(recommendations),
            'total_critical': len([r for r in recommendations if r.priority == Priority.CRITICAL]),
            'total_recommended': len([r for r in recommendations if r.priority == Priority.RECOMMENDED]),
            'total_optional': len([r for r in recommendations if r.priority == Priority.OPTIONAL]),
        }

    @staticmethod
    def _build_summary(recommendations: List[ServiceRecommendation]) -> str:
        """Build human-readable summary of recommendations"""
        critical = [r for r in recommendations if r.priority == Priority.CRITICAL]
        recommended = [r for r in recommendations if r.priority == Priority.RECOMMENDED]

        parts = []

        if critical:
            parts.append(f"Обязательно: {len(critical)} услуг")
            for rec in critical[:3]:
                parts.append(f"  • {rec.service_name}")

        if recommended:
            parts.append(f"Рекомендуется: {len(recommended)} услуг")
            for rec in recommended[:3]:
                parts.append(f"  • {rec.service_name}")

        return "\n".join(parts)
