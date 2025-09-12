"""
Generators Core Core Core

This module was extracted from generators_core_core.py
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
import re
from ..models import DomainBoundaries
import re
import re
from ..core.health import ModuleHealth
from ..models import DomainBoundaries
import re
import re
import re
from ..models import DomainBoundaries
import re
import re
from ..models import DomainBoundaries
import re
import re
import re
from ..core.health import ModuleHealth
from ..models import DomainBoundaries
import re
import re
import re

class GenerationTarget(Enum):
    """Types of code generation targets."""
    ENTITY = 'entity'
    AGGREGATE_ROOT = 'aggregate_root'
    VALUE_OBJECT = 'value_object'
    DOMAIN_SERVICE = 'domain_service'
    REPOSITORY_INTERFACE = 'repository_interface'
    REPOSITORY_IMPLEMENTATION = 'repository_implementation'
    DOMAIN_EVENT = 'domain_event'
    BOUNDED_CONTEXT = 'bounded_context'
    ANTI_CORRUPTION_LAYER = 'anti_corruption_layer'

@dataclass
class GenerationSpec:
    """Specification for code generation."""
    target_type: GenerationTarget
    name: str
    domain_context: str
    attributes: List[Dict[str, Any]] = field(default_factory=list)
    methods: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate_spec(self) -> ValidationResult:
        """Validate the generation specification."""
        result = ValidationResult(is_valid=True)
        if not self.name:
            result.add_error('Generation spec must have a name')
        if not self.domain_context:
            result.add_error('Generation spec must have a domain context')
        for attr in self.attributes:
            if 'name' not in attr:
                result.add_error('Attribute must have a name')
            if 'type' not in attr:
                result.add_error(f"Attribute {attr.get('name', 'unknown')} must have a type")
        return result

@dataclass
class GeneratedCode:
    """Represents generated code with metadata."""
    target_type: GenerationTarget
    name: str
    code: str
    file_path: str
    imports: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)

    def save_to_file(self, base_path: Union[str, Path]) -> Path:
        """Save generated code to file."""
        base_path = Path(base_path)
        full_path = base_path / self.file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(self.code)
        logger.info(f'Generated code saved to {full_path}')
        return full_path

class CodeTemplate(ABC):
    """Abstract base class for code templates."""

    @abstractmethod
    def generate(self, spec: GenerationSpec) -> GeneratedCode:
        """
        Generate code from specification.
        
        Args:
            spec: Generation specification
            
        Returns:
            GeneratedCode: Generated code with metadata
        """
        pass

    @abstractmethod
    def get_supported_target(self) -> GenerationTarget:
        """Get the target type this template supports."""
        pass

class AggregateRootTemplate(CodeTemplate):
    """Template for generating aggregate roots."""

    def __init__(self):
        self.template_content = '"""\n{{ name }} aggregate root for {{ domain_context }} domain.\n\nGenerated at {{ generated_at }}.\n"""\n\nfrom typing import Any, Dict, List, Optional\nfrom uuid import UUID\nfrom datetime import datetime\n\nfrom rm_ddd import AggregateRoot, ValidationResult, DomainBoundaries, AggregateBoundaries\nfrom rm_ddd.decorators import aggregate_root\n\n\n@aggregate_root("{{ domain_context }}", max_size={{ max_size }})\nclass {{ name }}(AggregateRoot[{{ id_type }}]):\n    """{{ description }}"""\n    \n    def __init__(self, {{ constructor_params }}):\n        super().__init__({{ id_param }}, "{{ domain_context }}")\n        {% for attr in attributes -%}\n        self.{{ attr.name }} = {{ attr.name }}\n        {% endfor %}\n    \n    {% for method in methods -%}\n    def {{ method.name }}(self{{ method.params }}):\n        """{{ method.description }}"""\n        {% if method.body -%}\n        {{ method.body | indent(8) }}\n        {% else -%}\n        pass\n        {% endif %}\n    \n    {% endfor -%}\n    \n    def get_domain_boundaries(self) -> DomainBoundaries:\n        """Get domain boundaries for this aggregate."""\n        return DomainBoundaries(\n            context="{{ domain_context }}",\n            invariants=[\n                {% for constraint in constraints -%}\n                "{{ constraint }}",\n                {% endfor %}\n            ]\n        )\n    \n    def get_aggregate_boundaries(self) -> AggregateBoundaries:\n        """Get aggregate consistency boundaries."""\n        return AggregateBoundaries(\n            aggregate_type="{{ name }}",\n            max_size={{ max_size }},\n            consistency_rules=[\n                {% for constraint in constraints -%}\n                "{{ constraint }}",\n                {% endfor %}\n            ],\n            invariants=[\n                {% for constraint in constraints -%}\n                "{{ constraint }}",\n                {% endfor %}\n            ]\n        )\n    \n    def validate_domain_invariants(self) -> ValidationResult:\n        """Validate domain invariants for this aggregate."""\n        result = ValidationResult(is_valid=True)\n        \n        {% for constraint in constraints -%}\n        # Validate: {{ constraint }}\n        # TODO: Implement validation logic\n        \n        {% endfor -%}\n        \n        return result\n'

    def generate(self, spec: GenerationSpec) -> GeneratedCode:
        """Generate aggregate root code."""
        if not JINJA2_AVAILABLE:
            raise DomainException('Jinja2 is required for code generation but not available', error_code='JINJA2_NOT_AVAILABLE')
        validation_result = spec.validate_spec()
        if not validation_result.is_valid:
            raise DomainException(f'Invalid generation spec: {validation_result.errors}', error_code='INVALID_GENERATION_SPEC')
        context = self._prepare_context(spec)
        template = Template(self.template_content)
        code = template.render(**context)
        file_path = f'{spec.domain_context}/{spec.name.lower()}.py'
        return GeneratedCode(target_type=GenerationTarget.AGGREGATE_ROOT, name=spec.name, code=code, file_path=file_path, imports=self._get_imports(spec), dependencies=self._get_dependencies(spec))

    def get_supported_target(self) -> GenerationTarget:
        """Get supported target type."""
        return GenerationTarget.AGGREGATE_ROOT

    def _prepare_context(self, spec: GenerationSpec) -> Dict[str, Any]:
        """Prepare template context from spec."""
        entity_template = EntityTemplate()
        context = entity_template._prepare_context(spec)
        context['max_size'] = spec.metadata.get('max_size', 100)
        return context

    def _get_imports(self, spec: GenerationSpec) -> List[str]:
        """Get required imports for the generated code."""
        imports = ['from typing import Any, Dict, List, Optional', 'from rm_ddd import AggregateRoot, ValidationResult, DomainBoundaries, AggregateBoundaries', 'from rm_ddd.decorators import aggregate_root']
        for attr in spec.attributes:
            attr_type = attr.get('type', '')
            if 'UUID' in attr_type:
                imports.append('from uuid import UUID')
            elif 'datetime' in attr_type:
                imports.append('from datetime import datetime')
        return list(set(imports))

    def _get_dependencies(self, spec: GenerationSpec) -> List[str]:
        """Get dependencies for the generated code."""
        return ['rm_ddd']

class TemplateRegistry:
    """Registry for managing custom templates and template inheritance."""

    def __init__(self):
        self._templates: Dict[str, Dict[str, Any]] = {}
        self._template_inheritance: Dict[str, str] = {}
        self._custom_filters: Dict[str, Callable] = {}
        self._template_cache: Dict[str, Template] = {}

    def register_template(self, name: str, content: str, target_type: GenerationTarget, parent_template: Optional[str]=None, custom_filters: Optional[Dict[str, Callable]]=None):
        """Register a custom template with optional inheritance."""
        self._templates[name] = {'content': content, 'target_type': target_type, 'parent': parent_template, 'filters': custom_filters or {}}
        if parent_template:
            self._template_inheritance[name] = parent_template
        if custom_filters:
            self._custom_filters.update(custom_filters)
        if name in self._template_cache:
            del self._template_cache[name]
        logger.debug(f'Registered template: {name} for {target_type.value}')

    def get_template(self, name: str) -> Optional[Template]:
        """Get a compiled template with inheritance resolution."""
        if name in self._template_cache:
            return self._template_cache[name]
        if name not in self._templates:
            return None
        template_info = self._templates[name]
        content = template_info['content']
        if template_info['parent']:
            parent_content = self._get_parent_content(template_info['parent'])
            content = self._merge_template_content(parent_content, content)
        if JINJA2_AVAILABLE:
            env = Environment()
            env.filters.update(self._custom_filters)
            env.filters.update(template_info['filters'])
            template = env.from_string(content)
            self._template_cache[name] = template
            return template
        return None

    def _get_parent_content(self, parent_name: str) -> str:
        """Get parent template content recursively."""
        if parent_name not in self._templates:
            return ''
        parent_info = self._templates[parent_name]
        content = parent_info['content']
        if parent_info['parent']:
            grandparent_content = self._get_parent_content(parent_info['parent'])
            content = self._merge_template_content(grandparent_content, content)
        return content

    def _merge_template_content(self, parent_content: str, child_content: str) -> str:
        """Merge parent and child template content."""
        parent_blocks = self._extract_blocks(parent_content)
        child_blocks = self._extract_blocks(child_content)
        merged_blocks = {**parent_blocks, **child_blocks}
        result = parent_content
        for block_name, block_content in merged_blocks.items():
            block_pattern = f'{{% block {block_name} %}}.+?{{% endblock %}}'
            replacement = f'{{% block {block_name} %}}{block_content}{{% endblock %}}'
            result = result.replace(f"{{% block {block_name} %}}{parent_blocks.get(block_name, '')}{{% endblock %}}", replacement)
        return result

    def _extract_blocks(self, content: str) -> Dict[str, str]:
        """Extract Jinja2 blocks from template content."""
        import re
        blocks = {}
        block_pattern = '{%\\s*block\\s+(\\w+)\\s*%}(.*?){%\\s*endblock\\s*%}'
        matches = re.findall(block_pattern, content, re.DOTALL)
        for block_name, block_content in matches:
            blocks[block_name] = block_content.strip()
        return blocks

    def list_templates(self) -> List[Dict[str, Any]]:
        """List all registered templates."""
        return [{'name': name, 'target_type': info['target_type'].value, 'parent': info['parent'], 'has_custom_filters': bool(info['filters'])} for name, info in self._templates.items()]

class CustomizableCodeTemplate(CodeTemplate):
    """Base class for customizable code templates with extension points."""

    def __init__(self, template_registry: TemplateRegistry):
        self.template_registry = template_registry
        self._extension_points: Dict[str, Callable] = {}

    def add_extension_point(self, name: str, handler: Callable):
        """Add an extension point for template customization."""
        self._extension_points[name] = handler
        logger.debug(f'Added extension point: {name}')

    def apply_extensions(self, context: Dict[str, Any], spec: GenerationSpec) -> Dict[str, Any]:
        """Apply all registered extensions to the template context."""
        extended_context = context.copy()
        for name, handler in self._extension_points.items():
            try:
                extension_result = handler(extended_context, spec)
                if isinstance(extension_result, dict):
                    extended_context.update(extension_result)
            except Exception as e:
                logger.warning(f'Extension point {name} failed: {e}')
        return extended_context

    def get_custom_template(self, template_name: str) -> Optional[Template]:
        """Get a custom template from the registry."""
        return self.template_registry.get_template(template_name)

class RMDDDCodeGenerator(DomainReflectiveModule):
    """
    Comprehensive code generator for RM-DDD patterns with template customization.
    
    Provides systematic code generation with template management, inheritance,
    validation, and compliance checking for all RM-DDD components.
    """

    def __init__(self, domain_context: str='code_generation'):
        super().__init__(domain_context)
        self._templates: Dict[GenerationTarget, CodeTemplate] = {}
        self._generated_files: List[GeneratedCode] = []
        self._template_registry = TemplateRegistry()
        self._initialize_default_templates()
        self._register_default_custom_filters()

    def _initialize_default_templates(self):
        """Initialize default code templates with customization support."""
        self._templates[GenerationTarget.ENTITY] = EnhancedEntityTemplate(self._template_registry)
        self._templates[GenerationTarget.AGGREGATE_ROOT] = AggregateRootTemplate()
        self._register_default_template_variations()
        logger.debug('Initialized enhanced code generation templates')

    def _register_default_template_variations(self):
        """Register default template variations for common patterns."""
        simple_entity_template = '"""\n{{ name }} entity - Simple implementation.\n"""\n\nfrom rm_ddd import Entity, domain_entity\n\n@domain_entity("{{ domain_context }}")\nclass {{ name }}(Entity[str]):\n    def __init__(self, {{ id_param }}: str):\n        super().__init__({{ id_param }}, "{{ domain_context }}")\n        {% for attr in attributes -%}\n        self.{{ attr.name }} = None  # {{ attr.type }}\n        {% endfor %}\n'
        self._template_registry.register_template('entity_simple', simple_entity_template, GenerationTarget.ENTITY)
        rich_entity_template = '"""\n{{ name }} entity - Rich domain model.\n"""\n\nfrom typing import Any, Dict, List, Optional\nfrom rm_ddd import Entity, ValidationResult, DomainBoundaries, domain_entity\n\n@domain_entity("{{ domain_context }}")\nclass {{ name }}(Entity[{{ id_type }}]):\n    """{{ description }}"""\n    \n    def __init__(self, {{ constructor_params }}):\n        super().__init__({{ id_param }}, "{{ domain_context }}")\n        {% for attr in attributes -%}\n        self.{{ attr.name }} = {{ attr.name }}\n        {% endfor %}\n    \n    {% for method in business_methods -%}\n    def {{ method.name }}(self{{ method.params }}) -> {{ method.return_type }}:\n        """Business method: {{ method.name }}"""\n        {{ method.implementation | indent(8) }}\n    \n    {% endfor -%}\n    \n    {% for rule in validation_rules -%}\n    def _validate_{{ rule.name }}(self) -> bool:\n        """Validate {{ rule.name }}"""\n        {{ rule.implementation | indent(8) }}\n        return True\n    \n    {% endfor -%}\n    \n    def get_domain_boundaries(self) -> DomainBoundaries:\n        return DomainBoundaries(\n            context="{{ domain_context }}",\n            invariants=[\n                {% for constraint in constraints -%}\n                "{{ constraint }}",\n                {% endfor %}\n            ]\n        )\n    \n    def validate_domain_invariants(self) -> ValidationResult:\n        result = ValidationResult(is_valid=True)\n        \n        {% for rule in validation_rules -%}\n        if not self._validate_{{ rule.name }}():\n            result.add_error("{{ rule.name }} validation failed")\n        {% endfor %}\n        \n        return result\n'
        self._template_registry.register_template('entity_rich', rich_entity_template, GenerationTarget.ENTITY)

    def _register_default_custom_filters(self):
        """Register default custom Jinja2 filters."""

        def camel_case(text):
            """Convert text to camelCase."""
            components = text.split('_')
            return components[0] + ''.join((word.capitalize() for word in components[1:]))

        def pascal_case(text):
            """Convert text to PascalCase."""
            return ''.join((word.capitalize() for word in text.split('_')))

        def snake_case(text):
            """Convert text to snake_case."""
            import re
            s1 = re.sub('(.)([A-Z][a-z]+)', '\\1_\\2', text)
            return re.sub('([a-z0-9])([A-Z])', '\\1_\\2', s1).lower()
        custom_filters = {'camel_case': camel_case, 'pascal_case': pascal_case, 'snake_case': snake_case}
        for name, filter_func in custom_filters.items():
            self._template_registry._custom_filters[name] = filter_func

    def add_template(self, template: CodeTemplate):
        """
        Add a custom code template.
        
        Args:
            template: Code template to add
        """
        target_type = template.get_supported_target()
        self._templates[target_type] = template
        logger.debug(f'Added custom template for {target_type.value}')

    def generate_code(self, spec: GenerationSpec) -> GeneratedCode:
        """
        Generate code from specification.
        
        Args:
            spec: Generation specification
            
        Returns:
            GeneratedCode: Generated code with metadata
            
        Raises:
            DomainException: If generation fails
        """
        validation_result = spec.validate_spec()
        if not validation_result.is_valid:
            raise DomainException(f'Invalid generation specification: {validation_result.errors}', error_code='INVALID_GENERATION_SPEC')
        if spec.target_type not in self._templates:
            raise DomainException(f'No template available for target type: {spec.target_type.value}', error_code='TEMPLATE_NOT_FOUND')
        template = self._templates[spec.target_type]
        try:
            generated_code = template.generate(spec)
            self._generated_files.append(generated_code)
            logger.info(f'Generated {spec.target_type.value}: {spec.name}')
            return generated_code
        except Exception as e:
            logger.error(f'Code generation failed for {spec.name}: {e}')
            raise DomainException(f'Code generation failed: {str(e)}', error_code='CODE_GENERATION_FAILED')

    def generate_entity(self, name: str, domain_context: str, attributes: List[Dict[str, Any]], **kwargs) -> GeneratedCode:
        """
        Generate a domain entity.
        
        Args:
            name: Entity name
            domain_context: Domain context
            attributes: Entity attributes
            **kwargs: Additional metadata
            
        Returns:
            GeneratedCode: Generated entity code
        """
        spec = GenerationSpec(target_type=GenerationTarget.ENTITY, name=name, domain_context=domain_context, attributes=attributes, methods=kwargs.get('methods', []), constraints=kwargs.get('constraints', []), metadata=kwargs)
        return self.generate_code(spec)

    def generate_aggregate_root(self, name: str, domain_context: str, attributes: List[Dict[str, Any]], **kwargs) -> GeneratedCode:
        """
        Generate an aggregate root.
        
        Args:
            name: Aggregate name
            domain_context: Domain context
            attributes: Aggregate attributes
            **kwargs: Additional metadata
            
        Returns:
            GeneratedCode: Generated aggregate code
        """
        spec = GenerationSpec(target_type=GenerationTarget.AGGREGATE_ROOT, name=name, domain_context=domain_context, attributes=attributes, methods=kwargs.get('methods', []), constraints=kwargs.get('constraints', []), metadata=kwargs)
        return self.generate_code(spec)

    def save_all_generated_code(self, base_path: Union[str, Path]) -> List[Path]:
        """
        Save all generated code to files.
        
        Args:
            base_path: Base directory path
            
        Returns:
            List[Path]: List of saved file paths
        """
        saved_paths = []
        for generated_code in self._generated_files:
            try:
                path = generated_code.save_to_file(base_path)
                saved_paths.append(path)
            except Exception as e:
                logger.error(f'Failed to save {generated_code.name}: {e}')
        logger.info(f'Saved {len(saved_paths)} generated files')
        return saved_paths

    def get_generation_summary(self) -> Dict[str, Any]:
        """Get summary of code generation activity."""
        target_counts = {}
        for generated_code in self._generated_files:
            target_type = generated_code.target_type.value
            target_counts[target_type] = target_counts.get(target_type, 0) + 1
        return {'total_generated': len(self._generated_files), 'target_counts': target_counts, 'available_templates': [t.value for t in self._templates.keys()], 'generated_files': [{'name': gc.name, 'type': gc.target_type.value, 'file_path': gc.file_path, 'generated_at': gc.generated_at.isoformat()} for gc in self._generated_files]}

    async def get_module_status(self):
        """Get module status."""
        from ..core.health import ModuleHealth
        summary = self.get_generation_summary()
        return ModuleHealth(status=ModuleStatus.AVAILABLE, message=f'Code generator with {len(self._templates)} templates', capabilities=await self.get_module_capabilities(), health_indicators={'available_templates': len(self._templates), 'generated_files': summary['total_generated']})

    async def get_module_capabilities(self):
        """Get module capabilities."""
        return [ModuleCapability(name='rm_ddd_code_generation', description='Generates RM-DDD compliant code from specifications', available=True, version='1.0.0')]

    async def is_healthy(self) -> bool:
        """Check if code generator is healthy."""
        return len(self._templates) > 0

    async def get_health_indicators(self):
        """Get health indicators."""
        return {'generation_summary': self.get_generation_summary(), 'domain_context': self.domain_context, 'jinja2_available': JINJA2_AVAILABLE}

    def get_domain_boundaries(self):
        """Get domain boundaries."""
        from ..models import DomainBoundaries
        return DomainBoundaries(context=self.domain_context, invariants=['Generated code must be syntactically valid', 'Generated code must follow RM-DDD patterns', 'All specifications must be validated before generation'])

    def validate_domain_invariants(self):
        """Validate domain invariants."""
        result = ValidationResult(is_valid=True)
        if not JINJA2_AVAILABLE:
            result.add_warning('Jinja2 not available - code generation capabilities limited')
        if not self._templates:
            result.add_error('No code templates available')
        return result

def generate_entity_from_dict(entity_def: Dict[str, Any]) -> GeneratedCode:
    """
    Generate entity from dictionary definition.
    
    Args:
        entity_def: Dictionary containing entity definition
        
    Returns:
        GeneratedCode: Generated entity code
    """
    generator = RMDDDCodeGenerator()
    spec = GenerationSpec(target_type=GenerationTarget.ENTITY, name=entity_def['name'], domain_context=entity_def['domain_context'], attributes=entity_def.get('attributes', []), methods=entity_def.get('methods', []), constraints=entity_def.get('constraints', []), metadata=entity_def.get('metadata', {}))
    return generator.generate_code(spec)

def generate_aggregate_from_dict(aggregate_def: Dict[str, Any]) -> GeneratedCode:
    """
    Generate aggregate root from dictionary definition.
    
    Args:
        aggregate_def: Dictionary containing aggregate definition
        
    Returns:
        GeneratedCode: Generated aggregate code
    """
    generator = RMDDDCodeGenerator()
    spec = GenerationSpec(target_type=GenerationTarget.AGGREGATE_ROOT, name=aggregate_def['name'], domain_context=aggregate_def['domain_context'], attributes=aggregate_def.get('attributes', []), methods=aggregate_def.get('methods', []), constraints=aggregate_def.get('constraints', []), metadata=aggregate_def.get('metadata', {}))
    return generator.generate_code(spec)

    def register_custom_template(self, name: str, content: str, target_type: GenerationTarget, parent_template: Optional[str]=None, custom_filters: Optional[Dict[str, Callable]]=None):
        """
        Register a custom template for code generation.
        
        Args:
            name: Template name
            content: Template content (Jinja2 format)
            target_type: Target generation type
            parent_template: Optional parent template for inheritance
            custom_filters: Optional custom Jinja2 filters
        """
        self._template_registry.register_template(name, content, target_type, parent_template, custom_filters)
        logger.info(f'Registered custom template: {name}')

    def add_template_extension(self, target_type: GenerationTarget, extension_name: str, extension_handler: Callable):
        """
        Add an extension point to a template.
        
        Args:
            target_type: Target type to extend
            extension_name: Name of the extension point
            extension_handler: Handler function for the extension
        """
        if target_type in self._templates:
            template = self._templates[target_type]
            if isinstance(template, CustomizableCodeTemplate):
                template.add_extension_point(extension_name, extension_handler)
                logger.info(f'Added extension {extension_name} to {target_type.value}')

    def generate_with_template(self, spec: GenerationSpec, template_name: Optional[str]=None) -> GeneratedCode:
        """
        Generate code using a specific template.
        
        Args:
            spec: Generation specification
            template_name: Optional specific template to use
            
        Returns:
            GeneratedCode: Generated code with metadata
        """
        if template_name:
            custom_template = self._template_registry.get_template(template_name)
            if custom_template and spec.target_type in self._templates:
                template = self._templates[spec.target_type]
                if isinstance(template, CustomizableCodeTemplate):
                    return template._generate_with_custom_template(custom_template, spec)
        return self.generate_code(spec)

    def list_available_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all available templates by target type.
        
        Returns:
            Dict mapping target types to available templates
        """
        templates_by_type = {}
        for template_info in self._template_registry.list_templates():
            target_type = template_info['target_type']
            if target_type not in templates_by_type:
                templates_by_type[target_type] = []
            templates_by_type[target_type].append(template_info)
        return templates_by_type

    def create_template_composition(self, base_templates: List[str], composition_name: str, target_type: GenerationTarget) -> str:
        """
        Create a new template by composing existing templates.
        
        Args:
            base_templates: List of template names to compose
            composition_name: Name for the new composed template
            target_type: Target type for the composed template
            
        Returns:
            str: Name of the created composed template
        """
        composed_content = ''
        for template_name in base_templates:
            template_info = self._template_registry._templates.get(template_name)
            if template_info:
                composed_content += f"\n{{% include '{template_name}' %}}\n"
        self._template_registry.register_template(composition_name, composed_content, target_type)
        logger.info(f'Created composed template: {composition_name}')
        return composition_name

    def validate_template(self, template_name: str) -> ValidationResult:
        """
        Validate a template for syntax and completeness.
        
        Args:
            template_name: Name of template to validate
            
        Returns:
            ValidationResult: Validation results
        """
        result = ValidationResult(is_valid=True)
        template = self._template_registry.get_template(template_name)
        if not template:
            result.add_error(f'Template {template_name} not found')
            return result
        try:
            test_context = {'name': 'TestEntity', 'domain_context': 'test', 'attributes': [], 'methods': [], 'constraints': [], 'generated_at': datetime.now().isoformat()}
            template.render(**test_context)
            logger.debug(f'Template {template_name} validation successful')
        except Exception as e:
            result.add_error(f'Template validation failed: {str(e)}')
        return result

    def export_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Export a template for sharing or backup.
        
        Args:
            template_name: Name of template to export
            
        Returns:
            Optional[Dict]: Template export data
        """
        if template_name not in self._template_registry._templates:
            return None
        template_info = self._template_registry._templates[template_name]
        return {'name': template_name, 'content': template_info['content'], 'target_type': template_info['target_type'].value, 'parent': template_info['parent'], 'filters': list(template_info['filters'].keys()), 'exported_at': datetime.now().isoformat()}

    def import_template(self, template_data: Dict[str, Any]) -> bool:
        """
        Import a template from export data.
        
        Args:
            template_data: Template export data
            
        Returns:
            bool: True if import successful
        """
        try:
            target_type = GenerationTarget(template_data['target_type'])
            self._template_registry.register_template(template_data['name'], template_data['content'], target_type, template_data.get('parent'))
            logger.info(f"Imported template: {template_data['name']}")
            return True
        except Exception as e:
            logger.error(f'Failed to import template: {e}')
            return False

def create_custom_entity_template(name: str, template_content: str, custom_filters: Optional[Dict[str, Callable]]=None) -> str:
    """
    Create a custom entity template.
    
    Args:
        name: Template name
        template_content: Jinja2 template content
        custom_filters: Optional custom filters
        
    Returns:
        str: Template name for use in generation
    """
    generator = RMDDDCodeGenerator()
    generator.register_custom_template(name, template_content, GenerationTarget.ENTITY, custom_filters=custom_filters)
    return name

def generate_with_custom_template(spec_dict: Dict[str, Any], template_name: str) -> GeneratedCode:
    """
    Generate code using a custom template.
    
    Args:
        spec_dict: Generation specification as dictionary
        template_name: Name of custom template to use
        
    Returns:
        GeneratedCode: Generated code
    """
    generator = RMDDDCodeGenerator()
    spec = GenerationSpec(target_type=GenerationTarget(spec_dict['target_type']), name=spec_dict['name'], domain_context=spec_dict['domain_context'], attributes=spec_dict.get('attributes', []), methods=spec_dict.get('methods', []), constraints=spec_dict.get('constraints', []), metadata=spec_dict.get('metadata', {}))
    return generator.generate_with_template(spec, template_name)

def save_to_file(self, base_path: Union[str, Path]) -> Path:
    """Save generated code to file."""
    base_path = Path(base_path)
    full_path = base_path / self.file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(self.code)
    logger.info(f'Generated code saved to {full_path}')
    return full_path

@abstractmethod
def generate(self, spec: GenerationSpec) -> GeneratedCode:
    """
        Generate code from specification.
        
        Args:
            spec: Generation specification
            
        Returns:
            GeneratedCode: Generated code with metadata
        """
    pass

@abstractmethod
def get_supported_target(self) -> GenerationTarget:
    """Get the target type this template supports."""
    pass

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

def __init__(self):
    self.template_content = '"""\n{{ name }} aggregate root for {{ domain_context }} domain.\n\nGenerated at {{ generated_at }}.\n"""\n\nfrom typing import Any, Dict, List, Optional\nfrom uuid import UUID\nfrom datetime import datetime\n\nfrom rm_ddd import AggregateRoot, ValidationResult, DomainBoundaries, AggregateBoundaries\nfrom rm_ddd.decorators import aggregate_root\n\n\n@aggregate_root("{{ domain_context }}", max_size={{ max_size }})\nclass {{ name }}(AggregateRoot[{{ id_type }}]):\n    """{{ description }}"""\n    \n    def __init__(self, {{ constructor_params }}):\n        super().__init__({{ id_param }}, "{{ domain_context }}")\n        {% for attr in attributes -%}\n        self.{{ attr.name }} = {{ attr.name }}\n        {% endfor %}\n    \n    {% for method in methods -%}\n    def {{ method.name }}(self{{ method.params }}):\n        """{{ method.description }}"""\n        {% if method.body -%}\n        {{ method.body | indent(8) }}\n        {% else -%}\n        pass\n        {% endif %}\n    \n    {% endfor -%}\n    \n    def get_domain_boundaries(self) -> DomainBoundaries:\n        """Get domain boundaries for this aggregate."""\n        return DomainBoundaries(\n            context="{{ domain_context }}",\n            invariants=[\n                {% for constraint in constraints -%}\n                "{{ constraint }}",\n                {% endfor %}\n            ]\n        )\n    \n    def get_aggregate_boundaries(self) -> AggregateBoundaries:\n        """Get aggregate consistency boundaries."""\n        return AggregateBoundaries(\n            aggregate_type="{{ name }}",\n            max_size={{ max_size }},\n            consistency_rules=[\n                {% for constraint in constraints -%}\n                "{{ constraint }}",\n                {% endfor %}\n            ],\n            invariants=[\n                {% for constraint in constraints -%}\n                "{{ constraint }}",\n                {% endfor %}\n            ]\n        )\n    \n    def validate_domain_invariants(self) -> ValidationResult:\n        """Validate domain invariants for this aggregate."""\n        result = ValidationResult(is_valid=True)\n        \n        {% for constraint in constraints -%}\n        # Validate: {{ constraint }}\n        # TODO: Implement validation logic\n        \n        {% endfor -%}\n        \n        return result\n'

def generate(self, spec: GenerationSpec) -> GeneratedCode:
    """Generate aggregate root code."""
    if not JINJA2_AVAILABLE:
        raise DomainException('Jinja2 is required for code generation but not available', error_code='JINJA2_NOT_AVAILABLE')
    validation_result = spec.validate_spec()
    if not validation_result.is_valid:
        raise DomainException(f'Invalid generation spec: {validation_result.errors}', error_code='INVALID_GENERATION_SPEC')
    context = self._prepare_context(spec)
    template = Template(self.template_content)
    code = template.render(**context)
    file_path = f'{spec.domain_context}/{spec.name.lower()}.py'
    return GeneratedCode(target_type=GenerationTarget.AGGREGATE_ROOT, name=spec.name, code=code, file_path=file_path, imports=self._get_imports(spec), dependencies=self._get_dependencies(spec))

def get_supported_target(self) -> GenerationTarget:
    """Get supported target type."""
    return GenerationTarget.AGGREGATE_ROOT

def _prepare_context(self, spec: GenerationSpec) -> Dict[str, Any]:
    """Prepare template context from spec."""
    entity_template = EntityTemplate()
    context = entity_template._prepare_context(spec)
    context['max_size'] = spec.metadata.get('max_size', 100)
    return context

def _get_imports(self, spec: GenerationSpec) -> List[str]:
    """Get required imports for the generated code."""
    imports = ['from typing import Any, Dict, List, Optional', 'from rm_ddd import AggregateRoot, ValidationResult, DomainBoundaries, AggregateBoundaries', 'from rm_ddd.decorators import aggregate_root']
    for attr in spec.attributes:
        attr_type = attr.get('type', '')
        if 'UUID' in attr_type:
            imports.append('from uuid import UUID')
        elif 'datetime' in attr_type:
            imports.append('from datetime import datetime')
    return list(set(imports))

def _get_dependencies(self, spec: GenerationSpec) -> List[str]:
    """Get dependencies for the generated code."""
    return ['rm_ddd']

def __init__(self):
    self._templates: Dict[str, Dict[str, Any]] = {}
    self._template_inheritance: Dict[str, str] = {}
    self._custom_filters: Dict[str, Callable] = {}
    self._template_cache: Dict[str, Template] = {}

def register_template(self, name: str, content: str, target_type: GenerationTarget, parent_template: Optional[str]=None, custom_filters: Optional[Dict[str, Callable]]=None):
    """Register a custom template with optional inheritance."""
    self._templates[name] = {'content': content, 'target_type': target_type, 'parent': parent_template, 'filters': custom_filters or {}}
    if parent_template:
        self._template_inheritance[name] = parent_template
    if custom_filters:
        self._custom_filters.update(custom_filters)
    if name in self._template_cache:
        del self._template_cache[name]
    logger.debug(f'Registered template: {name} for {target_type.value}')

def get_template(self, name: str) -> Optional[Template]:
    """Get a compiled template with inheritance resolution."""
    if name in self._template_cache:
        return self._template_cache[name]
    if name not in self._templates:
        return None
    template_info = self._templates[name]
    content = template_info['content']
    if template_info['parent']:
        parent_content = self._get_parent_content(template_info['parent'])
        content = self._merge_template_content(parent_content, content)
    if JINJA2_AVAILABLE:
        env = Environment()
        env.filters.update(self._custom_filters)
        env.filters.update(template_info['filters'])
        template = env.from_string(content)
        self._template_cache[name] = template
        return template
    return None

def _get_parent_content(self, parent_name: str) -> str:
    """Get parent template content recursively."""
    if parent_name not in self._templates:
        return ''
    parent_info = self._templates[parent_name]
    content = parent_info['content']
    if parent_info['parent']:
        grandparent_content = self._get_parent_content(parent_info['parent'])
        content = self._merge_template_content(grandparent_content, content)
    return content

def _merge_template_content(self, parent_content: str, child_content: str) -> str:
    """Merge parent and child template content."""
    parent_blocks = self._extract_blocks(parent_content)
    child_blocks = self._extract_blocks(child_content)
    merged_blocks = {**parent_blocks, **child_blocks}
    result = parent_content
    for block_name, block_content in merged_blocks.items():
        block_pattern = f'{{% block {block_name} %}}.+?{{% endblock %}}'
        replacement = f'{{% block {block_name} %}}{block_content}{{% endblock %}}'
        result = result.replace(f"{{% block {block_name} %}}{parent_blocks.get(block_name, '')}{{% endblock %}}", replacement)
    return result

def _extract_blocks(self, content: str) -> Dict[str, str]:
    """Extract Jinja2 blocks from template content."""
    import re
    blocks = {}
    block_pattern = '{%\\s*block\\s+(\\w+)\\s*%}(.*?){%\\s*endblock\\s*%}'
    matches = re.findall(block_pattern, content, re.DOTALL)
    for block_name, block_content in matches:
        blocks[block_name] = block_content.strip()
    return blocks

def list_templates(self) -> List[Dict[str, Any]]:
    """List all registered templates."""
    return [{'name': name, 'target_type': info['target_type'].value, 'parent': info['parent'], 'has_custom_filters': bool(info['filters'])} for name, info in self._templates.items()]

def __init__(self, template_registry: TemplateRegistry):
    self.template_registry = template_registry
    self._extension_points: Dict[str, Callable] = {}

def add_extension_point(self, name: str, handler: Callable):
    """Add an extension point for template customization."""
    self._extension_points[name] = handler
    logger.debug(f'Added extension point: {name}')

def apply_extensions(self, context: Dict[str, Any], spec: GenerationSpec) -> Dict[str, Any]:
    """Apply all registered extensions to the template context."""
    extended_context = context.copy()
    for name, handler in self._extension_points.items():
        try:
            extension_result = handler(extended_context, spec)
            if isinstance(extension_result, dict):
                extended_context.update(extension_result)
        except Exception as e:
            logger.warning(f'Extension point {name} failed: {e}')
    return extended_context

def get_custom_template(self, template_name: str) -> Optional[Template]:
    """Get a custom template from the registry."""
    return self.template_registry.get_template(template_name)

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

def __init__(self, domain_context: str='code_generation'):
    super().__init__(domain_context)
    self._templates: Dict[GenerationTarget, CodeTemplate] = {}
    self._generated_files: List[GeneratedCode] = []
    self._template_registry = TemplateRegistry()
    self._initialize_default_templates()
    self._register_default_custom_filters()

def _initialize_default_templates(self):
    """Initialize default code templates with customization support."""
    self._templates[GenerationTarget.ENTITY] = EnhancedEntityTemplate(self._template_registry)
    self._templates[GenerationTarget.AGGREGATE_ROOT] = AggregateRootTemplate()
    self._register_default_template_variations()
    logger.debug('Initialized enhanced code generation templates')

def _register_default_template_variations(self):
    """Register default template variations for common patterns."""
    simple_entity_template = '"""\n{{ name }} entity - Simple implementation.\n"""\n\nfrom rm_ddd import Entity, domain_entity\n\n@domain_entity("{{ domain_context }}")\nclass {{ name }}(Entity[str]):\n    def __init__(self, {{ id_param }}: str):\n        super().__init__({{ id_param }}, "{{ domain_context }}")\n        {% for attr in attributes -%}\n        self.{{ attr.name }} = None  # {{ attr.type }}\n        {% endfor %}\n'
    self._template_registry.register_template('entity_simple', simple_entity_template, GenerationTarget.ENTITY)
    rich_entity_template = '"""\n{{ name }} entity - Rich domain model.\n"""\n\nfrom typing import Any, Dict, List, Optional\nfrom rm_ddd import Entity, ValidationResult, DomainBoundaries, domain_entity\n\n@domain_entity("{{ domain_context }}")\nclass {{ name }}(Entity[{{ id_type }}]):\n    """{{ description }}"""\n    \n    def __init__(self, {{ constructor_params }}):\n        super().__init__({{ id_param }}, "{{ domain_context }}")\n        {% for attr in attributes -%}\n        self.{{ attr.name }} = {{ attr.name }}\n        {% endfor %}\n    \n    {% for method in business_methods -%}\n    def {{ method.name }}(self{{ method.params }}) -> {{ method.return_type }}:\n        """Business method: {{ method.name }}"""\n        {{ method.implementation | indent(8) }}\n    \n    {% endfor -%}\n    \n    {% for rule in validation_rules -%}\n    def _validate_{{ rule.name }}(self) -> bool:\n        """Validate {{ rule.name }}"""\n        {{ rule.implementation | indent(8) }}\n        return True\n    \n    {% endfor -%}\n    \n    def get_domain_boundaries(self) -> DomainBoundaries:\n        return DomainBoundaries(\n            context="{{ domain_context }}",\n            invariants=[\n                {% for constraint in constraints -%}\n                "{{ constraint }}",\n                {% endfor %}\n            ]\n        )\n    \n    def validate_domain_invariants(self) -> ValidationResult:\n        result = ValidationResult(is_valid=True)\n        \n        {% for rule in validation_rules -%}\n        if not self._validate_{{ rule.name }}():\n            result.add_error("{{ rule.name }} validation failed")\n        {% endfor %}\n        \n        return result\n'
    self._template_registry.register_template('entity_rich', rich_entity_template, GenerationTarget.ENTITY)

def _register_default_custom_filters(self):
    """Register default custom Jinja2 filters."""

    def camel_case(text):
        """Convert text to camelCase."""
        components = text.split('_')
        return components[0] + ''.join((word.capitalize() for word in components[1:]))

    def pascal_case(text):
        """Convert text to PascalCase."""
        return ''.join((word.capitalize() for word in text.split('_')))

    def snake_case(text):
        """Convert text to snake_case."""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', '\\1_\\2', text)
        return re.sub('([a-z0-9])([A-Z])', '\\1_\\2', s1).lower()
    custom_filters = {'camel_case': camel_case, 'pascal_case': pascal_case, 'snake_case': snake_case}
    for name, filter_func in custom_filters.items():
        self._template_registry._custom_filters[name] = filter_func

def add_template(self, template: CodeTemplate):
    """
        Add a custom code template.
        
        Args:
            template: Code template to add
        """
    target_type = template.get_supported_target()
    self._templates[target_type] = template
    logger.debug(f'Added custom template for {target_type.value}')

def generate_code(self, spec: GenerationSpec) -> GeneratedCode:
    """
        Generate code from specification.
        
        Args:
            spec: Generation specification
            
        Returns:
            GeneratedCode: Generated code with metadata
            
        Raises:
            DomainException: If generation fails
        """
    validation_result = spec.validate_spec()
    if not validation_result.is_valid:
        raise DomainException(f'Invalid generation specification: {validation_result.errors}', error_code='INVALID_GENERATION_SPEC')
    if spec.target_type not in self._templates:
        raise DomainException(f'No template available for target type: {spec.target_type.value}', error_code='TEMPLATE_NOT_FOUND')
    template = self._templates[spec.target_type]
    try:
        generated_code = template.generate(spec)
        self._generated_files.append(generated_code)
        logger.info(f'Generated {spec.target_type.value}: {spec.name}')
        return generated_code
    except Exception as e:
        logger.error(f'Code generation failed for {spec.name}: {e}')
        raise DomainException(f'Code generation failed: {str(e)}', error_code='CODE_GENERATION_FAILED')

def generate_entity(self, name: str, domain_context: str, attributes: List[Dict[str, Any]], **kwargs) -> GeneratedCode:
    """
        Generate a domain entity.
        
        Args:
            name: Entity name
            domain_context: Domain context
            attributes: Entity attributes
            **kwargs: Additional metadata
            
        Returns:
            GeneratedCode: Generated entity code
        """
    spec = GenerationSpec(target_type=GenerationTarget.ENTITY, name=name, domain_context=domain_context, attributes=attributes, methods=kwargs.get('methods', []), constraints=kwargs.get('constraints', []), metadata=kwargs)
    return self.generate_code(spec)

def generate_aggregate_root(self, name: str, domain_context: str, attributes: List[Dict[str, Any]], **kwargs) -> GeneratedCode:
    """
        Generate an aggregate root.
        
        Args:
            name: Aggregate name
            domain_context: Domain context
            attributes: Aggregate attributes
            **kwargs: Additional metadata
            
        Returns:
            GeneratedCode: Generated aggregate code
        """
    spec = GenerationSpec(target_type=GenerationTarget.AGGREGATE_ROOT, name=name, domain_context=domain_context, attributes=attributes, methods=kwargs.get('methods', []), constraints=kwargs.get('constraints', []), metadata=kwargs)
    return self.generate_code(spec)

def save_all_generated_code(self, base_path: Union[str, Path]) -> List[Path]:
    """
        Save all generated code to files.
        
        Args:
            base_path: Base directory path
            
        Returns:
            List[Path]: List of saved file paths
        """
    saved_paths = []
    for generated_code in self._generated_files:
        try:
            path = generated_code.save_to_file(base_path)
            saved_paths.append(path)
        except Exception as e:
            logger.error(f'Failed to save {generated_code.name}: {e}')
    logger.info(f'Saved {len(saved_paths)} generated files')
    return saved_paths

def get_generation_summary(self) -> Dict[str, Any]:
    """Get summary of code generation activity."""
    target_counts = {}
    for generated_code in self._generated_files:
        target_type = generated_code.target_type.value
        target_counts[target_type] = target_counts.get(target_type, 0) + 1
    return {'total_generated': len(self._generated_files), 'target_counts': target_counts, 'available_templates': [t.value for t in self._templates.keys()], 'generated_files': [{'name': gc.name, 'type': gc.target_type.value, 'file_path': gc.file_path, 'generated_at': gc.generated_at.isoformat()} for gc in self._generated_files]}

def get_domain_boundaries(self):
    """Get domain boundaries."""
    from ..models import DomainBoundaries
    return DomainBoundaries(context=self.domain_context, invariants=['Generated code must be syntactically valid', 'Generated code must follow RM-DDD patterns', 'All specifications must be validated before generation'])

def register_custom_template(self, name: str, content: str, target_type: GenerationTarget, parent_template: Optional[str]=None, custom_filters: Optional[Dict[str, Callable]]=None):
    """
        Register a custom template for code generation.
        
        Args:
            name: Template name
            content: Template content (Jinja2 format)
            target_type: Target generation type
            parent_template: Optional parent template for inheritance
            custom_filters: Optional custom Jinja2 filters
        """
    self._template_registry.register_template(name, content, target_type, parent_template, custom_filters)
    logger.info(f'Registered custom template: {name}')

def add_template_extension(self, target_type: GenerationTarget, extension_name: str, extension_handler: Callable):
    """
        Add an extension point to a template.
        
        Args:
            target_type: Target type to extend
            extension_name: Name of the extension point
            extension_handler: Handler function for the extension
        """
    if target_type in self._templates:
        template = self._templates[target_type]
        if isinstance(template, CustomizableCodeTemplate):
            template.add_extension_point(extension_name, extension_handler)
            logger.info(f'Added extension {extension_name} to {target_type.value}')

def generate_with_template(self, spec: GenerationSpec, template_name: Optional[str]=None) -> GeneratedCode:
    """
        Generate code using a specific template.
        
        Args:
            spec: Generation specification
            template_name: Optional specific template to use
            
        Returns:
            GeneratedCode: Generated code with metadata
        """
    if template_name:
        custom_template = self._template_registry.get_template(template_name)
        if custom_template and spec.target_type in self._templates:
            template = self._templates[spec.target_type]
            if isinstance(template, CustomizableCodeTemplate):
                return template._generate_with_custom_template(custom_template, spec)
    return self.generate_code(spec)

def list_available_templates(self) -> Dict[str, List[Dict[str, Any]]]:
    """
        List all available templates by target type.
        
        Returns:
            Dict mapping target types to available templates
        """
    templates_by_type = {}
    for template_info in self._template_registry.list_templates():
        target_type = template_info['target_type']
        if target_type not in templates_by_type:
            templates_by_type[target_type] = []
        templates_by_type[target_type].append(template_info)
    return templates_by_type

def create_template_composition(self, base_templates: List[str], composition_name: str, target_type: GenerationTarget) -> str:
    """
        Create a new template by composing existing templates.
        
        Args:
            base_templates: List of template names to compose
            composition_name: Name for the new composed template
            target_type: Target type for the composed template
            
        Returns:
            str: Name of the created composed template
        """
    composed_content = ''
    for template_name in base_templates:
        template_info = self._template_registry._templates.get(template_name)
        if template_info:
            composed_content += f"\n{{% include '{template_name}' %}}\n"
    self._template_registry.register_template(composition_name, composed_content, target_type)
    logger.info(f'Created composed template: {composition_name}')
    return composition_name

def export_template(self, template_name: str) -> Optional[Dict[str, Any]]:
    """
        Export a template for sharing or backup.
        
        Args:
            template_name: Name of template to export
            
        Returns:
            Optional[Dict]: Template export data
        """
    if template_name not in self._template_registry._templates:
        return None
    template_info = self._template_registry._templates[template_name]
    return {'name': template_name, 'content': template_info['content'], 'target_type': template_info['target_type'].value, 'parent': template_info['parent'], 'filters': list(template_info['filters'].keys()), 'exported_at': datetime.now().isoformat()}

def import_template(self, template_data: Dict[str, Any]) -> bool:
    """
        Import a template from export data.
        
        Args:
            template_data: Template export data
            
        Returns:
            bool: True if import successful
        """
    try:
        target_type = GenerationTarget(template_data['target_type'])
        self._template_registry.register_template(template_data['name'], template_data['content'], target_type, template_data.get('parent'))
        logger.info(f"Imported template: {template_data['name']}")
        return True
    except Exception as e:
        logger.error(f'Failed to import template: {e}')
        return False

def camel_case(text):
    """Convert text to camelCase."""
    components = text.split('_')
    return components[0] + ''.join((word.capitalize() for word in components[1:]))

def pascal_case(text):
    """Convert text to PascalCase."""
    return ''.join((word.capitalize() for word in text.split('_')))

def snake_case(text):
    """Convert text to snake_case."""
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', '\\1_\\2', text)
    return re.sub('([a-z0-9])([A-Z])', '\\1_\\2', s1).lower()

def save_to_file(self, base_path: Union[str, Path]) -> Path:
    """Save generated code to file."""
    base_path = Path(base_path)
    full_path = base_path / self.file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(self.code)
    logger.info(f'Generated code saved to {full_path}')
    return full_path

@abstractmethod
def generate(self, spec: GenerationSpec) -> GeneratedCode:
    """
        Generate code from specification.
        
        Args:
            spec: Generation specification
            
        Returns:
            GeneratedCode: Generated code with metadata
        """
    pass

@abstractmethod
def get_supported_target(self) -> GenerationTarget:
    """Get the target type this template supports."""
    pass

def __init__(self):
    self.template_content = '"""\n{{ name }} aggregate root for {{ domain_context }} domain.\n\nGenerated at {{ generated_at }}.\n"""\n\nfrom typing import Any, Dict, List, Optional\nfrom uuid import UUID\nfrom datetime import datetime\n\nfrom rm_ddd import AggregateRoot, ValidationResult, DomainBoundaries, AggregateBoundaries\nfrom rm_ddd.decorators import aggregate_root\n\n\n@aggregate_root("{{ domain_context }}", max_size={{ max_size }})\nclass {{ name }}(AggregateRoot[{{ id_type }}]):\n    """{{ description }}"""\n    \n    def __init__(self, {{ constructor_params }}):\n        super().__init__({{ id_param }}, "{{ domain_context }}")\n        {% for attr in attributes -%}\n        self.{{ attr.name }} = {{ attr.name }}\n        {% endfor %}\n    \n    {% for method in methods -%}\n    def {{ method.name }}(self{{ method.params }}):\n        """{{ method.description }}"""\n        {% if method.body -%}\n        {{ method.body | indent(8) }}\n        {% else -%}\n        pass\n        {% endif %}\n    \n    {% endfor -%}\n    \n    def get_domain_boundaries(self) -> DomainBoundaries:\n        """Get domain boundaries for this aggregate."""\n        return DomainBoundaries(\n            context="{{ domain_context }}",\n            invariants=[\n                {% for constraint in constraints -%}\n                "{{ constraint }}",\n                {% endfor %}\n            ]\n        )\n    \n    def get_aggregate_boundaries(self) -> AggregateBoundaries:\n        """Get aggregate consistency boundaries."""\n        return AggregateBoundaries(\n            aggregate_type="{{ name }}",\n            max_size={{ max_size }},\n            consistency_rules=[\n                {% for constraint in constraints -%}\n                "{{ constraint }}",\n                {% endfor %}\n            ],\n            invariants=[\n                {% for constraint in constraints -%}\n                "{{ constraint }}",\n                {% endfor %}\n            ]\n        )\n    \n    def validate_domain_invariants(self) -> ValidationResult:\n        """Validate domain invariants for this aggregate."""\n        result = ValidationResult(is_valid=True)\n        \n        {% for constraint in constraints -%}\n        # Validate: {{ constraint }}\n        # TODO: Implement validation logic\n        \n        {% endfor -%}\n        \n        return result\n'

def generate(self, spec: GenerationSpec) -> GeneratedCode:
    """Generate aggregate root code."""
    if not JINJA2_AVAILABLE:
        raise DomainException('Jinja2 is required for code generation but not available', error_code='JINJA2_NOT_AVAILABLE')
    validation_result = spec.validate_spec()
    if not validation_result.is_valid:
        raise DomainException(f'Invalid generation spec: {validation_result.errors}', error_code='INVALID_GENERATION_SPEC')
    context = self._prepare_context(spec)
    template = Template(self.template_content)
    code = template.render(**context)
    file_path = f'{spec.domain_context}/{spec.name.lower()}.py'
    return GeneratedCode(target_type=GenerationTarget.AGGREGATE_ROOT, name=spec.name, code=code, file_path=file_path, imports=self._get_imports(spec), dependencies=self._get_dependencies(spec))

def get_supported_target(self) -> GenerationTarget:
    """Get supported target type."""
    return GenerationTarget.AGGREGATE_ROOT

def _prepare_context(self, spec: GenerationSpec) -> Dict[str, Any]:
    """Prepare template context from spec."""
    entity_template = EntityTemplate()
    context = entity_template._prepare_context(spec)
    context['max_size'] = spec.metadata.get('max_size', 100)
    return context

def _get_imports(self, spec: GenerationSpec) -> List[str]:
    """Get required imports for the generated code."""
    imports = ['from typing import Any, Dict, List, Optional', 'from rm_ddd import AggregateRoot, ValidationResult, DomainBoundaries, AggregateBoundaries', 'from rm_ddd.decorators import aggregate_root']
    for attr in spec.attributes:
        attr_type = attr.get('type', '')
        if 'UUID' in attr_type:
            imports.append('from uuid import UUID')
        elif 'datetime' in attr_type:
            imports.append('from datetime import datetime')
    return list(set(imports))

def _get_dependencies(self, spec: GenerationSpec) -> List[str]:
    """Get dependencies for the generated code."""
    return ['rm_ddd']

def __init__(self):
    self._templates: Dict[str, Dict[str, Any]] = {}
    self._template_inheritance: Dict[str, str] = {}
    self._custom_filters: Dict[str, Callable] = {}
    self._template_cache: Dict[str, Template] = {}

def register_template(self, name: str, content: str, target_type: GenerationTarget, parent_template: Optional[str]=None, custom_filters: Optional[Dict[str, Callable]]=None):
    """Register a custom template with optional inheritance."""
    self._templates[name] = {'content': content, 'target_type': target_type, 'parent': parent_template, 'filters': custom_filters or {}}
    if parent_template:
        self._template_inheritance[name] = parent_template
    if custom_filters:
        self._custom_filters.update(custom_filters)
    if name in self._template_cache:
        del self._template_cache[name]
    logger.debug(f'Registered template: {name} for {target_type.value}')

def get_template(self, name: str) -> Optional[Template]:
    """Get a compiled template with inheritance resolution."""
    if name in self._template_cache:
        return self._template_cache[name]
    if name not in self._templates:
        return None
    template_info = self._templates[name]
    content = template_info['content']
    if template_info['parent']:
        parent_content = self._get_parent_content(template_info['parent'])
        content = self._merge_template_content(parent_content, content)
    if JINJA2_AVAILABLE:
        env = Environment()
        env.filters.update(self._custom_filters)
        env.filters.update(template_info['filters'])
        template = env.from_string(content)
        self._template_cache[name] = template
        return template
    return None

def _get_parent_content(self, parent_name: str) -> str:
    """Get parent template content recursively."""
    if parent_name not in self._templates:
        return ''
    parent_info = self._templates[parent_name]
    content = parent_info['content']
    if parent_info['parent']:
        grandparent_content = self._get_parent_content(parent_info['parent'])
        content = self._merge_template_content(grandparent_content, content)
    return content

def _merge_template_content(self, parent_content: str, child_content: str) -> str:
    """Merge parent and child template content."""
    parent_blocks = self._extract_blocks(parent_content)
    child_blocks = self._extract_blocks(child_content)
    merged_blocks = {**parent_blocks, **child_blocks}
    result = parent_content
    for block_name, block_content in merged_blocks.items():
        block_pattern = f'{{% block {block_name} %}}.+?{{% endblock %}}'
        replacement = f'{{% block {block_name} %}}{block_content}{{% endblock %}}'
        result = result.replace(f"{{% block {block_name} %}}{parent_blocks.get(block_name, '')}{{% endblock %}}", replacement)
    return result

def _extract_blocks(self, content: str) -> Dict[str, str]:
    """Extract Jinja2 blocks from template content."""
    import re
    blocks = {}
    block_pattern = '{%\\s*block\\s+(\\w+)\\s*%}(.*?){%\\s*endblock\\s*%}'
    matches = re.findall(block_pattern, content, re.DOTALL)
    for block_name, block_content in matches:
        blocks[block_name] = block_content.strip()
    return blocks

def list_templates(self) -> List[Dict[str, Any]]:
    """List all registered templates."""
    return [{'name': name, 'target_type': info['target_type'].value, 'parent': info['parent'], 'has_custom_filters': bool(info['filters'])} for name, info in self._templates.items()]

def __init__(self, template_registry: TemplateRegistry):
    self.template_registry = template_registry
    self._extension_points: Dict[str, Callable] = {}

def add_extension_point(self, name: str, handler: Callable):
    """Add an extension point for template customization."""
    self._extension_points[name] = handler
    logger.debug(f'Added extension point: {name}')

def apply_extensions(self, context: Dict[str, Any], spec: GenerationSpec) -> Dict[str, Any]:
    """Apply all registered extensions to the template context."""
    extended_context = context.copy()
    for name, handler in self._extension_points.items():
        try:
            extension_result = handler(extended_context, spec)
            if isinstance(extension_result, dict):
                extended_context.update(extension_result)
        except Exception as e:
            logger.warning(f'Extension point {name} failed: {e}')
    return extended_context

def get_custom_template(self, template_name: str) -> Optional[Template]:
    """Get a custom template from the registry."""
    return self.template_registry.get_template(template_name)

def __init__(self, domain_context: str='code_generation'):
    super().__init__(domain_context)
    self._templates: Dict[GenerationTarget, CodeTemplate] = {}
    self._generated_files: List[GeneratedCode] = []
    self._template_registry = TemplateRegistry()
    self._initialize_default_templates()
    self._register_default_custom_filters()

def _initialize_default_templates(self):
    """Initialize default code templates with customization support."""
    self._templates[GenerationTarget.ENTITY] = EnhancedEntityTemplate(self._template_registry)
    self._templates[GenerationTarget.AGGREGATE_ROOT] = AggregateRootTemplate()
    self._register_default_template_variations()
    logger.debug('Initialized enhanced code generation templates')

def _register_default_template_variations(self):
    """Register default template variations for common patterns."""
    simple_entity_template = '"""\n{{ name }} entity - Simple implementation.\n"""\n\nfrom rm_ddd import Entity, domain_entity\n\n@domain_entity("{{ domain_context }}")\nclass {{ name }}(Entity[str]):\n    def __init__(self, {{ id_param }}: str):\n        super().__init__({{ id_param }}, "{{ domain_context }}")\n        {% for attr in attributes -%}\n        self.{{ attr.name }} = None  # {{ attr.type }}\n        {% endfor %}\n'
    self._template_registry.register_template('entity_simple', simple_entity_template, GenerationTarget.ENTITY)
    rich_entity_template = '"""\n{{ name }} entity - Rich domain model.\n"""\n\nfrom typing import Any, Dict, List, Optional\nfrom rm_ddd import Entity, ValidationResult, DomainBoundaries, domain_entity\n\n@domain_entity("{{ domain_context }}")\nclass {{ name }}(Entity[{{ id_type }}]):\n    """{{ description }}"""\n    \n    def __init__(self, {{ constructor_params }}):\n        super().__init__({{ id_param }}, "{{ domain_context }}")\n        {% for attr in attributes -%}\n        self.{{ attr.name }} = {{ attr.name }}\n        {% endfor %}\n    \n    {% for method in business_methods -%}\n    def {{ method.name }}(self{{ method.params }}) -> {{ method.return_type }}:\n        """Business method: {{ method.name }}"""\n        {{ method.implementation | indent(8) }}\n    \n    {% endfor -%}\n    \n    {% for rule in validation_rules -%}\n    def _validate_{{ rule.name }}(self) -> bool:\n        """Validate {{ rule.name }}"""\n        {{ rule.implementation | indent(8) }}\n        return True\n    \n    {% endfor -%}\n    \n    def get_domain_boundaries(self) -> DomainBoundaries:\n        return DomainBoundaries(\n            context="{{ domain_context }}",\n            invariants=[\n                {% for constraint in constraints -%}\n                "{{ constraint }}",\n                {% endfor %}\n            ]\n        )\n    \n    def validate_domain_invariants(self) -> ValidationResult:\n        result = ValidationResult(is_valid=True)\n        \n        {% for rule in validation_rules -%}\n        if not self._validate_{{ rule.name }}():\n            result.add_error("{{ rule.name }} validation failed")\n        {% endfor %}\n        \n        return result\n'
    self._template_registry.register_template('entity_rich', rich_entity_template, GenerationTarget.ENTITY)

def _register_default_custom_filters(self):
    """Register default custom Jinja2 filters."""

    def camel_case(text):
        """Convert text to camelCase."""
        components = text.split('_')
        return components[0] + ''.join((word.capitalize() for word in components[1:]))

    def pascal_case(text):
        """Convert text to PascalCase."""
        return ''.join((word.capitalize() for word in text.split('_')))

    def snake_case(text):
        """Convert text to snake_case."""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', '\\1_\\2', text)
        return re.sub('([a-z0-9])([A-Z])', '\\1_\\2', s1).lower()
    custom_filters = {'camel_case': camel_case, 'pascal_case': pascal_case, 'snake_case': snake_case}
    for name, filter_func in custom_filters.items():
        self._template_registry._custom_filters[name] = filter_func

def add_template(self, template: CodeTemplate):
    """
        Add a custom code template.
        
        Args:
            template: Code template to add
        """
    target_type = template.get_supported_target()
    self._templates[target_type] = template
    logger.debug(f'Added custom template for {target_type.value}')

def generate_code(self, spec: GenerationSpec) -> GeneratedCode:
    """
        Generate code from specification.
        
        Args:
            spec: Generation specification
            
        Returns:
            GeneratedCode: Generated code with metadata
            
        Raises:
            DomainException: If generation fails
        """
    validation_result = spec.validate_spec()
    if not validation_result.is_valid:
        raise DomainException(f'Invalid generation specification: {validation_result.errors}', error_code='INVALID_GENERATION_SPEC')
    if spec.target_type not in self._templates:
        raise DomainException(f'No template available for target type: {spec.target_type.value}', error_code='TEMPLATE_NOT_FOUND')
    template = self._templates[spec.target_type]
    try:
        generated_code = template.generate(spec)
        self._generated_files.append(generated_code)
        logger.info(f'Generated {spec.target_type.value}: {spec.name}')
        return generated_code
    except Exception as e:
        logger.error(f'Code generation failed for {spec.name}: {e}')
        raise DomainException(f'Code generation failed: {str(e)}', error_code='CODE_GENERATION_FAILED')

def generate_entity(self, name: str, domain_context: str, attributes: List[Dict[str, Any]], **kwargs) -> GeneratedCode:
    """
        Generate a domain entity.
        
        Args:
            name: Entity name
            domain_context: Domain context
            attributes: Entity attributes
            **kwargs: Additional metadata
            
        Returns:
            GeneratedCode: Generated entity code
        """
    spec = GenerationSpec(target_type=GenerationTarget.ENTITY, name=name, domain_context=domain_context, attributes=attributes, methods=kwargs.get('methods', []), constraints=kwargs.get('constraints', []), metadata=kwargs)
    return self.generate_code(spec)

def generate_aggregate_root(self, name: str, domain_context: str, attributes: List[Dict[str, Any]], **kwargs) -> GeneratedCode:
    """
        Generate an aggregate root.
        
        Args:
            name: Aggregate name
            domain_context: Domain context
            attributes: Aggregate attributes
            **kwargs: Additional metadata
            
        Returns:
            GeneratedCode: Generated aggregate code
        """
    spec = GenerationSpec(target_type=GenerationTarget.AGGREGATE_ROOT, name=name, domain_context=domain_context, attributes=attributes, methods=kwargs.get('methods', []), constraints=kwargs.get('constraints', []), metadata=kwargs)
    return self.generate_code(spec)

def save_all_generated_code(self, base_path: Union[str, Path]) -> List[Path]:
    """
        Save all generated code to files.
        
        Args:
            base_path: Base directory path
            
        Returns:
            List[Path]: List of saved file paths
        """
    saved_paths = []
    for generated_code in self._generated_files:
        try:
            path = generated_code.save_to_file(base_path)
            saved_paths.append(path)
        except Exception as e:
            logger.error(f'Failed to save {generated_code.name}: {e}')
    logger.info(f'Saved {len(saved_paths)} generated files')
    return saved_paths

def get_generation_summary(self) -> Dict[str, Any]:
    """Get summary of code generation activity."""
    target_counts = {}
    for generated_code in self._generated_files:
        target_type = generated_code.target_type.value
        target_counts[target_type] = target_counts.get(target_type, 0) + 1
    return {'total_generated': len(self._generated_files), 'target_counts': target_counts, 'available_templates': [t.value for t in self._templates.keys()], 'generated_files': [{'name': gc.name, 'type': gc.target_type.value, 'file_path': gc.file_path, 'generated_at': gc.generated_at.isoformat()} for gc in self._generated_files]}

def get_domain_boundaries(self):
    """Get domain boundaries."""
    from ..models import DomainBoundaries
    return DomainBoundaries(context=self.domain_context, invariants=['Generated code must be syntactically valid', 'Generated code must follow RM-DDD patterns', 'All specifications must be validated before generation'])

def register_custom_template(self, name: str, content: str, target_type: GenerationTarget, parent_template: Optional[str]=None, custom_filters: Optional[Dict[str, Callable]]=None):
    """
        Register a custom template for code generation.
        
        Args:
            name: Template name
            content: Template content (Jinja2 format)
            target_type: Target generation type
            parent_template: Optional parent template for inheritance
            custom_filters: Optional custom Jinja2 filters
        """
    self._template_registry.register_template(name, content, target_type, parent_template, custom_filters)
    logger.info(f'Registered custom template: {name}')

def add_template_extension(self, target_type: GenerationTarget, extension_name: str, extension_handler: Callable):
    """
        Add an extension point to a template.
        
        Args:
            target_type: Target type to extend
            extension_name: Name of the extension point
            extension_handler: Handler function for the extension
        """
    if target_type in self._templates:
        template = self._templates[target_type]
        if isinstance(template, CustomizableCodeTemplate):
            template.add_extension_point(extension_name, extension_handler)
            logger.info(f'Added extension {extension_name} to {target_type.value}')

def generate_with_template(self, spec: GenerationSpec, template_name: Optional[str]=None) -> GeneratedCode:
    """
        Generate code using a specific template.
        
        Args:
            spec: Generation specification
            template_name: Optional specific template to use
            
        Returns:
            GeneratedCode: Generated code with metadata
        """
    if template_name:
        custom_template = self._template_registry.get_template(template_name)
        if custom_template and spec.target_type in self._templates:
            template = self._templates[spec.target_type]
            if isinstance(template, CustomizableCodeTemplate):
                return template._generate_with_custom_template(custom_template, spec)
    return self.generate_code(spec)

def list_available_templates(self) -> Dict[str, List[Dict[str, Any]]]:
    """
        List all available templates by target type.
        
        Returns:
            Dict mapping target types to available templates
        """
    templates_by_type = {}
    for template_info in self._template_registry.list_templates():
        target_type = template_info['target_type']
        if target_type not in templates_by_type:
            templates_by_type[target_type] = []
        templates_by_type[target_type].append(template_info)
    return templates_by_type

def create_template_composition(self, base_templates: List[str], composition_name: str, target_type: GenerationTarget) -> str:
    """
        Create a new template by composing existing templates.
        
        Args:
            base_templates: List of template names to compose
            composition_name: Name for the new composed template
            target_type: Target type for the composed template
            
        Returns:
            str: Name of the created composed template
        """
    composed_content = ''
    for template_name in base_templates:
        template_info = self._template_registry._templates.get(template_name)
        if template_info:
            composed_content += f"\n{{% include '{template_name}' %}}\n"
    self._template_registry.register_template(composition_name, composed_content, target_type)
    logger.info(f'Created composed template: {composition_name}')
    return composition_name

def export_template(self, template_name: str) -> Optional[Dict[str, Any]]:
    """
        Export a template for sharing or backup.
        
        Args:
            template_name: Name of template to export
            
        Returns:
            Optional[Dict]: Template export data
        """
    if template_name not in self._template_registry._templates:
        return None
    template_info = self._template_registry._templates[template_name]
    return {'name': template_name, 'content': template_info['content'], 'target_type': template_info['target_type'].value, 'parent': template_info['parent'], 'filters': list(template_info['filters'].keys()), 'exported_at': datetime.now().isoformat()}

def import_template(self, template_data: Dict[str, Any]) -> bool:
    """
        Import a template from export data.
        
        Args:
            template_data: Template export data
            
        Returns:
            bool: True if import successful
        """
    try:
        target_type = GenerationTarget(template_data['target_type'])
        self._template_registry.register_template(template_data['name'], template_data['content'], target_type, template_data.get('parent'))
        logger.info(f"Imported template: {template_data['name']}")
        return True
    except Exception as e:
        logger.error(f'Failed to import template: {e}')
        return False

def camel_case(text):
    """Convert text to camelCase."""
    components = text.split('_')
    return components[0] + ''.join((word.capitalize() for word in components[1:]))

def pascal_case(text):
    """Convert text to PascalCase."""
    return ''.join((word.capitalize() for word in text.split('_')))

def snake_case(text):
    """Convert text to snake_case."""
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', '\\1_\\2', text)
    return re.sub('([a-z0-9])([A-Z])', '\\1_\\2', s1).lower()

def camel_case(text):
    """Convert text to camelCase."""
    components = text.split('_')
    return components[0] + ''.join((word.capitalize() for word in components[1:]))

def pascal_case(text):
    """Convert text to PascalCase."""
    return ''.join((word.capitalize() for word in text.split('_')))

def snake_case(text):
    """Convert text to snake_case."""
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', '\\1_\\2', text)
    return re.sub('([a-z0-9])([A-Z])', '\\1_\\2', s1).lower()

def save_to_file(self, base_path: Union[str, Path]) -> Path:
    """Save generated code to file."""
    base_path = Path(base_path)
    full_path = base_path / self.file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(self.code)
    logger.info(f'Generated code saved to {full_path}')
    return full_path

@abstractmethod
def generate(self, spec: GenerationSpec) -> GeneratedCode:
    """
        Generate code from specification.
        
        Args:
            spec: Generation specification
            
        Returns:
            GeneratedCode: Generated code with metadata
        """
    pass

@abstractmethod
def get_supported_target(self) -> GenerationTarget:
    """Get the target type this template supports."""
    pass

def __init__(self):
    self.template_content = '"""\n{{ name }} aggregate root for {{ domain_context }} domain.\n\nGenerated at {{ generated_at }}.\n"""\n\nfrom typing import Any, Dict, List, Optional\nfrom uuid import UUID\nfrom datetime import datetime\n\nfrom rm_ddd import AggregateRoot, ValidationResult, DomainBoundaries, AggregateBoundaries\nfrom rm_ddd.decorators import aggregate_root\n\n\n@aggregate_root("{{ domain_context }}", max_size={{ max_size }})\nclass {{ name }}(AggregateRoot[{{ id_type }}]):\n    """{{ description }}"""\n    \n    def __init__(self, {{ constructor_params }}):\n        super().__init__({{ id_param }}, "{{ domain_context }}")\n        {% for attr in attributes -%}\n        self.{{ attr.name }} = {{ attr.name }}\n        {% endfor %}\n    \n    {% for method in methods -%}\n    def {{ method.name }}(self{{ method.params }}):\n        """{{ method.description }}"""\n        {% if method.body -%}\n        {{ method.body | indent(8) }}\n        {% else -%}\n        pass\n        {% endif %}\n    \n    {% endfor -%}\n    \n    def get_domain_boundaries(self) -> DomainBoundaries:\n        """Get domain boundaries for this aggregate."""\n        return DomainBoundaries(\n            context="{{ domain_context }}",\n            invariants=[\n                {% for constraint in constraints -%}\n                "{{ constraint }}",\n                {% endfor %}\n            ]\n        )\n    \n    def get_aggregate_boundaries(self) -> AggregateBoundaries:\n        """Get aggregate consistency boundaries."""\n        return AggregateBoundaries(\n            aggregate_type="{{ name }}",\n            max_size={{ max_size }},\n            consistency_rules=[\n                {% for constraint in constraints -%}\n                "{{ constraint }}",\n                {% endfor %}\n            ],\n            invariants=[\n                {% for constraint in constraints -%}\n                "{{ constraint }}",\n                {% endfor %}\n            ]\n        )\n    \n    def validate_domain_invariants(self) -> ValidationResult:\n        """Validate domain invariants for this aggregate."""\n        result = ValidationResult(is_valid=True)\n        \n        {% for constraint in constraints -%}\n        # Validate: {{ constraint }}\n        # TODO: Implement validation logic\n        \n        {% endfor -%}\n        \n        return result\n'

def generate(self, spec: GenerationSpec) -> GeneratedCode:
    """Generate aggregate root code."""
    if not JINJA2_AVAILABLE:
        raise DomainException('Jinja2 is required for code generation but not available', error_code='JINJA2_NOT_AVAILABLE')
    validation_result = spec.validate_spec()
    if not validation_result.is_valid:
        raise DomainException(f'Invalid generation spec: {validation_result.errors}', error_code='INVALID_GENERATION_SPEC')
    context = self._prepare_context(spec)
    template = Template(self.template_content)
    code = template.render(**context)
    file_path = f'{spec.domain_context}/{spec.name.lower()}.py'
    return GeneratedCode(target_type=GenerationTarget.AGGREGATE_ROOT, name=spec.name, code=code, file_path=file_path, imports=self._get_imports(spec), dependencies=self._get_dependencies(spec))

def get_supported_target(self) -> GenerationTarget:
    """Get supported target type."""
    return GenerationTarget.AGGREGATE_ROOT

def _prepare_context(self, spec: GenerationSpec) -> Dict[str, Any]:
    """Prepare template context from spec."""
    entity_template = EntityTemplate()
    context = entity_template._prepare_context(spec)
    context['max_size'] = spec.metadata.get('max_size', 100)
    return context

def _get_imports(self, spec: GenerationSpec) -> List[str]:
    """Get required imports for the generated code."""
    imports = ['from typing import Any, Dict, List, Optional', 'from rm_ddd import AggregateRoot, ValidationResult, DomainBoundaries, AggregateBoundaries', 'from rm_ddd.decorators import aggregate_root']
    for attr in spec.attributes:
        attr_type = attr.get('type', '')
        if 'UUID' in attr_type:
            imports.append('from uuid import UUID')
        elif 'datetime' in attr_type:
            imports.append('from datetime import datetime')
    return list(set(imports))

def _get_dependencies(self, spec: GenerationSpec) -> List[str]:
    """Get dependencies for the generated code."""
    return ['rm_ddd']

def __init__(self):
    self._templates: Dict[str, Dict[str, Any]] = {}
    self._template_inheritance: Dict[str, str] = {}
    self._custom_filters: Dict[str, Callable] = {}
    self._template_cache: Dict[str, Template] = {}

def register_template(self, name: str, content: str, target_type: GenerationTarget, parent_template: Optional[str]=None, custom_filters: Optional[Dict[str, Callable]]=None):
    """Register a custom template with optional inheritance."""
    self._templates[name] = {'content': content, 'target_type': target_type, 'parent': parent_template, 'filters': custom_filters or {}}
    if parent_template:
        self._template_inheritance[name] = parent_template
    if custom_filters:
        self._custom_filters.update(custom_filters)
    if name in self._template_cache:
        del self._template_cache[name]
    logger.debug(f'Registered template: {name} for {target_type.value}')

def get_template(self, name: str) -> Optional[Template]:
    """Get a compiled template with inheritance resolution."""
    if name in self._template_cache:
        return self._template_cache[name]
    if name not in self._templates:
        return None
    template_info = self._templates[name]
    content = template_info['content']
    if template_info['parent']:
        parent_content = self._get_parent_content(template_info['parent'])
        content = self._merge_template_content(parent_content, content)
    if JINJA2_AVAILABLE:
        env = Environment()
        env.filters.update(self._custom_filters)
        env.filters.update(template_info['filters'])
        template = env.from_string(content)
        self._template_cache[name] = template
        return template
    return None

def _get_parent_content(self, parent_name: str) -> str:
    """Get parent template content recursively."""
    if parent_name not in self._templates:
        return ''
    parent_info = self._templates[parent_name]
    content = parent_info['content']
    if parent_info['parent']:
        grandparent_content = self._get_parent_content(parent_info['parent'])
        content = self._merge_template_content(grandparent_content, content)
    return content

def _merge_template_content(self, parent_content: str, child_content: str) -> str:
    """Merge parent and child template content."""
    parent_blocks = self._extract_blocks(parent_content)
    child_blocks = self._extract_blocks(child_content)
    merged_blocks = {**parent_blocks, **child_blocks}
    result = parent_content
    for block_name, block_content in merged_blocks.items():
        block_pattern = f'{{% block {block_name} %}}.+?{{% endblock %}}'
        replacement = f'{{% block {block_name} %}}{block_content}{{% endblock %}}'
        result = result.replace(f"{{% block {block_name} %}}{parent_blocks.get(block_name, '')}{{% endblock %}}", replacement)
    return result

def _extract_blocks(self, content: str) -> Dict[str, str]:
    """Extract Jinja2 blocks from template content."""
    import re
    blocks = {}
    block_pattern = '{%\\s*block\\s+(\\w+)\\s*%}(.*?){%\\s*endblock\\s*%}'
    matches = re.findall(block_pattern, content, re.DOTALL)
    for block_name, block_content in matches:
        blocks[block_name] = block_content.strip()
    return blocks

def list_templates(self) -> List[Dict[str, Any]]:
    """List all registered templates."""
    return [{'name': name, 'target_type': info['target_type'].value, 'parent': info['parent'], 'has_custom_filters': bool(info['filters'])} for name, info in self._templates.items()]

def __init__(self, template_registry: TemplateRegistry):
    self.template_registry = template_registry
    self._extension_points: Dict[str, Callable] = {}

def add_extension_point(self, name: str, handler: Callable):
    """Add an extension point for template customization."""
    self._extension_points[name] = handler
    logger.debug(f'Added extension point: {name}')

def apply_extensions(self, context: Dict[str, Any], spec: GenerationSpec) -> Dict[str, Any]:
    """Apply all registered extensions to the template context."""
    extended_context = context.copy()
    for name, handler in self._extension_points.items():
        try:
            extension_result = handler(extended_context, spec)
            if isinstance(extension_result, dict):
                extended_context.update(extension_result)
        except Exception as e:
            logger.warning(f'Extension point {name} failed: {e}')
    return extended_context

def get_custom_template(self, template_name: str) -> Optional[Template]:
    """Get a custom template from the registry."""
    return self.template_registry.get_template(template_name)

def __init__(self, domain_context: str='code_generation'):
    super().__init__(domain_context)
    self._templates: Dict[GenerationTarget, CodeTemplate] = {}
    self._generated_files: List[GeneratedCode] = []
    self._template_registry = TemplateRegistry()
    self._initialize_default_templates()
    self._register_default_custom_filters()

def _initialize_default_templates(self):
    """Initialize default code templates with customization support."""
    self._templates[GenerationTarget.ENTITY] = EnhancedEntityTemplate(self._template_registry)
    self._templates[GenerationTarget.AGGREGATE_ROOT] = AggregateRootTemplate()
    self._register_default_template_variations()
    logger.debug('Initialized enhanced code generation templates')

def _register_default_template_variations(self):
    """Register default template variations for common patterns."""
    simple_entity_template = '"""\n{{ name }} entity - Simple implementation.\n"""\n\nfrom rm_ddd import Entity, domain_entity\n\n@domain_entity("{{ domain_context }}")\nclass {{ name }}(Entity[str]):\n    def __init__(self, {{ id_param }}: str):\n        super().__init__({{ id_param }}, "{{ domain_context }}")\n        {% for attr in attributes -%}\n        self.{{ attr.name }} = None  # {{ attr.type }}\n        {% endfor %}\n'
    self._template_registry.register_template('entity_simple', simple_entity_template, GenerationTarget.ENTITY)
    rich_entity_template = '"""\n{{ name }} entity - Rich domain model.\n"""\n\nfrom typing import Any, Dict, List, Optional\nfrom rm_ddd import Entity, ValidationResult, DomainBoundaries, domain_entity\n\n@domain_entity("{{ domain_context }}")\nclass {{ name }}(Entity[{{ id_type }}]):\n    """{{ description }}"""\n    \n    def __init__(self, {{ constructor_params }}):\n        super().__init__({{ id_param }}, "{{ domain_context }}")\n        {% for attr in attributes -%}\n        self.{{ attr.name }} = {{ attr.name }}\n        {% endfor %}\n    \n    {% for method in business_methods -%}\n    def {{ method.name }}(self{{ method.params }}) -> {{ method.return_type }}:\n        """Business method: {{ method.name }}"""\n        {{ method.implementation | indent(8) }}\n    \n    {% endfor -%}\n    \n    {% for rule in validation_rules -%}\n    def _validate_{{ rule.name }}(self) -> bool:\n        """Validate {{ rule.name }}"""\n        {{ rule.implementation | indent(8) }}\n        return True\n    \n    {% endfor -%}\n    \n    def get_domain_boundaries(self) -> DomainBoundaries:\n        return DomainBoundaries(\n            context="{{ domain_context }}",\n            invariants=[\n                {% for constraint in constraints -%}\n                "{{ constraint }}",\n                {% endfor %}\n            ]\n        )\n    \n    def validate_domain_invariants(self) -> ValidationResult:\n        result = ValidationResult(is_valid=True)\n        \n        {% for rule in validation_rules -%}\n        if not self._validate_{{ rule.name }}():\n            result.add_error("{{ rule.name }} validation failed")\n        {% endfor %}\n        \n        return result\n'
    self._template_registry.register_template('entity_rich', rich_entity_template, GenerationTarget.ENTITY)

def _register_default_custom_filters(self):
    """Register default custom Jinja2 filters."""

    def camel_case(text):
        """Convert text to camelCase."""
        components = text.split('_')
        return components[0] + ''.join((word.capitalize() for word in components[1:]))

    def pascal_case(text):
        """Convert text to PascalCase."""
        return ''.join((word.capitalize() for word in text.split('_')))

    def snake_case(text):
        """Convert text to snake_case."""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', '\\1_\\2', text)
        return re.sub('([a-z0-9])([A-Z])', '\\1_\\2', s1).lower()
    custom_filters = {'camel_case': camel_case, 'pascal_case': pascal_case, 'snake_case': snake_case}
    for name, filter_func in custom_filters.items():
        self._template_registry._custom_filters[name] = filter_func

def add_template(self, template: CodeTemplate):
    """
        Add a custom code template.
        
        Args:
            template: Code template to add
        """
    target_type = template.get_supported_target()
    self._templates[target_type] = template
    logger.debug(f'Added custom template for {target_type.value}')

def generate_code(self, spec: GenerationSpec) -> GeneratedCode:
    """
        Generate code from specification.
        
        Args:
            spec: Generation specification
            
        Returns:
            GeneratedCode: Generated code with metadata
            
        Raises:
            DomainException: If generation fails
        """
    validation_result = spec.validate_spec()
    if not validation_result.is_valid:
        raise DomainException(f'Invalid generation specification: {validation_result.errors}', error_code='INVALID_GENERATION_SPEC')
    if spec.target_type not in self._templates:
        raise DomainException(f'No template available for target type: {spec.target_type.value}', error_code='TEMPLATE_NOT_FOUND')
    template = self._templates[spec.target_type]
    try:
        generated_code = template.generate(spec)
        self._generated_files.append(generated_code)
        logger.info(f'Generated {spec.target_type.value}: {spec.name}')
        return generated_code
    except Exception as e:
        logger.error(f'Code generation failed for {spec.name}: {e}')
        raise DomainException(f'Code generation failed: {str(e)}', error_code='CODE_GENERATION_FAILED')

def generate_entity(self, name: str, domain_context: str, attributes: List[Dict[str, Any]], **kwargs) -> GeneratedCode:
    """
        Generate a domain entity.
        
        Args:
            name: Entity name
            domain_context: Domain context
            attributes: Entity attributes
            **kwargs: Additional metadata
            
        Returns:
            GeneratedCode: Generated entity code
        """
    spec = GenerationSpec(target_type=GenerationTarget.ENTITY, name=name, domain_context=domain_context, attributes=attributes, methods=kwargs.get('methods', []), constraints=kwargs.get('constraints', []), metadata=kwargs)
    return self.generate_code(spec)

def generate_aggregate_root(self, name: str, domain_context: str, attributes: List[Dict[str, Any]], **kwargs) -> GeneratedCode:
    """
        Generate an aggregate root.
        
        Args:
            name: Aggregate name
            domain_context: Domain context
            attributes: Aggregate attributes
            **kwargs: Additional metadata
            
        Returns:
            GeneratedCode: Generated aggregate code
        """
    spec = GenerationSpec(target_type=GenerationTarget.AGGREGATE_ROOT, name=name, domain_context=domain_context, attributes=attributes, methods=kwargs.get('methods', []), constraints=kwargs.get('constraints', []), metadata=kwargs)
    return self.generate_code(spec)

def save_all_generated_code(self, base_path: Union[str, Path]) -> List[Path]:
    """
        Save all generated code to files.
        
        Args:
            base_path: Base directory path
            
        Returns:
            List[Path]: List of saved file paths
        """
    saved_paths = []
    for generated_code in self._generated_files:
        try:
            path = generated_code.save_to_file(base_path)
            saved_paths.append(path)
        except Exception as e:
            logger.error(f'Failed to save {generated_code.name}: {e}')
    logger.info(f'Saved {len(saved_paths)} generated files')
    return saved_paths

def get_generation_summary(self) -> Dict[str, Any]:
    """Get summary of code generation activity."""
    target_counts = {}
    for generated_code in self._generated_files:
        target_type = generated_code.target_type.value
        target_counts[target_type] = target_counts.get(target_type, 0) + 1
    return {'total_generated': len(self._generated_files), 'target_counts': target_counts, 'available_templates': [t.value for t in self._templates.keys()], 'generated_files': [{'name': gc.name, 'type': gc.target_type.value, 'file_path': gc.file_path, 'generated_at': gc.generated_at.isoformat()} for gc in self._generated_files]}

def get_domain_boundaries(self):
    """Get domain boundaries."""
    from ..models import DomainBoundaries
    return DomainBoundaries(context=self.domain_context, invariants=['Generated code must be syntactically valid', 'Generated code must follow RM-DDD patterns', 'All specifications must be validated before generation'])

def register_custom_template(self, name: str, content: str, target_type: GenerationTarget, parent_template: Optional[str]=None, custom_filters: Optional[Dict[str, Callable]]=None):
    """
        Register a custom template for code generation.
        
        Args:
            name: Template name
            content: Template content (Jinja2 format)
            target_type: Target generation type
            parent_template: Optional parent template for inheritance
            custom_filters: Optional custom Jinja2 filters
        """
    self._template_registry.register_template(name, content, target_type, parent_template, custom_filters)
    logger.info(f'Registered custom template: {name}')

def add_template_extension(self, target_type: GenerationTarget, extension_name: str, extension_handler: Callable):
    """
        Add an extension point to a template.
        
        Args:
            target_type: Target type to extend
            extension_name: Name of the extension point
            extension_handler: Handler function for the extension
        """
    if target_type in self._templates:
        template = self._templates[target_type]
        if isinstance(template, CustomizableCodeTemplate):
            template.add_extension_point(extension_name, extension_handler)
            logger.info(f'Added extension {extension_name} to {target_type.value}')

def generate_with_template(self, spec: GenerationSpec, template_name: Optional[str]=None) -> GeneratedCode:
    """
        Generate code using a specific template.
        
        Args:
            spec: Generation specification
            template_name: Optional specific template to use
            
        Returns:
            GeneratedCode: Generated code with metadata
        """
    if template_name:
        custom_template = self._template_registry.get_template(template_name)
        if custom_template and spec.target_type in self._templates:
            template = self._templates[spec.target_type]
            if isinstance(template, CustomizableCodeTemplate):
                return template._generate_with_custom_template(custom_template, spec)
    return self.generate_code(spec)

def list_available_templates(self) -> Dict[str, List[Dict[str, Any]]]:
    """
        List all available templates by target type.
        
        Returns:
            Dict mapping target types to available templates
        """
    templates_by_type = {}
    for template_info in self._template_registry.list_templates():
        target_type = template_info['target_type']
        if target_type not in templates_by_type:
            templates_by_type[target_type] = []
        templates_by_type[target_type].append(template_info)
    return templates_by_type

def create_template_composition(self, base_templates: List[str], composition_name: str, target_type: GenerationTarget) -> str:
    """
        Create a new template by composing existing templates.
        
        Args:
            base_templates: List of template names to compose
            composition_name: Name for the new composed template
            target_type: Target type for the composed template
            
        Returns:
            str: Name of the created composed template
        """
    composed_content = ''
    for template_name in base_templates:
        template_info = self._template_registry._templates.get(template_name)
        if template_info:
            composed_content += f"\n{{% include '{template_name}' %}}\n"
    self._template_registry.register_template(composition_name, composed_content, target_type)
    logger.info(f'Created composed template: {composition_name}')
    return composition_name

def export_template(self, template_name: str) -> Optional[Dict[str, Any]]:
    """
        Export a template for sharing or backup.
        
        Args:
            template_name: Name of template to export
            
        Returns:
            Optional[Dict]: Template export data
        """
    if template_name not in self._template_registry._templates:
        return None
    template_info = self._template_registry._templates[template_name]
    return {'name': template_name, 'content': template_info['content'], 'target_type': template_info['target_type'].value, 'parent': template_info['parent'], 'filters': list(template_info['filters'].keys()), 'exported_at': datetime.now().isoformat()}

def import_template(self, template_data: Dict[str, Any]) -> bool:
    """
        Import a template from export data.
        
        Args:
            template_data: Template export data
            
        Returns:
            bool: True if import successful
        """
    try:
        target_type = GenerationTarget(template_data['target_type'])
        self._template_registry.register_template(template_data['name'], template_data['content'], target_type, template_data.get('parent'))
        logger.info(f"Imported template: {template_data['name']}")
        return True
    except Exception as e:
        logger.error(f'Failed to import template: {e}')
        return False

def camel_case(text):
    """Convert text to camelCase."""
    components = text.split('_')
    return components[0] + ''.join((word.capitalize() for word in components[1:]))

def pascal_case(text):
    """Convert text to PascalCase."""
    return ''.join((word.capitalize() for word in text.split('_')))

def snake_case(text):
    """Convert text to snake_case."""
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', '\\1_\\2', text)
    return re.sub('([a-z0-9])([A-Z])', '\\1_\\2', s1).lower()

def camel_case(text):
    """Convert text to camelCase."""
    components = text.split('_')
    return components[0] + ''.join((word.capitalize() for word in components[1:]))

def pascal_case(text):
    """Convert text to PascalCase."""
    return ''.join((word.capitalize() for word in text.split('_')))

def snake_case(text):
    """Convert text to snake_case."""
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', '\\1_\\2', text)
    return re.sub('([a-z0-9])([A-Z])', '\\1_\\2', s1).lower()

def camel_case(text):
    """Convert text to camelCase."""
    components = text.split('_')
    return components[0] + ''.join((word.capitalize() for word in components[1:]))

def pascal_case(text):
    """Convert text to PascalCase."""
    return ''.join((word.capitalize() for word in text.split('_')))

def snake_case(text):
    """Convert text to snake_case."""
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', '\\1_\\2', text)
    return re.sub('([a-z0-9])([A-Z])', '\\1_\\2', s1).lower()
