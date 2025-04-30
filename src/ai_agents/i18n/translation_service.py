"""
Internationalization (i18n) system for multilingual support in the Property Investment Analysis App
"""
from typing import Dict, Optional, Any, List
import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class TranslationService:
    """
    Service for managing translations for UI elements and prompts
    """
    _instance = None
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super(TranslationService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the translation service"""
        if self._initialized:
            return
            
        self._translations = {}
        self._prompt_templates = {}
        self._default_language = "en"
        self._available_languages = ["en", "de"]
        self._load_translations()
        self._initialized = True
    
    def _load_translations(self):
        """Load translations from files"""
        # Get the path to the translations directory
        translations_dir = Path(__file__).parent / "translations"
        
        # Check if the directory exists, if not create it
        if not translations_dir.exists():
            translations_dir.mkdir(parents=True)
            logger.warning(f"Created translations directory at {translations_dir}")
        
        # Load UI translations
        for lang in self._available_languages:
            ui_file = translations_dir / f"ui_{lang}.json"
            prompt_file = translations_dir / f"prompts_{lang}.json"
            
            # Load UI translations if the file exists
            if ui_file.exists():
                with open(ui_file, 'r', encoding='utf-8') as f:
                    self._translations[lang] = json.load(f)
                logger.info(f"Loaded UI translations for {lang}")
            else:
                self._translations[lang] = {}
                logger.warning(f"UI translation file for {lang} not found at {ui_file}")
            
            # Load prompt templates if the file exists
            if prompt_file.exists():
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    self._prompt_templates[lang] = json.load(f)
                logger.info(f"Loaded prompt templates for {lang}")
            else:
                self._prompt_templates[lang] = {}
                logger.warning(f"Prompt template file for {lang} not found at {prompt_file}")
    
    def get_translation(self, key: str, language: Optional[str] = None) -> str:
        """
        Get translation for a specific key in the specified language
        
        Args:
            key (str): Translation key
            language (str, optional): Language code (e.g., 'en', 'de'). Defaults to default language.
            
        Returns:
            str: Translated text or the key itself if translation not found
        """
        lang = language or self._default_language
        
        # Fall back to default language if requested language not available
        if lang not in self._available_languages:
            logger.warning(f"Language {lang} not available, falling back to {self._default_language}")
            lang = self._default_language
        
        # Get translation or fall back to key
        return self._translations.get(lang, {}).get(key, key)
    
    def get_prompt_template(self, template_name: str, language: Optional[str] = None) -> str:
        """
        Get prompt template in the specified language
        
        Args:
            template_name (str): Template name
            language (str, optional): Language code (e.g., 'en', 'de'). Defaults to default language.
            
        Returns:
            str: Prompt template or empty string if not found
        """
        lang = language or self._default_language
        
        # Fall back to default language if requested language not available
        if lang not in self._available_languages:
            logger.warning(f"Language {lang} not available, falling back to {self._default_language}")
            lang = self._default_language
        
        # Get template or fall back to default language or empty string
        template = self._prompt_templates.get(lang, {}).get(template_name)
        if template is None and lang != self._default_language:
            template = self._prompt_templates.get(self._default_language, {}).get(template_name, "")
            if template:
                logger.warning(f"Prompt template {template_name} not found in {lang}, falling back to {self._default_language}")
        
        return template or ""
    
    def get_available_languages(self) -> List[str]:
        """Get list of available languages"""
        return self._available_languages
    
    def set_default_language(self, language: str) -> None:
        """Set default language"""
        if language in self._available_languages:
            self._default_language = language
        else:
            logger.warning(f"Language {language} not available, default language not changed")
    
    def add_translation(self, key: str, translations: Dict[str, str]) -> None:
        """
        Add or update translations for a key
        
        Args:
            key (str): Translation key
            translations (Dict[str, str]): Dictionary mapping language codes to translations
        """
        for lang, translation in translations.items():
            if lang in self._available_languages:
                if lang not in self._translations:
                    self._translations[lang] = {}
                self._translations[lang][key] = translation
            else:
                logger.warning(f"Language {lang} not available, translation not added")
    
    def add_prompt_template(self, template_name: str, templates: Dict[str, str]) -> None:
        """
        Add or update prompt templates
        
        Args:
            template_name (str): Template name
            templates (Dict[str, str]): Dictionary mapping language codes to templates
        """
        for lang, template in templates.items():
            if lang in self._available_languages:
                if lang not in self._prompt_templates:
                    self._prompt_templates[lang] = {}
                self._prompt_templates[lang][template_name] = template
            else:
                logger.warning(f"Language {lang} not available, template not added")
    
    def save_translations(self) -> None:
        """Save translations to files"""
        translations_dir = Path(__file__).parent / "translations"
        
        # Create directory if it doesn't exist
        if not translations_dir.exists():
            translations_dir.mkdir(parents=True)
        
        # Save UI translations
        for lang in self._available_languages:
            if lang in self._translations:
                ui_file = translations_dir / f"ui_{lang}.json"
                with open(ui_file, 'w', encoding='utf-8') as f:
                    json.dump(self._translations[lang], f, ensure_ascii=False, indent=2)
                logger.info(f"Saved UI translations for {lang}")
        
        # Save prompt templates
        for lang in self._available_languages:
            if lang in self._prompt_templates:
                prompt_file = translations_dir / f"prompts_{lang}.json"
                with open(prompt_file, 'w', encoding='utf-8') as f:
                    json.dump(self._prompt_templates[lang], f, ensure_ascii=False, indent=2)
                logger.info(f"Saved prompt templates for {lang}")

class PromptTemplateManager:
    """
    Manager for system prompts for different agent roles in multiple languages
    """
    
    def __init__(self, translation_service: Optional[TranslationService] = None):
        """
        Initialize the prompt template manager
        
        Args:
            translation_service (TranslationService, optional): Translation service instance.
                If None, a new instance will be created.
        """
        self.translation_service = translation_service or TranslationService()
        
        # Default prompt templates for each agent role and user expertise level
        self._default_templates = {
            "manager_agent": {
                "beginner": "manager_agent_beginner",
                "intermediate": "manager_agent_intermediate",
                "expert": "manager_agent_expert"
            },
            "market_data_agent": {
                "beginner": "market_data_agent_beginner",
                "intermediate": "market_data_agent_intermediate",
                "expert": "market_data_agent_expert"
            },
            "rent_estimation_agent": {
                "beginner": "rent_estimation_agent_beginner",
                "intermediate": "rent_estimation_agent_intermediate",
                "expert": "rent_estimation_agent_expert"
            },
            "document_analysis_agent": {
                "beginner": "document_analysis_agent_beginner",
                "intermediate": "document_analysis_agent_intermediate",
                "expert": "document_analysis_agent_expert"
            },
            "risk_analysis_agent": {
                "beginner": "risk_analysis_agent_beginner",
                "intermediate": "risk_analysis_agent_intermediate",
                "expert": "risk_analysis_agent_expert"
            },
            "strategy_agent": {
                "beginner": "strategy_agent_beginner",
                "intermediate": "strategy_agent_intermediate",
                "expert": "strategy_agent_expert"
            }
        }
    
    def get_prompt_template(self, agent_type: str, language: str, expertise_level: str = "beginner") -> str:
        """
        Get the appropriate prompt template for an agent based on language and expertise level
        
        Args:
            agent_type (str): Type of agent (e.g., 'manager_agent', 'market_data_agent')
            language (str): Language code (e.g., 'en', 'de')
            expertise_level (str, optional): User expertise level. Defaults to 'beginner'.
            
        Returns:
            str: Prompt template
        """
        # Validate expertise level
        if expertise_level not in ["beginner", "intermediate", "expert"]:
            logger.warning(f"Invalid expertise level: {expertise_level}, falling back to beginner")
            expertise_level = "beginner"
        
        # Get template name based on agent type and expertise level
        template_name = self._default_templates.get(agent_type, {}).get(expertise_level)
        
        if not template_name:
            logger.warning(f"No template found for agent type: {agent_type} and expertise level: {expertise_level}")
            # Fall back to manager agent beginner template
            template_name = "manager_agent_beginner"
        
        # Get the actual template from the translation service
        template = self.translation_service.get_prompt_template(template_name, language)
        
        if not template:
            logger.warning(f"No template content found for {template_name} in language: {language}")
            # Generate a basic template as fallback
            template = self._generate_fallback_template(agent_type, expertise_level)
        
        return template
    
    def _generate_fallback_template(self, agent_type: str, expertise_level: str) -> str:
        """
        Generate a basic fallback template when no template is found
        
        Args:
            agent_type (str): Type of agent
            expertise_level (str): User expertise level
            
        Returns:
            str: Basic template
        """
        return f"""You are an AI assistant specializing in property investment analysis, acting as a {agent_type.replace('_', ' ')}.
Your task is to help users with their property investment decisions.
Adapt your explanations to a {expertise_level} level of expertise.
Provide clear, concise, and accurate information."""

# Create translations directory and default translation files
def create_default_translations():
    """Create default translation files if they don't exist"""
    translations_dir = Path(__file__).parent / "translations"
    
    # Create directory if it doesn't exist
    if not translations_dir.exists():
        translations_dir.mkdir(parents=True)
        logger.info(f"Created translations directory at {translations_dir}")
    
    # Default UI translations
    default_ui_translations = {
        "en": {
            "app_title": "Property Investment Analysis",
            "property_details": "Property Details",
            "financial_details": "Financial Details",
            "analysis_results": "Analysis Results",
            "cash_flow": "Cash Flow",
            "roi": "Return on Investment",
            "cap_rate": "Capitalization Rate",
            "error_message": "An error occurred. Please try again.",
            # Add more translations as needed
        },
        "de": {
            "app_title": "Immobilieninvestitionsanalyse",
            "property_details": "Immobiliendetails",
            "financial_details": "Finanzielle Details",
            "analysis_results": "Analyseergebnisse",
            "cash_flow": "Cashflow",
            "roi": "Kapitalrendite",
            "cap_rate": "Kapitalisierungsrate",
            "error_message": "Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut.",
            # Add more translations as needed
        }
    }
    
    # Create or update UI translation files
    for lang, translations in default_ui_translations.items():
        ui_file = translations_dir / f"ui_{lang}.json"
        if not ui_file.exists():
            with open(ui_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)
            logger.info(f"Created default UI translations for {lang}")
    
    # Create sample prompt templates
    default_prompt_templates = {
        "en": {
            "manager_agent_beginner": """You are a helpful Property Investment Analysis Assistant.
Your task is to guide the user through the property investment analysis process.
The user has a BEGINNER level of expertise, so explain concepts in simple terms and avoid jargon.
Provide step-by-step guidance and clear explanations.""",
            
            "manager_agent_intermediate": """You are a Property Investment Analysis Assistant.
Your task is to guide the user through the property investment analysis process.
The user has an INTERMEDIATE level of expertise, so you can use more technical terms.
Focus on providing detailed analysis and actionable insights.""",
            
            "manager_agent_expert": """You are a Property Investment Analysis Assistant.
Your task is to guide the user through the property investment analysis process.
The user has an EXPERT level of expertise, so you can use technical terms and advanced concepts.
Focus on providing sophisticated analysis, market insights, and optimization strategies."""
        },
        "de": {
            "manager_agent_beginner": """Sie sind ein hilfreicher Assistent für Immobilieninvestitionsanalyse.
Ihre Aufgabe ist es, den Benutzer durch den Prozess der Immobilieninvestitionsanalyse zu führen.
Der Benutzer hat ein ANFÄNGER-Niveau, daher erklären Sie Konzepte in einfachen Worten und vermeiden Fachjargon.
Bieten Sie schrittweise Anleitung und klare Erklärungen.""",
            
            "manager_agent_intermediate": """Sie sind ein Assistent für Immobilieninvestitionsanalyse.
Ihre Aufgabe ist es, den Benutzer durch den Prozess der Immobilieninvestitionsanalyse zu führen.
Der Benutzer hat ein FORTGESCHRITTENES Niveau, daher können Sie mehr Fachbegriffe verwenden.
Konzentrieren Sie sich auf detaillierte Analysen und umsetzbare Erkenntnisse.""",
            
            "manager_agent_expert": """Sie sind ein Assistent für Immobilieninvestitionsanalyse.
Ihre Aufgabe ist es, den Benutzer durch den Prozess der Immobilieninvestitionsanalyse zu führen.
Der Benutzer hat ein EXPERTEN-Niveau, daher können Sie Fachbegriffe und fortgeschrittene Konzepte verwenden.
Konzentrieren Sie sich auf anspruchsvolle Analysen, Markteinblicke und Optimierungsstrategien."""
        }
    }
    
    # Create or update prompt template files
    for lang, templates in default_prompt_templates.items():
        prompt_file = translations_dir / f"prompts_{lang}.json"
        if not prompt_file.exists():
            with open(prompt_file, 'w', encoding='utf-8') as f:
                json.dump(templates, f, ensure_ascii=False, indent=2)
            logger.info(f"Created default prompt templates for {lang}")

# Create default translations when the module is imported
create_default_translations()

# Singleton instances
translation_service = TranslationService()
prompt_template_manager = PromptTemplateManager(translation_service)