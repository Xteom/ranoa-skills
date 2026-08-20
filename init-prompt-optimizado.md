# /init — Prompt optimizado para Claude Code

> Pega esto como instrucción del comando `/init` (o como primer mensaje de la sesión de planeación).
> Presupone que el agente tiene acceso al repo y a los documentos de diseño.

---

## MISIÓN

Esto va a crecer. Tu entregable no es "un archivo", es un **sistema de documentación de planeación** (en adelante, **el Plan**) que vive bajo `docs/` y que escala con el proyecto.

**El diseño de ese sistema es TUYO.** No lo decidas en frío: primero **investiga** (este repo, el handoff, los repos hermanos — cómo organizan ellos sus docs), y con eso **piensa y decide la mejor forma de ordenar todo e iterar sobre ello**. Usa superpowers para diseñarlo y pasa el diseño por un **agente adversarial** antes de fijarlo: ¿un agente fresco de verdad puede retomar con esto? ¿escala o se vuelve un archivo monstruo? ¿dónde se va a pudrir?

Lo único fijo es el contrato de entrada:

- **`PLAN.md` en la raíz de `docs/` es el punto de entrada estable.** Todo agente fresco empieza ahí, siempre. Puede ser el documento completo hoy y un índice mañana — eso lo decides tú y lo puedes reestructurar cuando el crecimiento lo pida, **siempre que el punto de entrada no cambie y nada de información se pierda**.

El Plan NO es el código ni el diseño detallado: es la guía general que cualquier agente nuevo, **sin ningún contexto previo**, puede leer para saber:

1. Qué leer (y en qué orden, lo mínimo necesario).
2. Cómo empezar, avanzar y modificar cosas.
3. Qué ya se avanzó, qué falló, qué se aprendió.
4. Cuál es el siguiente subgoal y sus criterios de aceptación.

Lo particular se decide al momento de escribir código; el Plan se mantiene **general**.

---

## FUENTES DE VERDAD (autoridad por dominio, no ranking)

Ninguna fuente manda sobre todo. Cada una es la autoridad **en su dominio**, y en el dominio de otra no compite:

| Fuente | Autoridad sobre |
|---|---|
| **`docs/cliente/drp-backend-handoff-v2.pdf`** | El **QUÉ**: contrato con el cliente, tablas de lectura que inicializan todo, spec/JSON que triggerea el batch job, resultados esperados. |
| **`core/`** | El **CÓMO actual**: implementación vigente, lógica del DRP tal como existe hoy. |
| **Repos hermanos** — `/home/uumami/dds/mentat_forecasting_engine` y `/home/uumami/dds/cloudcore-backend` | Las **CONVENCIONES**: patterns, CI/CD, estructura de branches, tests y carpetas. |
| **`legacy/`** | **Nada.** Solo referencia histórica; nunca fuente de verdad. |

**Regla de conflicto:**
- Choque **entre dominios** → gana la autoridad de ese dominio (ej.: si core/ contradice al handoff sobre el spec del trigger, gana el handoff; si el handoff sugiere una estructura de código rara, ganan las convenciones de los repos hermanos).
- Choque **dentro del mismo dominio** o caso no cubierto → anótalo en "Inconsistencias" del Plan con tu resolución propuesta, decide con el criterio general, y **sigue adelante sin detenerte**.

⚠️ **Los documentos tienen errores y bias.** Para decidir, razona en general: ¿cómo afecta la usabilidad? ¿cuál es la mejor práctica de ingeniería? Busca:

- **Consistencia interna**: lógica y prácticas correctas.
- **Consistencia externa**: uso correcto desde el punto de vista del usuario/consumidor.

---

## ALCANCE

**Frontera del sistema: nuestro dominio empieza en el momento en que el job se triggerea (trigger incluido) y termina en los resultados finales listos para consumirse.**

**Nosotros construimos (del trigger — inclusive — al final):**
- La recepción y manejo del trigger y del spec/JSON del job.
- La lógica del DRP.
- La lambda de actualización.
- Las tablas **intermedias** y **finales** (resultados listos para consumirse).
- El foco es: **tablas + lógica**.

**NO construimos (vive fuera, lo hace otro equipo):**
- Las **tablas de lectura** que inicializan todo.
- El **mecanismo que dispara el batch job** (el trigger inicial del DRP). Nosotros lo *recibimos* y procesamos; no lo generamos.

Para desarrollo, simula ambos de forma **súper sencilla**: un sample de datos que imite las tablas de lectura y un trigger/spec de ejemplo, sin romper nada. El formato de ambos sale del handoff, no lo inventes.

