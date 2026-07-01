# Patrones de Diseño Usados en el Proyecto

Este documento explica qué patrones de diseño usamos, en qué archivo están y para qué nos sirvieron.

## 1. Strategy (patrón de comportamiento)

Es el patrón que más usamos. La idea es simple: en vez de un `if/elif` gigante para decidir qué hacer según un caso, se crea una interfaz común y una clase distinta por cada caso. Así, agregar un caso nuevo no obliga a tocar el código que ya funciona.

Lo usamos en 4 lugares:

- **Roles de cuidador** (`domains/caregivers/role_strategies.py`): hay una interfaz `CaregiverRoleStrategy` y tres clases (`SolidarioRoleStrategy`, `ProfesionalRoleStrategy`, `EspecializadoRoleStrategy`) que deciden si un cuidador acepta cierta especie según su rol.
- **Búsqueda por imagen** (`domains/search/intent_handlers.py`): hay un `IntentHandler` y tres clases (`AdoptionIntentHandler`, `SalesIntentHandler`, `LostPetIntentHandler`) que deciden qué se busca según la intención elegida (adopción, venta, verificar pérdida).
- **Comparación de imágenes** (`infrastructure/image_matcher.py`): la interfaz `IImageMatcher` permite cambiar el motor que compara fotos. Hoy usamos `PerceptualHashMatcher` (hashing de imágenes), pero si quisiéramos usar algo más avanzado (una red neuronal, por ejemplo) solo tendríamos que crear otra clase que implemente la misma interfaz.
- **Canales de notificación** (`infrastructure/notification_channels.py`): la interfaz `INotificationChannel` permite mandar notificaciones por distintos medios (por ahora solo existe `ConsoleChannel`, que simula el envío imprimiendo en consola).

## 2. Factory (patrón creacional)

En `domains/caregivers/role_strategies.py` hay una función `get_role_strategy(role_type)` que, dado un rol, devuelve la estrategia correspondiente. Así el resto del código no necesita saber cómo se crean las estrategias, solo pide "dame la del rol X".

También armamos algo parecido a un "punto central de armado" en `core/dependencies.py`: es el único archivo donde se decide qué clase concreta usar en cada caso (por ejemplo, qué motor de comparación de imágenes se inyecta en los handlers de búsqueda). El resto del código nunca crea esos objetos directamente, los recibe ya armados.

## 3. Repository (patrón estructural / arquitectónico)

Cada dominio separa la lógica de negocio del acceso a la base de datos. Por ejemplo, en `domains/reports/` hay:

- `repositories/interfaces.py`: define qué operaciones existen (buscar por id, crear, etc.) sin decir cómo se hacen.
- `repositories/implementations.py`: la clase real que sí usa SQLAlchemy para hablar con Postgres.
- `services.py`: la lógica de negocio, que le pide cosas al repositorio sin preocuparse de si por dentro es SQL, otra base de datos, o lo que sea.

Esto también nos sirvió para poder probar los servicios sin conectarnos a una base de datos real: en los tests (`tests/unit/domains/reports/test_services.py`) usamos un mock en vez del repositorio de verdad.

## 4. Principios SOLID

Además de los patrones puntuales, tratamos de seguir los principios SOLID en general:

- **S (responsabilidad única)**: cada archivo hace una sola cosa — `models.py` es el esquema, `services.py` es la lógica, `routers.py` solo recibe/responde HTTP.
- **O (abierto/cerrado)**: gracias al Strategy, podemos agregar un rol de cuidador, una intención de búsqueda o un canal de notificación nuevo sin modificar el código que ya existe.
- **L (sustitución de Liskov)**: las tres estrategias de rol de cuidador se pueden usar indistintamente porque todas cumplen el mismo contrato (`CaregiverRoleStrategy`).
- **I (segregación de interfaces)**: en reportes separamos `IReportRepository` (crear, actualizar) de `IReportSearchRepository` (buscar/consultar), para que quien solo necesita consultar no dependa de métodos de escritura que no usa.
- **D (inversión de dependencias)**: los servicios reciben sus dependencias por constructor (por ejemplo `ReportService` recibe un repositorio y un dispatcher de alertas), en vez de crearlas ellos mismos. Quién decide qué implementación usar es `core/dependencies.py`.

## 5. Manejo de errores centralizado

No es un patrón de diseño clásico, pero lo mencionamos porque ayuda a mantener el código limpio: definimos una jerarquía de excepciones propias en `shared/exceptions.py` (`NotFoundError`, `ForbiddenError`, etc.) y un solo lugar (`middleware/error_handling.py`) que las convierte en respuestas HTTP. Así cualquier servicio puede simplemente lanzar `raise ForbiddenError(...)` sin preocuparse de cómo se ve la respuesta al usuario.

