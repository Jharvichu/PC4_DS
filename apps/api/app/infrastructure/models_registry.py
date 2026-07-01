"""Central import of every ORM model so Base.metadata is fully populated.

Import this module (for its side effects only) wherever SQLAlchemy needs to see
every table: Alembic's env.py, and app.main before the app starts serving.
Without this, models that are never imported directly won't be registered on
Base.metadata and `create_all`/`autogenerate` will silently skip them.
"""

from app.domains.users.models import User  # noqa: F401
from app.domains.pets.models import Pet  # noqa: F401
from app.domains.reports.models import Report  # noqa: F401
from app.domains.sightings.models import Sighting  # noqa: F401
from app.domains.notifications.models import Notification, NotificationPreference  # noqa: F401
from app.domains.caregivers.models import Caregiver, CaregiverRating  # noqa: F401
from app.domains.search.models import ImageSearch  # noqa: F401
from app.domains.catalog.models import CatalogListing  # noqa: F401
