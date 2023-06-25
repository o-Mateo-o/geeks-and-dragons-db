"""A database manager app allowing to 
- clear the database, give it a new structure, and fill it with the random data,
- generate a report from the database,
- open the newest report automatically.

Use it the following way

```python
from src import DBManagerApp
DBManagerApp().run(f, r, o)
```

Best to utilize the package almost directly with the terminal.
"""

from .app import DBManagerApp
