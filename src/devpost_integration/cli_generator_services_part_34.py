
    def generate_cli_entry_point(self, module: ReflectiveModule) -> str:
        """Generate CLI entry point script"""
        module_info = module.get_module_info()
        entry_point = f'''#!/usr/bin/env python3\n"""\nAuto-generated CLI entry point for {module_info['name']}\nModule ID: {module.module_id}\n"""\n\nimport sys\nfrom pathlib import Path\n\n# Add src to path\nsrc_path = Path(__file__).parent.parent\nsys.path.insert(0, str(src_path))\n\n# Import and run the CLI\nfrom {module.__class__.__module__} import {module.__class__.__name__}\nfrom devpost_integration.cli_generator import CLIGeneratorEngine\n\ndef main():\n    # Initialize module\n    module = {module.__class__.__name__}()\n    \n    # Generate and execute CLI\n    generator = CLIGeneratorEngine()\n    analysis = generator.analyze_module(module)\n    cli_code = generator.generate_cli_code(analysis)\n    \n    # Execute the generated CLI\n    exec(cli_code)\n\nif __name__ == '__main__':\n    main()\n'''
        return entry_point
