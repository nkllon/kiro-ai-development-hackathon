"""
Generators Models

This module was extracted from generators.py
as part of RM-DDD compliance refactoring.
"""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, Union
from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import DomainException, ModuleStatus, ModuleCapability
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
import re
from ..core.health import ModuleHealth
from ..models import DomainBoundaries
import re

class EntityTemplate(CodeTemplate):
    """Template for generating domain entities."""

    def __init__(self):
        self.template_content = '"""\n{{ name }} entity for {{ domain_context }} domain.\n\nGenerated at {{ generated_at }}.\n"""\n\nfrom typing import Any, Dict, List, Optional\nfrom uuid import UUID\nfrom datetime import datetime\n\nfrom rm_ddd import Entity, ValidationResult, DomainBoundaries\nfrom rm_ddd.decorators import domain_entity\n\n\n@domain_entity("{{ domain_context }}")\nclass {{ name }}(Entity[{{ id_type }}]):\n    """{{ description }}"""\n    \n    def __init__(self, {{ constructor_params }}):\n        super().__init__({{ id_param }}, "{{ domain_context }}")\n        {% for attr in attributes -%}\n        self.{{ attr.name }} = {{ attr.name }}\n        {% endfor %}\n    \n    {% for method in methods -%}\n    def {{ method.name }}(self{{ method.params }}):\n        """{{ method.description }}"""\n        {% if method.body -%}\n        {{ method.body | indent(8) }}\n        {% else -%}\n        pass\n        {% endif %}\n    \n    {% endfor -%}\n    \n    def get_domain_boundaries(self) -> DomainBoundaries:\n        """Get domain boundaries for this entity."""\n        return DomainBoundaries(\n            context="{{ domain_context }}",\n            invariants=[\n                {% for constraint in constraints -%}\n                "{{ constraint }}",\n                {% endfor %}\n            ]\n        )\n    \n    def validate_domain_invariants(self) -> ValidationResult:\n        """Validate domain invariants for this entity."""\n        result = ValidationResult(is_valid=True)\n        \n        {% for constraint in constraints -%}\n        # Validate: {{ constraint }}\n        # TODO: Implement validation logic\n        \n        {% endfor -%}\n        \n        return result\n'

    def generate(self, spec: GenerationSpec) -> GeneratedCode:
        """Generate entity code."""
        if not JINJA2_AVAILABLE:
            raise DomainException('Jinja2 is required for code generation but not available', error_code='JINJA2_NOT_AVAILABLE')
        validation_result = spec.validate_spec()
        if not validation_result.is_valid:
            raise DomainException(f'Invalid generation spec: {validation_result.errors}', error_code='INVALID_GENERATION_SPEC')
        context = self._prepare_context(spec)
        template = Template(self.template_content)
        code = template.render(**context)
        file_path = f'{spec.domain_context}/{spec.name.lower()}.py'
        return GeneratedCode(target_type=GenerationTarget.ENTITY, name=spec.name, code=code, file_path=file_path, imports=self._get_imports(spec), dependencies=self._get_dependencies(spec))

    def get_supported_target(self) -> GenerationTarget:
        """Get supported target type."""
        return GenerationTarget.ENTITY

    def _prepare_context(self, spec: GenerationSpec) -> Dict[str, Any]:
        """Prepare template context from spec."""
        id_attr = next((attr for attr in spec.attributes if attr.get('is_id', False)), None)
        if id_attr:
            id_type = id_attr['type']
            id_param = id_attr['name']
        else:
            id_type = 'str'
            id_param = f'{spec.name.lower()}_id'
        constructor_params = []
        if id_param not in [attr['name'] for attr in spec.attributes]:
            constructor_params.append(f'{id_param}: {id_type}')
        for attr in spec.attributes:
            if not attr.get('is_id', False):
                attr_type = attr.get('type', 'Any')
                optional = attr.get('optional', False)
                if optional:
                    attr_type = f'Optional[{attr_type}]'
                    constructor_params.append(f"{attr['name']}: {attr_type} = None")
                else:
                    constructor_params.append(f"{attr['name']}: {attr_type}")
        return {'name': spec.name, 'domain_context': spec.domain_context, 'description': spec.metadata.get('description', f'{spec.name} domain entity'), 'id_type': id_type, 'id_param': id_param, 'constructor_params': ', '.join(constructor_params), 'attributes': spec.attributes, 'methods': spec.methods, 'constraints': spec.constraints, 'generated_at': datetime.now().isoformat()}

    def _get_imports(self, spec: GenerationSpec) -> List[str]:
        """Get required imports for the generated code."""
        imports = ['from typing import Any, Dict, List, Optional', 'from rm_ddd import Entity, ValidationResult, DomainBoundaries', 'from rm_ddd.decorators import domain_entity']
        for attr in spec.attributes:
            attr_type = attr.get('type', '')
            if 'UUID' in attr_type:
                imports.append('from uuid import UUID')
            elif 'datetime' in attr_type:
                imports.append('from datetime import datetime')
        return list(set(imports))

    def _get_dependencies(self, spec: GenerationSpec) -> List[str]:
        """Get dependencies for the generated code."""
        dependencies = ['rm_ddd']
        for rel in spec.relationships:
            if 'target_entity' in rel:
                dependencies.append(rel['target_entity'])
        return dependencies