---

## RESTRICCIONES DURAS (no negociables)

| Regla | Detalle |
|---|---|
| **Ambientes** | Existen `prod`, `staging`, `dev`. Por ahora **todo en `dev`**: branch a dev, deploy solo a dev. Sigue los patrones de release branches de los repos hermanos. |
| **AWS (allowlist)** | Credenciales en `uumami_accessKeys.csv` (repo mentat_forecasting_engine). **Nunca copies las llaves a ningún archivo; solo referencia la ruta.** En AWS solo puedes hacer UNA cosa: **crear/actualizar nuestras tablas y lambdas en `dev`**, bien definidas y bajo una **allowlist de nombres/prefijos que el Plan declara explícitamente**. Todo recurso que no esté en la allowlist está prohibido — sin excepciones ni interpretación. |
| **Local (contenedor)** | **Libertad total.** Corre, rompe, borra, experimenta lo que necesites dentro del contenedor. El límite duro es solo hacia AWS. |
| **Contenedores** | Todo con **docker/podman**. Nada de instalar dependencias local. |
| **No hardcodear** | Nada de valores mágicos. Todo parámetro se pasa **explícito**. Evita defaults implícitos: si hay un default, que se pase explícito. |
| **Simplicidad** | Mínimo necesario pero correcto y útil e2e. Si dudas entre simple y complejo, elige simple. General > particular: debe sobrevivir modificaciones futuras. |
| **Higiene de branches** | Ver sección "GIT: flujo para agentes". Feature pequeña → CI verde → merge → borrar branch → re-branchear de dev. |

---

## ESTRATEGIA: WALKING SKELETON PRIMERO

1. **Fase 0 — Esqueleto e2e**: solo fierro y piping. El flujo completo del DRP corre de inicio a fin con datos de ejemplo, aunque la lógica sea trivial. Objetivo: asegurar que todo conecta y **se puede probar**.
2. **Fases siguientes**: reemplazar lógica trivial por lógica real, **poco a poco**, feature por feature. Cada feature es pequeña pero útil, pensada desde el punto de vista del usuario y del sistema.

---

## TESTING (útil, no exagerado)

- **Prioridad #1: e2e** — diseñados para replicar el flujo completo del DRP de inicio a fin, incluyendo modificaciones. Varios e2e cubriendo **diferentes edge cases**.
- **Integration y unit tests**: los mínimos que prueben que la lógica se comporta como se espera, con foco en **edge cases**, no en cobertura por cobertura.
- **Flujo**: testear local (unit + integration + e2e en contenedor) → push → CI/CD con tests útiles, sobre todo e2e.
- Todo ordenado en carpetas correctas siguiendo los patrones de los repos hermanos.

---

## GIT: FLUJO PARA AGENTES

**Base: GitHub flow corto**, igual que los repos hermanos. Es el flujo correcto para este caso: un agente, features pequeñas, merges frecuentes. No lo compliques.

```
dev ──► branch por subgoal ──► commits checkpoint ──► PR ──► CI verde ──► merge ──► borrar branch ──► re-branchear de dev
```

Adaptaciones agénticas:

- **Commits checkpoint pequeños y frecuentes.** Si el run nocturno muere a medias, el siguiente agente recupera desde el último checkpoint en vez de rehacer todo. Mensaje de commit = qué paso del loop completó.
- **Un branch = un subgoal.** Nunca mezcles subgoals en un branch.
- **Branches anidadas (stacking) solo cuando estén justificadas**: si el subgoal N+1 depende de código de N que aún no mergea (CI pendiente), branchea N+1 **encima** de N para no quedarte esperando; cuando N mergee a dev, rebasea N+1 sobre dev. **Máximo 2 niveles de stack** — más profundo es complejidad que este proyecto no necesita. Si los subgoals son independientes, no stackees: branchea de dev.
- **Nunca force-push a dev.** Force-push solo a tus propias branches del stack después de un rebase.
- **Auto-merge**: CI verde = merge, **sin aprobación humana**. Nadie va a revisar hasta mañana; un PR esperando es un PR muerto.
- **CI rojo no te detiene**: itera hasta lograrlo. Sin límite de intentos, pero **parsimonioso**: cada reintento con una hipótesis NUEVA — si vas a repetir lo mismo, detente y piensa primero. Si te quedas sin hipótesis, **parquea** el subgoal (`blocked` con diagnóstico en el Plan), avanza con otro, y **regresa más tarde en la noche con un subagente fresco** — ojos nuevos sobre un problema parqueado valen más que el intento 15 del mismo contexto.
- Worktrees solo si algún día corren agentes en paralelo; hoy no aplica.

