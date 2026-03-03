# ag-skills

Agricultural data analysis skills package for students.

## Installation

### From GitHub (Recommended for Students)

```bash
pip install git+https://github.com/borealBytes/ag-skills.git
```

### Development Installation

```bash
git clone https://github.com/borealBytes/ag-skills.git
cd ag-skills
pip install -e ".[dev]"
```

## Quick Start

```python
import ag_skills

# Skills will be available as:
# from ag_skills.skill_name import SkillClass
```

## Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=ag_skills --cov-report=term-missing
```

## Package Structure

```
ag-skills/
├── src/ag_skills/          # Main package
├── tests/                   # Test suite
├── data/samples/            # Sample data files
├── pyproject.toml          # Package configuration
└── README.md               # This file
```

## Dependencies

- pandas: Data manipulation and analysis
- numpy: Numerical computing
- matplotlib: Plotting and visualization
- seaborn: Statistical data visualization
- geopandas: Geospatial data analysis
- shapely: Geometric operations

## License

MIT License - see LICENSE file for details.
