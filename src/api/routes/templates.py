"""Template management endpoints

Lists and provides access to built-in scenario templates.
"""

from pathlib import Path
from typing import List

import yaml
from fastapi import APIRouter, HTTPException, status

from ..schemas import TemplateInfo, TemplateListResponse

router = APIRouter(prefix="/api/templates", tags=["templates"])


def get_templates_directory() -> Path:
    """Get the path to the templates directory"""
    # Navigate from src/api/routes to project root
    project_root = Path(__file__).parent.parent.parent.parent
    return project_root / "data" / "scenarios"


@router.get("", response_model=TemplateListResponse)
async def list_templates() -> TemplateListResponse:
    """List all available scenario templates

    Returns all YAML template files from data/scenarios directory.
    """
    templates_dir = get_templates_directory()

    if not templates_dir.exists():
        return TemplateListResponse(templates=[], total=0)

    templates = []
    for yaml_file in templates_dir.glob("*.yaml"):
        try:
            with open(yaml_file, 'r') as f:
                config = yaml.safe_load(f)

            # Extract description from config if available
            description = None
            if isinstance(config, dict):
                description = config.get('description')

            templates.append(TemplateInfo(
                name=yaml_file.stem,  # Filename without extension
                path=str(yaml_file.relative_to(templates_dir.parent.parent)),
                description=description,
                config=config
            ))
        except Exception as e:
            # Skip files that can't be parsed
            print(f"Warning: Could not load template {yaml_file}: {e}")
            continue

    return TemplateListResponse(
        templates=sorted(templates, key=lambda t: t.name),
        total=len(templates)
    )


@router.get("/{template_name}", response_model=TemplateInfo)
async def get_template(template_name: str) -> TemplateInfo:
    """Get specific template by name

    Returns the configuration for a specific template.
    """
    templates_dir = get_templates_directory()
    template_path = templates_dir / f"{template_name}.yaml"

    if not template_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{template_name}' not found"
        )

    try:
        with open(template_path, 'r') as f:
            config = yaml.safe_load(f)

        description = None
        if isinstance(config, dict):
            description = config.get('description')

        return TemplateInfo(
            name=template_name,
            path=str(template_path.relative_to(templates_dir.parent.parent)),
            description=description,
            config=config
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading template: {str(e)}"
        )
