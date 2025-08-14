#!/usr/bin/env python3

import os
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

IMAGES_DIR = "/workspace/imagenes"
OUTPUT_DIR = "/workspace/salidas"
LETTER_PATHS = ["/workspace/carta.txt", "/workspace/imagenes/carta.txt"]

PAGE_W_PT, PAGE_H_PT = A4  # 595 x 842 pt aprox
DPI = 300
# Convert points (1/72 inch) to pixels at 300 DPI for PIL composites
PT_TO_PX = DPI / 72.0

CARD_TITLE = "Feliz cumpleaños, Abu Orieta"


def ensure_dirs() -> None:
	os.makedirs(IMAGES_DIR, exist_ok=True)
	os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_images(max_count: int = 6) -> List[Image.Image]:
	paths = []
	for name in sorted(os.listdir(IMAGES_DIR)):
		if name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
			paths.append(os.path.join(IMAGES_DIR, name))
		if len(paths) >= max_count:
			break
	images: List[Image.Image] = []
	for p in paths:
		img = Image.open(p).convert("RGB")
		images.append(img)
	return images


def draw_decorations(draw: ImageDraw.ImageDraw, canvas_size: Tuple[int, int]) -> None:
	w, h = canvas_size
	# Simple hearts
	heart_color = (233, 64, 102)
	for cx, cy, s in [
		(w * 0.08, h * 0.86, 36),
		(w * 0.16, h * 0.9, 28),
		(w * 0.9, h * 0.86, 32),
		(w * 0.82, h * 0.9, 26),
	]:
		cx = int(cx)
		cy = int(cy)
		s = int(s)
		# Heart using two circles and a triangle-like bottom
		draw.pieslice((cx - s, cy - s, cx, cy), 0, 360, fill=heart_color)
		draw.pieslice((cx, cy - s, cx + s, cy), 0, 360, fill=heart_color)
		draw.polygon([(cx - s, cy), (cx + s, cy), (cx, cy + int(1.3 * s))], fill=heart_color)

	# Balloons (simple circles with strings)
	balloon_color = (80, 153, 255)
	for cx, cy, r in [
		(w * 0.2, h * 0.15, 32),
		(w * 0.8, h * 0.18, 28),
		(w * 0.65, h * 0.14, 24),
	]:
		cx = int(cx)
		cy = int(cy)
		r = int(r)
		draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=balloon_color, outline=(30, 96, 197), width=3)
		draw.line((cx, cy + r, cx - 8, cy + r + 45), fill=(60, 60, 60), width=2)



def build_collage_page(images: List[Image.Image]) -> Image.Image:
	# Create an A4 canvas in pixels
	canvas_w = int(PAGE_W_PT * PT_TO_PX)
	canvas_h = int(PAGE_H_PT * PT_TO_PX)
	bg = Image.new("RGB", (canvas_w, canvas_h), (250, 248, 246))
	draw = ImageDraw.Draw(bg)

	# Grid for up to 4 images (2x2). If more than 4, last row will scroll.
	margin = int(36 * PT_TO_PX)
	gap = int(14 * PT_TO_PX)
	usable_w = canvas_w - margin * 2
	usable_h = canvas_h - margin * 2 - int(120 * PT_TO_PX)  # leave space for title

	cols = 2
	rows = 2 if len(images) <= 4 else 3
	cell_w = (usable_w - (cols - 1) * gap) // cols
	cell_h = (usable_h - (rows - 1) * gap) // rows

	def fit_into(img: Image.Image, w: int, h: int) -> Image.Image:
		img_w, img_h = img.size
		ratio = min(w / img_w, h / img_h)
		new_size = (max(1, int(img_w * ratio)), max(1, int(img_h * ratio)))
		return img.resize(new_size, Image.LANCZOS)

	# Paste images
	idx = 0
	for r in range(rows):
		for c in range(cols):
			if idx >= len(images):
				break
			thumb = fit_into(images[idx], cell_w, cell_h)
			# center inside cell
			x = margin + c * (cell_w + gap) + (cell_w - thumb.width) // 2
			y = margin + r * (cell_h + gap) + (cell_h - thumb.height) // 2
			bg.paste(thumb, (x, y))
			idx += 1

	# Title text area at bottom
	title_y = canvas_h - margin - int(70 * PT_TO_PX)
	# Use a common font fallback
	try:
		font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
		font = ImageFont.truetype(font_path, size=int(40 * PT_TO_PX))
	except Exception:
		font = ImageFont.load_default()

	draw.rectangle((margin, title_y - int(20 * PT_TO_PX), canvas_w - margin, title_y + int(70 * PT_TO_PX)), fill=(255, 255, 255))
	w_text, h_text = draw.textsize(CARD_TITLE, font=font)
	draw.text(((canvas_w - w_text) // 2, title_y), CARD_TITLE, fill=(33, 33, 33), font=font)

	# Decorations around
	draw_decorations(draw, (canvas_w, canvas_h))

	return bg


def export_pdf(collage_img: Image.Image, letter_text: str, out_path: str) -> None:
	c = canvas.Canvas(out_path, pagesize=A4)
	# Page 1: collage
	collage_reader = ImageReader(collage_img)
	c.drawImage(collage_reader, 0, 0, width=PAGE_W_PT, height=PAGE_H_PT)
	c.showPage()
	# Page 2: letter
	c.setFillColorRGB(0.13, 0.13, 0.13)
	c.setFont("Helvetica", 20)
	c.drawCentredString(PAGE_W_PT / 2, PAGE_H_PT - 72, "Carta para Abu Orieta")
	c.setFont("Times-Roman", 14)

	left = 54
	right = PAGE_W_PT - 54
	top = PAGE_H_PT - 120
	line_height = 20

	# simple word wrap
	words = letter_text.split()
	line = ""
	cursor_y = top
	for word in words:
		candidate = (line + " " + word).strip()
		if c.stringWidth(candidate, "Times-Roman", 14) <= (right - left):
			line = candidate
		else:
			c.drawString(left, cursor_y, line)
			cursor_y -= line_height
			line = word
	if line:
		c.drawString(left, cursor_y, line)

	c.showPage()
	c.save()


def default_letter() -> str:
	return (
		"Querida Abu Orieta,\n\n"
		"Gracias por tu amor infinito, tus abrazos y tus risas. "
		"Hoy celebramos tu vida y todo lo hermoso que compartes con nosotros. "
		"Te deseamos un día lleno de alegría, salud y muchos momentos felices.\n\n"
		"Con mucho cariño,\nTu familia"
	)


def read_letter_from_file() -> str:
	for path in LETTER_PATHS:
		if os.path.exists(path):
			try:
				with open(path, "r", encoding="utf-8") as fh:
					content = fh.read().strip()
					if content:
						return content
			except Exception:
				pass
	return ""


def main() -> None:
	ensure_dirs()
	images = load_images(max_count=6)
	if not images:
		print(f"No encontré imágenes en {IMAGES_DIR}. Agrega 1 a 6 fotos y vuelve a ejecutar.")
		return
	collage = build_collage_page(images)
	letter = read_letter_from_file() or default_letter()
	out_path = os.path.join(OUTPUT_DIR, "tarjeta_cumple_abu_orieta.pdf")
	export_pdf(collage, letter, out_path)
	collage_path = os.path.join(OUTPUT_DIR, "preview_collage.jpg")
	collage.save(collage_path, quality=95)
	print("Listo: ")
	print(f"- PDF para imprimir: {out_path}")
	print(f"- Previsualización collage: {collage_path}")


if __name__ == "__main__":
	main()