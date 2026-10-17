# Explicación para el público no técnico (≤ 120 palabras)

> Destinatario: representante de la Municipalidad / presidente de la asociación de recicladores.
> Fuente: vista de contexto (`img/structurizr-Contexto.png`). Versión revisada por el equipo.

```text
EcoRecicla AQP es una aplicación para que los vecinos de Arequipa pidan que recojan sus residuos reciclables en casa. El vecino indica el material, su dirección y una franja horaria; el sistema asigna a un reciclador formalizado de su distrito, que recorre su ruta del día desde el celular, pesa el material y lo registra aunque no tenga señal. Con cada pesaje el vecino acumula puntos que puede canjear por beneficios municipales. La municipalidad administra los distritos y ve cuántas toneladas se recogen. Para avisar a vecinos y recicladores, el sistema usa un servicio de notificaciones; para los canjes, el sistema de incentivos municipales. Si una conexión falla, el registro se guarda y se reintenta.
```

**Palabras:** 115.

## Verificación de cada afirmación contra el modelo

| Afirmación | Respaldo en el modelo |
|---|---|
| El vecino indica material, dirección y franja; el sistema asigna un reciclador de su distrito | HU-03 (`docs/design/historia.md`); vista dinámica pasos 1–4; `ServicioRutas.asignar` filtra por distrito |
| El reciclador usa su ruta del día desde el celular y registra sin señal | Contenedor `PWA del reciclador` (Service Worker, cola local); RF-02, RF-03; QA-02 y fiabilidad |
| Con cada pesaje el vecino acumula puntos canjeables por beneficios | Componente `Módulo Puntos`; sistema externo `Sistema de incentivos municipales` (RF-04) |
| La municipalidad administra distritos y ve toneladas | Persona `Administrador municipal`; módulos `Distritos` y `Reportes` (RF-05, RF-06) |
| Avisos mediante un servicio de notificaciones | Sistema externo `Servicio de notificaciones` |
| Si una conexión falla, el registro se guarda y se reintenta | PWA guarda en el celular; `Worker de tareas` (Celery) con reintentos |

## Criterios aplicados al redactarla

- Sin jerga: se evitó "API", "PWA", "cola" y "contenedor"; se habla de "aplicación", "celular" y "servicio".
- Solo lo que existe en el modelo: EcoRecicla **no cobra** (acredita puntos), por lo que no se menciona ningún medio de pago.
- Longitud verificada con un conteo de palabras (115, por debajo del máximo de 120).
