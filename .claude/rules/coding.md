# Coding Rules

## Python Conventions

- Python 3.11+ required
- PEP 8 compliance (black formatter, ruff linter)
- Type hints required on all functions
- Google-style docstrings
- Use f-strings (% formatting and .format() are prohibited)

## Code Patterns

- **Data models**: Use Pydantic BaseModel
- **Logging**: Use structlog, structured JSON logging
- **Retries**: Retry API calls with the tenacity library (max 3 times, exponential backoff)
- **Configuration**: Manage environment variables + YAML together via pydantic-settings
- **DB**: SQLAlchemy ORM, with async support
- **Inheritance**: Each module defines a base class, and concrete implementations inherit from it

## Matplotlib Chart Authoring Rules

### Korean Fonts (Linux/WSL)

```python
import matplotlib.font_manager as _fm
import matplotlib.pyplot as plt

# Note: rcParams alone won't work — register the file directly with addfont() then specify family
_KOREAN_FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if os.path.exists(_KOREAN_FONT_PATH):
    _fm.fontManager.addfont(_KOREAN_FONT_PATH)
    # addfont() only registers the first font (JP) in the .ttc collection → its name is "Noto Sans CJK JP"
    # The JP font also contains Korean glyphs — rendering works correctly
    plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["axes.unicode_minus"] = False  # Required: prevents the minus (−) sign from breaking
```

- If you set only the family name without `addfont()`, matplotlib won't recognize the system font
- If `axes.unicode_minus = False` is not set, negative signs render as □
- Headless environments (server / WSL email sending, etc.): the `matplotlib.use("Agg")` backend is required

### Y-Axis Scale Rules (house rule)

**Absolutely prohibited**: Setting the Y-axis to `0 ~ max` — the variation becomes invisible

**Required**: Apply `min - 10% ~ max + 10%` padding

```python
def _set_ylim_padded(ax, data_min, data_max, pad=0.10):
    rng = data_max - data_min
    if rng == 0:
        rng = abs(data_min) if data_min != 0 else 1.0
    ax.set_ylim(data_min - pad * rng, data_max + pad * rng)
```

- Axes where multiple series overlap: compute from the overall min/max
- Flow (inflow/outflow) bar charts: always include 0 first, then pad (`lo = min(flow.min(), 0)`)
- Normalized charts (base = 100): use the combined min/max of all normalized series

## Work Quality Checklist

When the work is complete, verify the items below:

- [ ] Type hints applied
- [ ] Google-style docstrings written
- [ ] Error handling and logging applied
- [ ] Security rules followed (no hardcoded API keys)
- [ ] Existing base class pattern followed
- [ ] Run/execution tests passing
