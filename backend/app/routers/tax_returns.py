"""REST endpoints for annual historical tax returns."""

from __future__ import annotations

from app import crud, models, schemas
from app.routers.flat_resource import make_flat_router

router = make_flat_router(
    path="/tax-returns",
    tag="tax_returns",
    noun="tax return",
    model=models.TaxReturn,
    read_schema=schemas.TaxReturnRead,
    create_schema=schemas.TaxReturnCreate,
    list_all=crud.get_tax_returns,
    create=crud.create_tax_return,
    update=crud.update_tax_return,
    delete=crud.delete_tax_return,
)
