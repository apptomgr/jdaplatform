from django import template

register = template.Library()

FEATURE_TRANSLATIONS = {
    "fr": {
        "Newsletters": "Newsletters",
        "IPO Review": "Analyse des introductions en bourse",
        "IPO Reviews": "Analyse des introductions en bourse",
        "IPO Analysis": "Analyse des OPV",
        "Recommendations": "Recommandations",
        "Top 10 Buy": "Top 10 Achats",
        "Top 10 Sell": "Top 10 Ventes",
        "Stock Opinion": "Avis sur valeur",
        "Quarterly Results Commentary": "Commentaires des résultats trimestriels",
        "Half Year Results Commentary": "Commentaires des résultats semestriels",
        "Annual Results Commentary": "Commentaires des résultats annuels",
        "General Meetings Commentary": "Commentaires des assemblées générales",
        "Stock Pitch": "Stock Pitch",
        "Analyst Access": "Accès analyste",
        "Research Notes": "Notes de recherche",
        "Economic Notes": "Notes économiques",
        "Opinion on all stocks": "Avis sur toutes les valeurs",
        "Access to all publications available on the platform": "Accès à toutes les publications disponibles sur la plateforme",
        "Corporate Access": "Accès corporate",
    }
}


@register.filter
def translate_feature(value, language_code=None):
    from django.utils.translation import get_language
    lang = language_code or get_language() or 'en'
    if lang.startswith('fr'):
        translations = FEATURE_TRANSLATIONS.get('fr', {})
        return translations.get(value, value)
    return value