---

## LOOP AUTÓNOMO POR SUBGOAL

**Tienes subagentes disponibles. Úsalos libremente y sin pedir permiso** — para implementar, revisar, investigar, lo que el paso pida.

**Un subgoal = un subagente con CONTEXTO FRESCO.** Esto es mecanismo, no metáfora: cada subgoal arranca en un subagente/sesión nueva que lee solo su brief. Beneficio doble: cero context-rot, y valida el Plan en cada iteración — si el agente fresco no puede retomar, el Plan falló y lo detectas temprano.

**Superpowers en cada paso** (brainstorm → plan → implementación por fases) y **agentes adversariales entre pasos** — no solo al final. El adversario es también un **subagente de contexto fresco**: lee solo el diff + el criterio de aceptación + la parte relevante del handoff (no hereda el razonamiento del implementador), y tiene **obligación de veredicto**: o encuentra problemas concretos, o declara explícitamente qué verificó y por qué pasa. "Se ve bien" no es un veredicto. Si encuentra algo, se corrige antes de avanzar. Ataca: lógica, edge cases, consistencia con handoff y patterns, hardcodeo — y el propio Plan cuando se modifica.

Para **cada subgoal**, ejecuta este ciclo:

```
1. BRIEF      → Subagente fresco lee docs/PLAN.md: estado, lecciones, su
               subgoal. Lee SOLO lo que el subgoal lista (anti context-rot).
               ANTES de tocar código, escribe la intención en el Plan
               (write-ahead): "in-progress: intentando X, plan Y". Si el run
               muere a medias, el siguiente agente sabe qué se intentaba.
2. PLANEA     → Superpowers: pasos pequeños, criterio de aceptación
               verificable (comando + resultado esperado). Adversario
               revisa el plan del subgoal. Los tests/criterios se fijan
               AQUÍ, antes de implementar — no después.
3. EJECUTA    → Implementa lo mínimo necesario. Explícito, sin hardcodeo.
4. ADVERSARIO → Pasada adversarial (subagente fresco, con veredicto).
5. TESTEA     → Unit + integration + e2e en contenedor. Si tocaste algo
               viejo, re-testea. Modificar un test existente exige
               justificación en el log de decisiones — el test no se
               "arregla" para que pase.
6. LIMPIA     → Refactor parsimonioso antes de cerrar: borra código muerto,
               helpers huérfanos, samples temporales, TODOs sin dueño,
               ramas de lógica que ya no se usan. Nada queda volando.
               Deja el campamento más limpio de como lo encontraste.
7. REFLEXIONA → (parsimonioso, 3-6 líneas) ¿Qué aprendí? ¿Qué me sorprendió?
               ¿Qué cambió y cómo se propaga? Anótalo en el Plan donde el
               SIGUIENTE subgoal lo verifique antes de empezar.
8. ACTUALIZA  → `done` SOLO con evidencia ejecutada EN ESTA SESIÓN: el
               comando de verificación corrió y su resultado queda
               referenciado en el Plan. Sin evidencia, no hay done.
               Actualiza estado/decisiones/problemas; reestructura el Plan
               si hace falta (con adversario). Merge y limpia branch.
```

---

## MODO NOCTURNO: AUTONOMÍA TOTAL POR DEFECTO

Este flujo corre **de noche, sin revisión paso a paso**. La regla operativa es:

> **Decide → documenta → continúa.** Detenerse es la excepción, no una opción cómoda.

**No hay revisión humana en ningún punto del run.** No pidas permiso, no dejes preguntas abiertas "para confirmar", no pauses esperando aprobación. Tienes subagentes: úsalos sin preguntar. Localmente (contenedor) puedes hacer lo que sea.

**Ante cualquier ambigüedad:** elige la opción más **simple y reversible**, anótala en el Log de decisiones como *"supuesto a validar"*, y sigue. Un supuesto documentado y reversible cuesta minutos corregirlo mañana; una noche detenida cuesta la noche entera.

**NUNCA te detengas por** (resuélvelo tú):
- Estilo, naming, estructura de carpetas, alcance de tests → convenciones de los repos hermanos.
- Dudas del handoff con una interpretación razonable → interpreta, anota en Inconsistencias, sigue.
- Tests que fallan o CI rojo → itera hasta lograrlo, con hipótesis nueva en cada intento; sin hipótesis nueva, parquea y regresa después con subagente fresco.
- Elegir entre dos opciones técnicas viables → la más simple y reversible.
- Falta de información deducible leyendo más código/docs → léelos.

