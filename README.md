# Quantum Oracle Dice V3 — Android

Prototipo Android sin sensor de movimiento.

## Funciones
- Dos dados procedurales pseudo-3D, sin sprites.
- Animación de lanzamiento y rotación.
- Destellos ambientales suaves, sin estroboscopio.
- Modos JUSTO, CAOS y ORACULO.
- Visualización conceptual tipo Bloch para dos qubits.
- Historial local en JSON.
- No solicita sensores, ubicación, micrófono ni Bluetooth.

## Importante sobre el modelo cuántico
El mapeo de dos dados de seis caras a dos qubits es una abstracción de juego.
No representa literalmente un dado físico como un qubit ni afirma que el resultado
sea una medición cuántica de hardware.

## Compilación

Para prueba:
    buildozer android debug

Para APK firmado de distribución:
    buildozer android release

Para Google Play:
    buildozer android release
y subir el AAB generado en bin/ a Play Console.

Google Play requiere AAB para apps nuevas y, desde el 31-08-2026,
las nuevas apps deben apuntar a Android 16 / API 36 o superior.

## Antes de publicar
1. Cambiar package.domain/package.name por el identificador definitivo.
2. Crear una clave de firma propia y guardarla fuera del repositorio.
3. Añadir icono y recursos gráficos de marca definitivos.
4. Probar en varios tamaños de pantalla y Android.
5. Completar ficha de Play Console, privacidad, clasificación de contenido,
   datos de seguridad y demás declaraciones que correspondan.
6. Crear una versión interna/cerrada antes de producción.
