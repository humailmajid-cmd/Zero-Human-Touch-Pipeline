"""
Stage 2: Build web app using Claude API
"""
import os
import json
import tempfile
import subprocess
from typing import Optional, Dict
from utils.logger import get_logger

logger = get_logger('stage_2_build')

class BuildStage:
    def __init__(self, requirements: str, output_dir: str):
        self.requirements = requirements
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def run(self) -> Optional[Dict]:
        """
        Build the web app based on requirements
        Uses Claude API via a dedicated build agent
        Returns: Dictionary with build status and output directory
        """
        try:
            logger.info("Starting build stage")
            
            # For now, we'll create a stub that expects an external build agent
            # In production, this would integrate with Claude API or aider
            
            # Create a build script that will be executed
            build_script = os.path.join(self.output_dir, 'BUILD_INSTRUCTIONS.md')
            with open(build_script, 'w') as f:
                f.write("# Build Instructions\n\n")
                f.write("An external agent (Claude Code, aider, or Cursor) should:\n\n")
                f.write("1. Read the requirements\n")
                f.write("2. Create a working web app\n")
                f.write("3. Output all files to this directory\n\n")
                f.write("## Requirements\n\n")
                f.write(self.requirements)
            
            logger.info(f"Build stage configured. Output directory: {self.output_dir}")
            logger.info("Manual agent intervention required to build the application")
            
            return {
                'status': 'pending',
                'output_dir': self.output_dir,
                'build_script': build_script
            }
        
        except Exception as e:
            logger.error(f"Error in build stage: {e}", exc_info=True)
            return None

def stage_2_build(requirements: str, output_dir: str = None):
    """Execute Stage 2"""
    if not output_dir:
        output_dir = tempfile.mkdtemp(prefix='build_')
    
    builder = BuildStage(requirements, output_dir)
    return builder.run()
