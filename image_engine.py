"""
image_engine.py - The Backend
This module executes all imaging operations leveraging the Pillow library. It isolates
mathematical operations (coordinate clamping, scaling, alpha manipulation) from
the application's graphical state management.
"""

import os
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageColor


class ImageEngine:
    def __init__(self):
        self.cached_image_watermark = None

    def cache_image_watermark(self, state):
        """Pre-processes the watermark image once, handling Pillow version differences safely."""
        if not state["watermark_path"] or not os.path.exists(state["watermark_path"]):
            self.cached_image_watermark = None
            return

        try:
            wm = Image.open(state["watermark_path"]).convert("RGBA")
            scale = max(1, state["scale"]) / 100.0
            new_w = max(1, round(wm.size[0] * scale))
            new_h = max(1, round(wm.size[1] * scale))

            # Cross-compatible: Works on both Pillow v8 (older Linux) and v9+
            resample_filter = getattr(Image, 'Resampling', Image).LANCZOS
            self.cached_image_watermark = wm.resize((new_w, new_h), resample_filter)
        except Exception as e:
            print(f"Error caching watermark: {e}")
            self.cached_image_watermark = None

    def _create_text_watermark(self, state, base_h):
        """Generates a text-based transparent RGBA image dynamically scaled to the base image height."""
        text = state["text_input"]
        raw_align = state.get("text_align", "Center").lower()
        pillow_align = "center" if raw_align == "centre" else raw_align

        # Mathematically links slider value to base image height
        font_size = max(12, int(base_h * (state["scale"] / 200.0)))
        font = None

        # Ensure a scalable TrueType font is loaded (avoiding the tiny unscalable bitmap default)
        font_candidates = [
            state.get("font_path", ""),
            "DejaVuSans.ttf",
            "LiberationSans-Regular.ttf",
            "Ubuntu-R.ttf",
            "arial.ttf"
        ]

        for candidate in font_candidates:
            if candidate and os.path.exists(candidate):
                try:
                    font = ImageFont.truetype(candidate, font_size)
                    break
                except (IOError, OSError):
                    continue

        if not font:
            try:
                # Load default system TTF rather than unscalable bitmap
                font = ImageFont.load_default(size=font_size)
            except TypeError:
                font = ImageFont.load_default()

        # Measure text boundaries cleanly using multiline_textbbox
        dummy_img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        draw = ImageDraw.Draw(dummy_img)
        bbox = draw.multiline_textbbox((0, 0), text, font=font, align=pillow_align)

        # Calculate bounding dimensions and compensate for glyph padding
        left, top, right, bottom = bbox
        text_w = round(max(1, right - left))
        text_h = round(max(1, bottom - top))

        alpha_val = round(((100 - state["transparency"]) / 100.0) * 255)
        r, g, b = ImageColor.getrgb(state["color"])

        # Render full multi-line block onto transparent RGBA surface
        text_img = Image.new("RGBA", (text_w, text_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_img)
        draw.multiline_text((-left, -top), text, font=font, fill=(r, g, b, alpha_val), align=pillow_align)

        return text_img

    def _prepare_watermark(self, state, base_h):
        """Routes execution to either generate dynamic text or apply alpha transforms to cached images."""
        if state["mode"] == "Text":
            if not state["text_input"]:
                return None
            return self._create_text_watermark(state, base_h)

        elif state["mode"] == "Image":
            wm = self.cached_image_watermark
            if wm:
                # Creates a shallow copy to prevent permanently altering the cached original
                wm_copy = wm.copy()

                # Extracts the alpha channel, maps new opacity percentages, and reinserts it
                alpha = wm_copy.getchannel('A')
                alpha = alpha.point(lambda p: round(p * ((100 - state["transparency"]) / 100.0)))
                wm_copy.putalpha(alpha)
                return wm_copy
        return None

    def _calculate_position(self, base_w, base_h, wm_w, wm_h, position_string, padding):
        """Calculates absolute pixel positioning coordinates and enforces bounding box constraints."""
        center_x = round((base_w - wm_w) / 2)
        center_y = round((base_h - wm_h) / 2)
        right_x = base_w - wm_w
        bottom_y = base_h - wm_h

        match position_string:
            case "Top-Left":
                raw_x, raw_y = padding, padding
            case "Top-Center":
                raw_x, raw_y = center_x, padding
            case "Top-Right":
                raw_x, raw_y = right_x - padding, padding
            case "Center-Left":
                raw_x, raw_y = padding, center_y
            case "Center":
                raw_x, raw_y = center_x, center_y
            case "Center-Right":
                raw_x, raw_y = right_x - padding, center_y
            case "Bottom-Left":
                raw_x, raw_y = padding, bottom_y - padding
            case "Bottom-Center":
                raw_x, raw_y = center_x, bottom_y - padding
            case "Bottom-Right":
                raw_x, raw_y = right_x - padding, bottom_y - padding
            case _:
                raw_x, raw_y = 0, 0

        # Mathematical clamping ensures coordinates cannot exceed dimensions (0 to max safe edge)
        final_x = max(0, min(raw_x, right_x))
        final_y = max(0, min(raw_y, bottom_y))

        return (final_x, final_y)

    def _apply_watermark(self, base_img, state):
        """Overlays the prepared RGBA watermark onto the base image respecting alpha constraints."""
        base_w, base_h = base_img.size
        watermark = self._prepare_watermark(state, base_h)

        if not watermark:
            return base_img

        final_x, final_y = self._calculate_position(
            base_w, base_h, watermark.size[0], watermark.size[1],
            state["position"], state["padding"]
        )

        base_img.paste(im=watermark, box=(final_x, final_y), mask=watermark)
        return base_img

    def generate_preview(self, state, canvas_w, canvas_h):
        """Downsamples the fully rendered image to fit UI dimensions without saving."""
        if not state["base_images"]:
            return None

        try:
            base_img = Image.open(state["base_images"][0]).convert("RGBA")
            watermarked_img = self._apply_watermark(base_img, state)

            preview_img = ImageOps.contain(watermarked_img, (canvas_w, canvas_h))
            return preview_img
        except Exception:
            return None

    def process_and_save_image(self, base_image_path, state, save_dir):
        """Executes full-resolution processing loop and writes standard RGB image to disk safely."""
        try:
            base_img = Image.open(base_image_path).convert("RGBA")
            final_img = self._apply_watermark(base_img, state).convert("RGB")

            _, filename = os.path.split(base_image_path)
            name, ext = os.path.splitext(filename)

            # 1. Define the initial target name
            base_new_name = f"{name}_watermarked"
            new_path = os.path.join(save_dir, f"{base_new_name}{ext}")

            # 2. Check for collisions and increment a counter if necessary
            counter = 1
            while os.path.exists(new_path):
                new_path = os.path.join(save_dir, f"{base_new_name}_{counter}{ext}")
                counter += 1

            # 3. Save safely to the guaranteed unique path
            final_img.save(new_path)

            return {"status": "success", "file": new_path}

        except Exception as e:
            return {"status": "error", "file": base_image_path, "message": str(e)}