**Detente SOLO si** (lista cerrada, todo lo demás NO califica):
1. **Seguridad**: exponer credenciales/secretos, cambiar permisos, o cualquier operación destructiva o fuera de `dev`.
2. **Fuera de alcance/allowlist**: tocar recursos AWS fuera de la allowlist, crear las tablas de lectura, o construir el mecanismo del trigger inicial (eso vive fuera).
3. **Irreversible + indecidible**: decisión que no se puede revertir, cuyo error costaría más que esperar una noche, **y** cuya respuesta no es deducible de ninguna fuente de verdad.

**Si te detienes por un bloqueo:** no mueras ahí. Deja en el Plan el estado exacto (qué bloqueó, opciones evaluadas, tu recomendación), marca el subgoal como `blocked`, y **continúa con el siguiente subgoal no bloqueado**. La noche solo termina cuando no queda ningún subgoal ejecutable — y antes de terminar, **regresa una vez a los subgoals parqueados** con subagente fresco.

**Cierre de sesión — reporte matutino (obligatorio, siempre, incluso si el run murió a medias):**
Lo último que el run escribe es un reporte corto en el Plan: qué mergió, qué quedó `blocked` y por qué, decisiones tomadas y supuestos a validar, refactors/limpiezas hechas, tests nuevos, y qué recomienda atacar en la siguiente sesión. Es lo primero que se lee en la mañana; sin él, auditar el run cuesta más que haberlo supervisado.

---

## EL PLAN: PROPIEDADES OBLIGATORIAS, ESTRUCTURA LIBRE

No te impongo un layout de archivos: **tú decides la estructura después de investigar**, y la reestructuras cuando crezca (dividir en varios archivos bajo `docs/`, crear índices, lo que el proyecto pida). Lo que sí es obligatorio son las **propiedades** — esto sí es best practice segura y no se negocia:

1. **Onboarding frío**: un agente con memoria completamente fresca lee `docs/PLAN.md` y en pocos minutos sabe qué es el sistema, qué leer (y qué NO leer), dónde va el proyecto y cuál es el siguiente subgoal ejecutable.
2. **Anti context-rot**: archivos cortos, **punteros a fuentes en vez de copias**, nada de resúmenes largos que se desactualizan. Si un archivo del Plan crece hasta ser costoso de leer completo, divídelo — eso es señal, no opción.
3. **Estado verificable**: cada subgoal tiene objetivo (1-2 líneas, general), qué leer antes de empezar, criterio de aceptación verificable (qué tests pasan), y estado `pending | in-progress | done | blocked`.
4. **Memoria del sistema**: en algún lugar del Plan viven — y un agente fresco los encuentra desde el punto de entrada —:
   - Log de decisiones (fecha, decisión, por qué, alternativa descartada — una línea c/u; incluye los *"supuestos a validar"* del modo nocturno).
   - Lecciones y sorpresas (append-only, parsimonioso: qué cambió, cómo se propaga, qué verificar en el siguiente subgoal).
   - Inconsistencias encontradas en los docs (fuente, descripción, resolución propuesta, estado).
   - Problemas abiertos / bloqueos.
   - Mapa de lectura: rutas al handoff, core/, repos hermanos, y la ruta (solo la ruta) de las credenciales AWS.
5. **Evolución sin pérdida**: reestructurar el Plan está permitido y esperado, pero es un cambio como cualquier otro — pasa por revisión adversarial, no pierde información, y el punto de entrada sigue siendo `docs/PLAN.md`.

Cuando dudes entre estructurar más o menos: pregúntate qué necesita leer el **siguiente agente fresco** para su subgoal, y optimiza para eso. El Plan existe para ese lector, no para verse completo.

---

## RECORDATORIOS FINALES

- Iterar **poco a poco**: features pequeñas pero útiles.
- El spec/JSON que triggerea el job y lo que va en cada tabla salen del handoff — no inventes, no hardcodees, pasa todo explícito.
- Si algo de lógica falta en los docs, está bien: mantén el mínimo necesario pero un sistema **correcto, útil y probado e2e**.
- Después de cada subgoal (y de cada etapa si hace falta) reflexiona de manera parsimoniosa y persiste la reflexión donde el siguiente agente la verifique.
