# Import Organization Standards

This document defines the import organization standards for the Choral LLM Workbench project to ensure consistency and maintainability across all Python files.

## Import Order

Imports should be organized in the following order:

1. **Standard library imports**
2. **Third-party library imports**
3. **Local application imports**
4. **Relative imports** (avoid when possible)

Each section should be separated by a blank line.

## Import Formatting Rules

### 1. Standard Library Imports
```python
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union
```

### 2. Third-Party Library Imports
```python
import gradio as gr
import music21
import numpy as np
import yaml
from mido import MidiFile
```

### 3. Local Application Imports
```python
from core.config import Config, AppConfig
from core.constants import AudioDefaults, VoiceInfo
from core.exceptions import ChoralWorkbenchError, ValidationError
from core.validation import validate_musicxml_path
from llm.ollama_adapter import OllamaAdapter
```

### 4. Relative Imports (Use Sparingly)
```python
from .utils import helper_function
from .models import DataModel
```

## Specific Guidelines

### 1. Import Style
- Use `import module` for standard library and most third-party imports
- Use `import module as alias` when the module name is long or commonly abbreviated
- Use `from module import specific_item` when you need specific classes/functions
- Avoid `from module import *` except in special cases (like `__init__.py` files)

### 2. Alias Conventions
```python
# Standard aliases
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gradio as gr

# Project-specific aliases
from core.config import ConfigManager as Config
from core.i18n import get_i18n as _
```

### 3. Grouping Related Imports
```python
# File system related
import os
import shutil
from pathlib import Path

# Data handling
import json
import yaml
from typing import Dict, List, Optional

# Scientific computing
import numpy as np
from music21 import stream, note, meter
```

### 4. Conditional Imports
```python
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    plt = None
```

## File Template

Here's a template for new Python files:

```python
"""
Module description for the Choral LLM Workbench.

This module provides [brief description of functionality].
"""

# Standard library imports
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union

# Third-party library imports
import gradio as gr
import music21
import numpy as np
import yaml

# Local application imports
from core.config import get_config
from core.constants import AudioDefaults, VoiceInfo
from core.exceptions import ChoralWorkbenchError, ValidationError
from core.validation import validate_musicxml_path, validate_base_tuning


def example_function(param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """Example function with proper type hints.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2
        
    Returns:
        Dictionary with results
    """
    pass
```

## Import Sorting Tools

To maintain consistent import organization, use tools like:

### 1. isort
```bash
pip install isort
isort .
```

### 2. Black (includes import sorting)
```bash
pip install black
black .
```

### 3. VS Code / IDE Integration
Most IDEs can automatically sort imports according to these standards.

## Common Import Patterns by Module Type

### CLI Modules
```python
# Standard library
import argparse
import sys

# Third-party
import gradio as gr

# Local
from core.config import get_config
from core.audio import render_audio
from core.score import load_musicxml
```

### Core Service Modules
```python
# Standard library
import logging
from pathlib import Path
from typing import Dict, List, Optional

# Third-party
import music21
import numpy as np

# Local
from core.config import AppConfig
from core.constants import AudioDefaults
from core.exceptions import AudioRenderingError
```

### Test Modules
```python
# Standard library
import unittest
from pathlib import Path

# Third-party
import pytest
from music21 import stream

# Local
from core.score import load_musicxml, write_musicxml
from core.validation import validate_musicxml_path
```

## Enforcement

These import standards will be enforced through:

1. **Pre-commit hooks** using isort and black
2. **Code review** processes
3. **CI/CD pipeline** checks
4. **IDE configuration** for automatic formatting

## Migration Strategy

When updating existing files:

1. Run `isort` to automatically sort imports
2. Manually review and adjust any issues
3. Group related imports logically
4. Add appropriate blank lines between sections
5. Update import aliases to follow conventions

## Examples of Good vs Bad Import Organization

### Good Example ✅
```python
# Standard library imports
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

# Third-party library imports
import gradio as gr
import music21
import numpy as np

# Local application imports
from core.config import get_config
from core.constants import AudioDefaults
from core.exceptions import ValidationError
```

### Bad Example ❌
```python
import os
from pathlib import Path
import gradio as gr
from core.config import get_config
import music21
import numpy as np
from typing import Dict, List, Optional
from core.constants import AudioDefaults
from core.exceptions import ValidationError
import tempfile
```

Following these standards will ensure consistent, readable, and maintainable import organization across the entire Choral LLM Workbench project.