from ldclient import LDClient
from ldclient.config import Config
from ldclient.context import Context
from django.conf import settings

client = LDClient(
    Config(
        sdk_key=settings.LD_SDK_KEY,
        send_events=True
    )
)


def is_feature_enabled(flag_key: str, user=None):
    # Crear contexto compatible con tu SDK
    if user is None:
        ld_context = Context.builder("anonymous") \
            .set("kind", "user") \
            .build()
    else:
        ld_context = (
            Context.builder(str(user.id if hasattr(user, "id") else "user-1"))
            .set("kind", "user")
            .set("name", getattr(user, "username", "usuario"))
            .set("email", getattr(user, "email", "no-email"))
            .build()
        )

    # Evaluar flag
    value = client.variation(flag_key, ld_context, False)
    return value