class EnhancedEntityTemplate(CustomizableCodeTemplate):
    """Enhanced entity template with customization support."""

    def __init__(self, template_registry: TemplateRegistry):
        super().__init__(template_registry)
        self._register_default_extensions()

    def _register_default_extensions(self):
        """Register default extension points."""
        self.add_extension_point('validation_rules', self._add_validation_rules)
        self.add_extension_point('business_methods', self._add_business_methods)
        self.add_extension_point('event_generation', self._add_event_generation)

    def generate(self, spec: GenerationSpec) -> GeneratedCode:
        """Generate entity code with customization support."""
        custom_template = self.get_custom_template(f'entity_{spec.name.lower()}')
        if not custom_template:
            custom_template = self.get_custom_template('entity_default')
        if custom_template:
            return self._generate_with_custom_template(custom_template, spec)
        else:
            return self._generate_with_default_template(spec)

    def _generate_with_custom_template(self, template: Template, spec: GenerationSpec) -> GeneratedCode:
        """Generate code using a custom template."""
        context = self._prepare_base_context(spec)
        context = self.apply_extensions(context, spec)
        code = template.render(**context)
        return GeneratedCode(target_type=GenerationTarget.ENTITY, name=spec.name, code=code, file_path=f'{spec.domain_context}/{spec.name.lower()}.py', imports=self._get_imports(spec), dependencies=self._get_dependencies(spec))

    def _generate_with_default_template(self, spec: GenerationSpec) -> GeneratedCode:
        """Generate code using the default template."""
        entity_template = EntityTemplate()
        return entity_template.generate(spec)

    def _prepare_base_context(self, spec: GenerationSpec) -> Dict[str, Any]:
        """Prepare base template context."""
        entity_template = EntityTemplate()
        return entity_template._prepare_context(spec)

    def _add_validation_rules(self, context: Dict[str, Any], spec: GenerationSpec) -> Dict[str, Any]:
        """Extension point for adding custom validation rules."""
        validation_rules = []
        for constraint in spec.constraints:
            if constraint.startswith('validate_'):
                rule_name = constraint[9:]
                validation_rules.append({'name': rule_name, 'implementation': f'# TODO: Implement {rule_name} validation'})
        return {'validation_rules': validation_rules}

    def _add_business_methods(self, context: Dict[str, Any], spec: GenerationSpec) -> Dict[str, Any]:
        """Extension point for adding business methods."""
        business_methods = []
        for method in spec.methods:
            if method.get('type') == 'business':
                business_methods.append({'name': method['name'], 'params': method.get('params', ''), 'return_type': method.get('return_type', 'None'), 'implementation': method.get('body', 'pass')})
        return {'business_methods': business_methods}

    def _add_event_generation(self, context: Dict[str, Any], spec: GenerationSpec) -> Dict[str, Any]:
        """Extension point for adding domain event generation."""
        events = []
        for method in spec.methods:
            if method.get('generates_event', False):
                event_name = f"{spec.name}{method['name'].title()}Event"
                events.append({'name': event_name, 'method': method['name'], 'data': method.get('event_data', [])})
        return {'domain_events': events}

    def get_supported_target(self) -> GenerationTarget:
        """Get supported target type."""
        return GenerationTarget.ENTITY

    def _get_imports(self, spec: GenerationSpec) -> List[str]:
        """Get required imports."""
        entity_template = EntityTemplate()
        return entity_template._get_imports(spec)

    def _get_dependencies(self, spec: GenerationSpec) -> List[str]:
        """Get dependencies."""
        entity_template = EntityTemplate()
        return entity_template._get_dependencies(spec)
