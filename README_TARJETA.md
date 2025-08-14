# Tarjeta de cumpleaños - Collage + Carta (PDF)

Coloca tus fotos en `/workspace/imagenes/` (1 a 6 imágenes, formatos: JPG/PNG/WEBP). Luego ejecuta:

```bash
python3 /workspace/generar_tarjeta.py
```

Se generará:
- `/workspace/salidas/tarjeta_cumple_abu_orieta.pdf` (2 páginas A4, lista para imprimir)
- `/workspace/salidas/preview_collage.jpg` (vista previa de la portada)

Personalizar:
- Edita el texto del título cambiando `CARD_TITLE` dentro de `generar_tarjeta.py`.
- Para personalizar la carta, modifica la función `default_letter()` en el mismo archivo o pásame el texto y lo actualizo por ti.