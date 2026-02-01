"""Skill loader - Dynamic skill discovery and loading"""

import importlib
import importlib.util
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional
from .base import Skill

logger = logging.getLogger(__name__)


class SkillLoader:
    """Load and manage skills dynamically"""

    def __init__(self, skills_directory: str = "./skills"):
        self.skills_directory = Path(skills_directory)
        self.skills: Dict[str, Skill] = {}
        self.skills_directory.mkdir(parents=True, exist_ok=True)

    def discover_skills(self) -> List[Path]:
        """
        Discover skill modules in skills directory

        Looks for:
        - skills/*.py files
        - skills/*/skill.py modules

        Returns:
            List of paths to skill modules
        """
        discovered = []

        # Find .py files in skills directory
        for file in self.skills_directory.glob("*.py"):
            if file.name != "__init__.py":
                discovered.append(file)

        # Find skill.py in subdirectories
        for dir in self.skills_directory.glob("*/"):
            if dir.is_dir():
                skill_file = dir / "skill.py"
                if skill_file.exists():
                    discovered.append(skill_file)

        return discovered

    def load_skill_from_file(self, file_path: Path) -> Optional[Skill]:
        """
        Load a skill from a Python file

        Args:
            file_path: Path to skill module

        Returns:
            Skill instance or None if failed
        """
        try:
            # Generate module name
            module_name = f"ultron_skill_{file_path.stem}"

            # Load module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                logger.error(f"Failed to load spec for {file_path}")
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find Skill subclass
            skill_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, Skill) and
                    attr is not Skill):
                    skill_class = attr
                    break

            if skill_class is None:
                logger.warning(f"No Skill class found in {file_path}")
                return None

            # Instantiate skill
            skill = skill_class()
            logger.info(f"Loaded skill: {skill.name()} from {file_path}")
            return skill

        except Exception as e:
            logger.error(f"Error loading skill from {file_path}: {e}", exc_info=True)
            return None

    def load_all_skills(self) -> int:
        """
        Load all skills from skills directory

        Returns:
            Number of skills loaded
        """
        discovered = self.discover_skills()
        logger.info(f"Discovered {len(discovered)} skill module(s)")

        loaded_count = 0
        for file_path in discovered:
            skill = self.load_skill_from_file(file_path)
            if skill:
                self.register_skill(skill)
                loaded_count += 1

        logger.info(f"Loaded {loaded_count} skill(s)")
        return loaded_count

    def register_skill(self, skill: Skill):
        """Register a skill"""
        self.skills[skill.name()] = skill
        logger.info(f"Registered skill: {skill.name()}")

    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name"""
        return self.skills.get(name)

    def list_skills(self) -> Dict[str, str]:
        """List all registered skills"""
        return {name: skill.description() for name, skill in self.skills.items()}

    def get_all_skills(self) -> List[Skill]:
        """Get all registered skills"""
        return list(self.skills.values())

    def reload_skill(self, name: str) -> bool:
        """
        Reload a skill (hot-reload)

        Args:
            name: Skill name to reload

        Returns:
            True if reloaded successfully
        """
        # Find the skill file
        for file_path in self.discover_skills():
            skill = self.load_skill_from_file(file_path)
            if skill and skill.name() == name:
                self.register_skill(skill)
                return True
        return False


# Global skill loader instance
_skill_loader: Optional[SkillLoader] = None


def get_skill_loader(skills_directory: str = "./skills") -> SkillLoader:
    """Get or create global skill loader instance"""
    global _skill_loader
    if _skill_loader is None:
        _skill_loader = SkillLoader(skills_directory)
    return _skill_loader
