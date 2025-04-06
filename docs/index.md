# Welcome to Unilock Documentation

![Unilock Logo](img/logo.png){ width=200 }

Unilock simplifies Keycloak management with:
- 🔐 Easy-to-use admin interface  
- 🚀 FastAPI-powered backend
- 🎨 Customizable UI components

```python
from fastapi import FastAPI
from unilock import Unilock

app = FastAPI()
app.include_router(Unilock().router)
```

## Quick Links

- [Getting Started](dev/setup.md)
- [API Reference](api/auth.md)
- [Contributing Guide](../CONTRIBUTING.md)

## Key Features

???+ note "Developer Friendly"
    - RESTful API design
    - Interactive OpenAPI docs
    - Comprehensive SDKs

!!! success "Enterprise Ready"
    - Role-based access control  
    - Audit logging
