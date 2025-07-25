"""
Free Models Manager for OpenRouter
=================================

Manages multiple free models with automatic fallback and dynamic switching
to handle rate limits and model availability issues.

Features:
- Multiple free model options
- Automatic fallback on rate limits/errors
- Model health monitoring
- Dynamic model switching
- User preference storage
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)

@dataclass
class PremiumModel:
    """Configuration for a premium backup model"""
    id: str
    name: str
    provider: str
    description: str
    context_window: int
    max_tokens: int
    temperature_range: Tuple[float, float]
    good_for: List[str]
    cost_info: str
    last_used: Optional[str] = None
    failure_count: int = 0
    last_failure: Optional[str] = None
    is_available: bool = True

@dataclass
class FreeModel:
    """Configuration for a free model"""
    id: str
    name: str
    provider: str
    description: str
    context_window: int
    max_tokens: int
    temperature_range: Tuple[float, float]
    good_for: List[str]  # Use cases this model excels at
    rate_limit_info: str
    last_used: Optional[str] = None
    failure_count: int = 0
    last_failure: Optional[str] = None
    is_available: bool = True

class FreeModelsManager:
    """Manages multiple free models with automatic failover"""
    
    def __init__(self):
        """Initialize the free models manager"""
        self.config_file = "config/free_models_config.json"
        self.premium_config_file = "config/premium_models_config.json"
        self.preferences_file = "config/user_model_preferences.json"
        
        # Initialize models
        self.models = self._initialize_free_models()
        self.premium_models = self._initialize_premium_models()
        
        # Load preferences
        self.current_model_id = self._load_user_preference()
        self.enable_premium_backup = os.getenv("ENABLE_PREMIUM_BACKUP", "true").lower() == "true"
        
        # Configuration
        self.failure_threshold = 3  # Switch model after 3 consecutive failures
        self.cooldown_minutes = 15  # Wait 15 minutes before retrying failed model
        
        logger.info(f"FreeModelsManager initialized with {len(self.models)} free models")
        logger.info(f"Premium backup {'enabled' if self.enable_premium_backup else 'disabled'}")
        if self.enable_premium_backup:
            logger.info(f"Available premium models: {len(self.premium_models)}")
    
    def _initialize_free_models(self) -> Dict[str, FreeModel]:
        """Initialize the list of available free models"""
        
        # Load from config file if exists, otherwise use defaults
        if os.path.exists(self.config_file):
            return self._load_models_from_config()
        
        # Default free models available on OpenRouter (Updated January 2025)
        # Note: IDs are stored WITHOUT "openrouter/" prefix - this is added by get_model_for_litellm()
        default_models = {
            # TIER 1: Top Performing Free Models (Verified Working)
            "qwen25-coder-32b": FreeModel(
                id="qwen/qwen-2.5-coder-32b-instruct:free",
                name="Qwen2.5 Coder 32B Free",
                provider="Alibaba",
                description="Latest Qwen coder model, excellent for programming tasks",
                context_window=32768,
                max_tokens=4000,
                temperature_range=(0.0, 1.0),
                good_for=["code", "programming", "technical", "analysis"],
                rate_limit_info="VERIFIED WORKING - Latest coder model with excellent performance"
            ),
            
            "llama33-70b": FreeModel(
                id="meta-llama/llama-3.3-70b-instruct:free",
                name="Llama 3.3 70B Instruct Free",
                provider="Meta",
                description="Large Meta model with excellent reasoning capabilities - MOST RELIABLE",
                context_window=131072,
                max_tokens=4000,
                temperature_range=(0.0, 1.0),
                good_for=["general", "reasoning", "analysis", "conversation", "complex"],
                rate_limit_info="VERIFIED WORKING - Most reliable 70B model, excellent stability"
            ),
            
            "mistral-small-32": FreeModel(
                id="mistralai/mistral-small-3.2-24b-instruct:free",
                name="Mistral Small 3.2 24B Free",
                provider="Mistral AI",
                description="Latest Mistral small model with improved performance",
                context_window=32768,
                max_tokens=4000,
                temperature_range=(0.0, 1.0),
                good_for=["general", "balanced", "reasoning", "analysis"],
                rate_limit_info="VERIFIED WORKING - Latest Mistral model with excellent reliability"
            ),
            
            # TIER 2: Additional Working Free Models
            "qwen25-vl-32b": FreeModel(
                id="qwen/qwen2.5-vl-32b-instruct:free",
                name="Qwen2.5 VL 32B Free",
                provider="Alibaba",
                description="Vision-language model for multimodal tasks",
                context_window=32768,
                max_tokens=4000,
                temperature_range=(0.0, 1.0),
                good_for=["vision", "multimodal", "analysis", "general"],
                rate_limit_info="VERIFIED WORKING - Vision-language capabilities"
            ),
            
            "mistral-small-31": FreeModel(
                id="mistralai/mistral-small-3.1-24b-instruct:free",
                name="Mistral Small 3.1 24B Free",
                provider="Mistral AI",
                description="Previous generation Mistral small model",
                context_window=32768,
                max_tokens=4000,
                temperature_range=(0.0, 1.0),
                good_for=["general", "balanced", "reasoning"],
                rate_limit_info="VERIFIED WORKING - Reliable Mistral 3.1 model"
            ),
            
            "dolphin-r1-24b": FreeModel(
                id="cognitivecomputations/dolphin3.0-r1-mistral-24b:free",
                name="Dolphin 3.0 R1 Mistral 24B Free",
                provider="Cognitive Computations",
                description="Uncensored reasoning model based on Mistral",
                context_window=32768,
                max_tokens=4000,
                temperature_range=(0.0, 1.0),
                good_for=["reasoning", "uncensored", "general"],
                rate_limit_info="VERIFIED WORKING - Uncensored model for flexible use"
            ),
            
            "qwen25-vl-72b": FreeModel(
                id="qwen/qwen2.5-vl-72b-instruct:free",
                name="Qwen2.5 VL 72B Free",
                provider="Alibaba",
                description="Large vision-language model",
                context_window=32768,
                max_tokens=4000,
                temperature_range=(0.0, 1.0),
                good_for=["vision", "multimodal", "analysis", "complex"],
                rate_limit_info="VERIFIED WORKING - Large VL model for complex tasks"
            ),
            
            # TIER 3: Fallback Models (Previously Working)
            "mistral-7b": FreeModel(
                id="mistralai/mistral-7b-instruct:free",
                name="Mistral 7B Instruct Free",
                provider="Mistral AI",
                description="Balanced model for general purpose tasks",
                context_window=32768,
                max_tokens=4000,
                temperature_range=(0.0, 1.0),
                good_for=["general", "balanced", "reasoning", "analysis"],
                rate_limit_info="VERIFIED WORKING - Reliable with good performance"
            ),
            
            "qwen3-coder": FreeModel(
                id="qwen/qwen3-coder:free",
                name="Qwen3 Coder Free",
                provider="Alibaba",
                description="Excellent for code generation, analysis, and technical tasks",
                context_window=32768,
                max_tokens=4000,
                temperature_range=(0.0, 1.0),
                good_for=["code", "analysis", "technical", "structured"],
                rate_limit_info="RATE LIMITED - High usage periods may have temporary limits",
                is_available=False  # Currently rate limited
            ),
            
            "llama3-8b": FreeModel(
                id="meta-llama/llama-3.1-8b-instruct:free",
                name="Llama 3.1 8B Instruct Free",
                provider="Meta",
                description="Powerful general-purpose model with excellent reasoning",
                context_window=131072,
                max_tokens=4000,
                temperature_range=(0.0, 1.0),
                good_for=["general", "reasoning", "analysis", "conversation"],
                rate_limit_info="NOT AVAILABLE - 404 errors on OpenRouter",
                is_available=False  # Permanently disabled due to 404 errors
            ),
            
            "gemma-7b": FreeModel(
                id="google/gemma-2-7b-it:free",
                name="Gemma 2 7B Instruct Free",
                provider="Google",
                description="Updated Gemma model for instruction following",
                context_window=8192,
                max_tokens=4000,
                temperature_range=(0.0, 1.0),
                good_for=["instruction", "general", "chat", "simple"],
                rate_limit_info="NOT AVAILABLE - Bad Request errors on OpenRouter",
                is_available=False  # Disabled due to 400 errors
            ),
            
            "mistral-7b": FreeModel(
                id="mistralai/mistral-7b-instruct:free",
                name="Mistral 7B Instruct Free",
                provider="Mistral AI",
                description="Balanced model for general purpose tasks",
                context_window=32768,
                max_tokens=4000,
                temperature_range=(0.0, 1.0),
                good_for=["general", "balanced", "reasoning", "analysis"],
                rate_limit_info="VERIFIED WORKING - Reliable with good performance"
            ),
            
            "phi-3": FreeModel(
                id="microsoft/phi-3-mini-128k-instruct:free",
                name="Phi-3 Mini 128K Free",
                provider="Microsoft",
                description="Efficient model with large context window",
                context_window=128000,
                max_tokens=4000,
                temperature_range=(0.0, 1.0),
                good_for=["efficient", "large_context", "general", "analysis"],
                rate_limit_info="UNTESTED - May have availability issues",
                is_available=False  # Needs verification
            )
        }
        
        # Save default configuration
        self._save_models_to_config(default_models)
        return default_models
    
    def _initialize_premium_models(self) -> Dict[str, PremiumModel]:
        """Initialize premium backup models"""
        
        # Try to load from existing config first
        if os.path.exists(self.premium_config_file):
            loaded_models = self._load_premium_models_from_config()
            if loaded_models:
                return loaded_models
        
        # Default premium backup models (from discovery results)
        premium_models = {
            "gpt-4o-mini": PremiumModel(
                id="openai/gpt-4o-mini",
                name="GPT-4o Mini",
                provider="OpenAI",
                description="Fast and cost-effective GPT model",
                context_window=128000,
                max_tokens=4000,
                temperature_range=(0.0, 2.0),
                good_for=["general", "reasoning", "coding", "analysis"],
                cost_info="Low cost - $0.15/1M tokens input, $0.60/1M tokens output"
            ),
            
            "claude-3-haiku": PremiumModel(
                id="anthropic/claude-3-haiku",
                name="Claude 3 Haiku",
                provider="Anthropic",
                description="Fast and efficient Claude model",
                context_window=200000,
                max_tokens=4000,
                temperature_range=(0.0, 1.0),
                good_for=["general", "reasoning", "analysis", "coding"],
                cost_info="Low cost - $0.25/1M tokens input, $1.25/1M tokens output"
            ),
            
            "gemini-flash-15": PremiumModel(
                id="google/gemini-flash-1.5",
                name="Gemini Flash 1.5",
                provider="Google",
                description="Fast Google Gemini model",
                context_window=1000000,
                max_tokens=4000,
                temperature_range=(0.0, 2.0),
                good_for=["general", "reasoning", "multimodal", "analysis"],
                cost_info="Low cost - $0.075/1M tokens input, $0.30/1M tokens output"
            ),
            
            "mistral-small": PremiumModel(
                id="mistralai/mistral-small",
                name="Mistral Small",
                provider="Mistral AI",
                description="Efficient Mistral model for various tasks",
                context_window=32768,
                max_tokens=4000,
                temperature_range=(0.0, 1.0),
                good_for=["general", "reasoning", "coding", "analysis"],
                cost_info="Low cost - $0.20/1M tokens input, $0.60/1M tokens output"
            )
        }
        
        # Save premium configuration
        self._save_premium_models_to_config(premium_models)
        return premium_models
    
    def _load_models_from_config(self) -> Dict[str, FreeModel]:
        """Load models configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            models = {}
            for key, model_data in data.items():
                models[key] = FreeModel(**model_data)
            
            logger.info(f"Loaded {len(models)} models from configuration")
            return models
            
        except Exception as e:
            logger.error(f"Failed to load models config: {e}")
            return {}
    
    def _save_models_to_config(self, models: Dict[str, FreeModel]):
        """Save models configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            data = {}
            for key, model in models.items():
                data[key] = asdict(model)
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save models config: {e}")
    
    def _load_premium_models_from_config(self) -> Dict[str, PremiumModel]:
        """Load premium models configuration from file"""
        try:
            with open(self.premium_config_file, 'r') as f:
                data = json.load(f)
            
            models = {}
            for key, model_data in data.items():
                models[key] = PremiumModel(**model_data)
            
            logger.info(f"Loaded {len(models)} premium models from configuration")
            return models
            
        except Exception as e:
            logger.error(f"Failed to load premium models config: {e}")
            return {}
    
    def _save_premium_models_to_config(self, models: Dict[str, PremiumModel]):
        """Save premium models configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.premium_config_file), exist_ok=True)
            
            data = {}
            for key, model in models.items():
                data[key] = asdict(model)
            
            with open(self.premium_config_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save premium models config: {e}")
    
    def _load_user_preference(self) -> str:
        """Load user's preferred model from preferences file"""
        try:
            if os.path.exists(self.preferences_file):
                with open(self.preferences_file, 'r') as f:
                    prefs = json.load(f)
                    return prefs.get('default_model', 'llama33-70b')
        except Exception as e:
            logger.error(f"Failed to load user preferences: {e}")
        
        return 'llama33-70b'  # Default to most reliable model (Llama 3.3 70B)
    
    def save_user_preference(self, model_key: str):
        """Save user's preferred model"""
        try:
            os.makedirs(os.path.dirname(self.preferences_file), exist_ok=True)
            
            prefs = {
                'default_model': model_key,
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.preferences_file, 'w') as f:
                json.dump(prefs, f, indent=2)
            
            self.current_model_id = model_key
            logger.info(f"Saved user preference for model: {model_key}")
            
        except Exception as e:
            logger.error(f"Failed to save user preferences: {e}")
    
    def get_available_models(self) -> Dict[str, FreeModel]:
        """Get all available models for UI display"""
        return self.models
    
    def get_working_models(self) -> Dict[str, FreeModel]:
        """Get only models that are currently available and working"""
        working = {}
        for key, model in self.models.items():
            if self._is_model_available(model):
                working[key] = model
        return working
    
    def get_current_model(self) -> FreeModel:
        """Get the currently selected model"""
        return self.models.get(self.current_model_id, list(self.models.values())[0])
    
    def get_model_for_litellm(self, use_case: str = "general") -> str:
        """Get model ID formatted for LiteLLM (with openrouter/ prefix)"""
        model = self.get_best_available_model(use_case)
        
        # Check if it's a premium model (has cost_info attribute)
        if hasattr(model, 'cost_info'):
            # Premium model - no openrouter prefix needed for most premium providers
            if model.id.startswith('openai/') or model.id.startswith('anthropic/') or model.id.startswith('google/'):
                return model.id  # These providers use direct model IDs in LiteLLM
            else:
                return f"openrouter/{model.id}"  # Other providers still need openrouter prefix
        else:
            # Free model - always needs openrouter prefix
            return f"openrouter/{model.id}"
    
    def get_model_for_openrouter_client(self, use_case: str = "general") -> str:
        """Get model ID formatted for OpenRouter client (without prefix)"""
        model = self.get_best_available_model(use_case)
        return model.id
    
    def get_best_available_model(self, use_case: str = "general"):
        """Get the best available model for a specific use case"""
        
        # First, try current user preference if it's available and suitable
        current = self.models.get(self.current_model_id)
        if current and self._is_model_available(current) and (use_case in current.good_for or use_case == "general"):
            return current
        
        # Find models good for this use case, sorted by availability and performance
        suitable_models = []
        for model in self.models.values():
            if self._is_model_available(model) and (use_case in model.good_for or use_case == "general"):
                # Score based on availability and recent performance
                score = self._calculate_model_score(model)
                suitable_models.append((score, model))
        
        if suitable_models:
            # Sort by score (higher is better) and return the best
            suitable_models.sort(reverse=True, key=lambda x: x[0])
            return suitable_models[0][1]
        
        # Fallback to any available free model
        available_models = [m for m in self.models.values() if self._is_model_available(m)]
        if available_models:
            return available_models[0]
        
        # If no free models available and premium backup is enabled, use premium
        if self.enable_premium_backup and self.premium_models:
            logger.warning("⚠️  All free models failed, switching to premium backup")
            return self.get_best_premium_model(use_case)
        
        # Emergency fallback - return current model even if it might be failing
        logger.error("❌ No working models available, using current as emergency fallback")
        return self.get_current_model()
    
    def get_best_premium_model(self, use_case: str = "general"):
        """Get the best available premium backup model"""
        suitable_premium = []
        
        for model in self.premium_models.values():
            if self._is_premium_model_available(model) and (use_case in model.good_for or use_case == "general"):
                score = self._calculate_premium_model_score(model)
                suitable_premium.append((score, model))
        
        if suitable_premium:
            suitable_premium.sort(reverse=True, key=lambda x: x[0])
            best_premium = suitable_premium[0][1]
            logger.info(f"🎯 Using premium backup: {best_premium.name} ({best_premium.cost_info})")
            return best_premium
        
        # If no suitable premium models, return the first available one
        if self.premium_models:
            first_premium = list(self.premium_models.values())[0]
            logger.warning(f"⚠️  Using first available premium model: {first_premium.name}")
            return first_premium
        
        # This should never happen if premium models are configured
        raise Exception("No premium backup models available")
    
    def _is_premium_model_available(self, model) -> bool:
        """Check if a premium model is available (similar to free model check)"""
        if not hasattr(model, 'is_available') or not model.is_available:
            return True  # Assume premium models are generally available
        
        # Check cooldown for premium models too
        if hasattr(model, 'failure_count') and model.failure_count >= self.failure_threshold:
            if hasattr(model, 'last_failure') and model.last_failure:
                try:
                    last_failure_time = datetime.fromisoformat(model.last_failure)
                    if datetime.now() - last_failure_time < timedelta(minutes=self.cooldown_minutes):
                        return False
                except:
                    pass
        
        return True
    
    def _calculate_premium_model_score(self, model) -> float:
        """Calculate score for premium model selection"""
        score = 100.0
        
        # Premium models get a base higher score
        score += 50
        
        # Prefer lower cost models
        if hasattr(model, 'cost_info'):
            if "Low cost" in model.cost_info:
                score += 30
            elif "Medium cost" in model.cost_info:
                score += 15
        
        # Penalize recent failures if tracked
        if hasattr(model, 'failure_count'):
            score -= model.failure_count * 5  # Less penalty than free models
        
        return score
    
    def _is_model_available(self, model: FreeModel) -> bool:
        """Check if a model is currently available"""
        if not model.is_available:
            return False
        
        # If model has recent failures, check if cooldown period has passed
        if model.failure_count >= self.failure_threshold and model.last_failure:
            try:
                last_failure_time = datetime.fromisoformat(model.last_failure)
                if datetime.now() - last_failure_time < timedelta(minutes=self.cooldown_minutes):
                    return False
            except:
                pass
        
        return True
    
    def _calculate_model_score(self, model: FreeModel) -> float:
        """Calculate a score for model selection (higher is better)"""
        score = 100.0
        
        # Penalize recent failures
        score -= model.failure_count * 10
        
        # Prefer recently successful models
        if model.last_used:
            try:
                last_used_time = datetime.fromisoformat(model.last_used)
                hours_since_use = (datetime.now() - last_used_time).total_seconds() / 3600
                if hours_since_use < 1:  # Used in last hour
                    score += 20
                elif hours_since_use < 24:  # Used in last day
                    score += 10
            except:
                pass
        
        # Prefer larger context windows for complex tasks
        score += min(model.context_window / 1000, 50)  # Up to 50 points for context
        
        return score
    
    def handle_model_failure(self, model_id: str, error_type: str = "unknown"):
        """Handle when a model fails - update failure count and try next model"""
        
        # Find model by ID (could be with or without openrouter/ prefix)
        model_key = None
        clean_id = model_id.replace("openrouter/", "")
        
        for key, model in self.models.items():
            if model.id == clean_id:
                model_key = key
                break
        
        if model_key:
            model = self.models[model_key]
            model.failure_count += 1
            model.last_failure = datetime.now().isoformat()
            
            logger.warning(f"Model {model.name} failed ({error_type}). Failure count: {model.failure_count}")
            
            # If this was the current model, switch to next best available
            if model_key == self.current_model_id:
                next_model = self.get_best_available_model()
                if next_model.id != model.id:
                    old_name = model.name
                    self.current_model_id = self._get_model_key_by_id(next_model.id)
                    logger.info(f"Switched from {old_name} to {next_model.name} due to failures")
            
            # Save updated configuration
            self._save_models_to_config(self.models)
            
            return self.get_current_model()
        
        return None
    
    def handle_model_success(self, model_id: str):
        """Handle when a model succeeds - reset failure count and update last used"""
        
        clean_id = model_id.replace("openrouter/", "")
        
        for key, model in self.models.items():
            if model.id == clean_id:
                model.failure_count = 0  # Reset failure count on success
                model.last_used = datetime.now().isoformat()
                model.is_available = True
                
                # Save updated configuration
                self._save_models_to_config(self.models)
                
                logger.debug(f"Model {model.name} successful - reset failure count")
                break
    
    def _get_model_key_by_id(self, model_id: str) -> str:
        """Get model key by model ID"""
        clean_id = model_id.replace("openrouter/", "")
        for key, model in self.models.items():
            if model.id == clean_id:
                return key
        return list(self.models.keys())[0]  # Fallback to first model
    
    def get_model_status_summary(self) -> Dict:
        """Get summary of all models for monitoring/debugging"""
        summary = {
            "total_models": len(self.models),
            "available_models": len([m for m in self.models.values() if self._is_model_available(m)]),
            "current_model": self.get_current_model().name,
            "models": {}
        }
        
        for key, model in self.models.items():
            summary["models"][key] = {
                "name": model.name,
                "available": self._is_model_available(model),
                "failure_count": model.failure_count,
                "last_used": model.last_used,
                "last_failure": model.last_failure
            }
        
        return summary
    
    def reset_model_failures(self, model_key: str = None):
        """Reset failure counts (for manual recovery)"""
        if model_key:
            if model_key in self.models:
                self.models[model_key].failure_count = 0
                self.models[model_key].last_failure = None
                self.models[model_key].is_available = True
                logger.info(f"Reset failures for model: {self.models[model_key].name}")
        else:
            # Reset all models
            for model in self.models.values():
                model.failure_count = 0
                model.last_failure = None
                model.is_available = True
            logger.info("Reset failures for all models")
        
        self._save_models_to_config(self.models)


# Global instance
_free_models_manager = None

def get_free_models_manager() -> FreeModelsManager:
    """Get the global free models manager instance"""
    global _free_models_manager
    if _free_models_manager is None:
        _free_models_manager = FreeModelsManager()
    return _free_models_manager

def get_current_free_model_for_litellm(use_case: str = "general") -> str:
    """Convenience function to get current model for LiteLLM"""
    return get_free_models_manager().get_model_for_litellm(use_case)

def get_current_free_model_for_openrouter(use_case: str = "general") -> str:
    """Convenience function to get current model for OpenRouter client"""
    return get_free_models_manager().get_model_for_openrouter_client(use_case)

def handle_api_failure(model_id: str, error_type: str = "unknown"):
    """Convenience function to handle API failures"""
    return get_free_models_manager().handle_model_failure(model_id, error_type)

def handle_api_success(model_id: str):
    """Convenience function to handle API success"""
    get_free_models_manager().handle_model_success(model_id)
