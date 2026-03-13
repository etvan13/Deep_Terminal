import os
import pygame
import fitz

# ============================================================
# Viewer tuning knobs (edit here)
# ============================================================

# Zoom behavior
DEFAULT_ZOOM = 1.0
ZOOM_STEP = 1.06          # 1.05–1.08 is the sweet spot for "hold zoom"
ZOOM_HOLD_HZ = 12         # zoom ticks per second when holding +/- (stable feel)
MIN_ZOOM = 0.12           # allow zooming out to see multiple pages
MAX_ZOOM = 6.0

# Pan / scroll behavior
SCROLL_STEP = 18
SCROLL_STEP_FAST = 70
HPAN_STEP = 18
HPAN_STEP_FAST = 70

# Layout
ITEM_SPACING = 22
VISIBILITY_MARGIN = 200

# Rendering / cache
ZOOM_CACHE_ROUND = 3      # cache key rounds zoom to this many decimals

# Font
FONT_NAME = "Consolas"
FONT_SIZE = 18

# ============================================================


class DividerItem:
    def __init__(self, label: str):
        self.label = label

    def height(self, width, zoom, font):
        return 60

    def render(self, width, zoom, font):
        surf = pygame.Surface((width, 60))
        surf.fill((0, 0, 0))
        pygame.draw.line(surf, (180, 180, 180), (20, 30), (width - 20, 30), 2)
        t = font.render(self.label, True, (230, 230, 230))
        surf.blit(t, (24, 10))
        return surf


class PdfPageItem:
    def __init__(self, doc: fitz.Document, doc_name: str, page_index: int):
        self.doc = doc
        self.doc_name = doc_name
        self.page_index = page_index
        page = self.doc.load_page(self.page_index)
        self._w = float(page.rect.width)
        self._h = float(page.rect.height)

    def height(self, width, zoom, font):
        # We render pages to width*zoom, so "width" is the viewport baseline.
        scale = (width * zoom) / max(1.0, self._w)
        return int(self._h * scale)

    def render(self, width, zoom, font):
        scale = (width * zoom) / max(1.0, self._w)
        mat = fitz.Matrix(scale, scale)
        page = self.doc.load_page(self.page_index)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        surf = pygame.image.fromstring(pix.samples, (pix.width, pix.height), "RGB").convert()
        return surf


class ImageItem:
    def __init__(self, path: str):
        self.path = path
        img = pygame.image.load(path)
        self._base = img.convert()
        self._w, self._h = self._base.get_width(), self._base.get_height()

    def height(self, width, zoom, font):
        scale = (width * zoom) / max(1, self._w)
        return int(self._h * scale)

    def render(self, width, zoom, font):
        scale = (width * zoom) / max(1, self._w)
        w = max(1, int(self._w * scale))
        h = max(1, int(self._h * scale))
        return pygame.transform.smoothscale(self._base, (w, h)).convert()


class TextItem:
    def __init__(self, path: str, title: str | None = None, max_chars=200_000):
        self.path = path
        self.title = title or os.path.basename(path)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                self.text = f.read(max_chars)
        except Exception as e:
            self.text = f"[Could not read file: {e}]"

    def _wrap(self, text, chars_per_line):
        lines = []
        for raw in text.splitlines():
            if not raw:
                lines.append("")
                continue
            i = 0
            while i < len(raw):
                lines.append(raw[i:i + chars_per_line])
                i += chars_per_line
        return lines

    def height(self, width, zoom, font):
        # Text is not zoom-scaled (kept readable); zoom only affects PDFs/images.
        char_w = max(1, font.size("M")[0])
        chars_per_line = max(20, int((width - 40) / char_w))
        lines = self._wrap(self.text, chars_per_line)
        line_h = font.get_linesize()
        return 40 + (len(lines) * line_h) + 30

    def render(self, width, zoom, font):
        h = self.height(width, zoom, font)
        surf = pygame.Surface((width, h))
        surf.fill((0, 0, 0))

        title = font.render(self.title, True, (240, 240, 240))
        surf.blit(title, (20, 10))
        pygame.draw.line(surf, (120, 120, 120), (20, 32), (width - 20, 32), 1)

        char_w = max(1, font.size("M")[0])
        chars_per_line = max(20, int((width - 40) / char_w))
        lines = self._wrap(self.text, chars_per_line)

        y = 45
        line_h = font.get_linesize()
        for line in lines:
            t = font.render(line, True, (200, 200, 200))
            surf.blit(t, (20, y))
            y += line_h

        return surf


class ProjectStreamViewer:
    def __init__(self, items, window=(1024, 768), title="Project"):
        self.items = items
        self.window = window
        self.title = title

        # State
        self.zoom = DEFAULT_ZOOM
        self.scroll_y = 0
        self.scroll_x = 0

        self.spacing = ITEM_SPACING

        # Internal layout
        self._cache = {}       # (idx, zoom_round) -> Surface
        self._tops = []
        self._heights = []
        self._total_h = 0
        self.attachments_anchor = None

        # Hold-to-zoom accumulator
        self._zoom_hold_accum = 0.0

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode(self.window, pygame.DOUBLEBUF)
        clock = pygame.time.Clock()
        font = pygame.font.SysFont(FONT_NAME, FONT_SIZE) or pygame.font.SysFont(None, FONT_SIZE)

        self._rebuild_layout(font)

        running = True
        while running:
            dt = clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_ESCAPE):
                        running = False
                    elif event.key == pygame.K_p:
                        self.scroll_y = 0
                        self.scroll_x = 0
                    elif event.key == pygame.K_a and self.attachments_anchor is not None:
                        self.scroll_y = self.attachments_anchor
                    elif event.key == pygame.K_f:
                        self._fit_to_width(font, anchor="center")

            keys = pygame.key.get_pressed()
            fast = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

            # ----------------------------
            # Scroll / pan (arrow keys)
            # ----------------------------
            vstep = SCROLL_STEP_FAST if fast else SCROLL_STEP
            hstep = HPAN_STEP_FAST if fast else HPAN_STEP

            if keys[pygame.K_DOWN]:
                self.scroll_y += vstep
            if keys[pygame.K_UP]:
                self.scroll_y -= vstep
            if keys[pygame.K_RIGHT]:
                self.scroll_x += hstep
            if keys[pygame.K_LEFT]:
                self.scroll_x -= hstep

            # ----------------------------
            # Hold-to-zoom (stable tick rate)
            # ----------------------------
            zoom_in = keys[pygame.K_EQUALS] or keys[pygame.K_PLUS] or keys[pygame.K_KP_PLUS]
            zoom_out = keys[pygame.K_MINUS] or keys[pygame.K_UNDERSCORE] or keys[pygame.K_KP_MINUS]

            if zoom_in or zoom_out:
                self._zoom_hold_accum += dt
                tick = 1.0 / max(1, ZOOM_HOLD_HZ)

                while self._zoom_hold_accum >= tick:
                    self._zoom_hold_accum -= tick

                    mult = (ZOOM_STEP ** (2 if fast else 1))
                    if zoom_out:
                        mult = 1.0 / mult

                    self._set_zoom(self.zoom * mult, font, anchor="center")
            else:
                self._zoom_hold_accum = 0.0

            # ----------------------------
            # Clamp scroll
            # ----------------------------
            self.scroll_y = max(0, min(self.scroll_y, max(0, self._total_h - self.window[1])))
            self.scroll_x = max(0, self.scroll_x)  # max clamp is optional (see note below)

            # ----------------------------
            # Draw
            # ----------------------------
            screen.fill((0, 0, 0))
            self._draw_visible(screen, font)

            pygame.display.set_caption(
                f"{self.title} | zoom {self.zoom:.2f} | arrows pan | +/- zoom | F fit | P top | A attachments | ESC quit"
            )
            pygame.display.flip()

        pygame.quit()

    def _fit_to_width(self, font, anchor="center"):
        # In this viewer, baseline width is the window width; zoom=1.0 corresponds to "fit-to-width".
        self._set_zoom(1.0, font, anchor=anchor)

    def _set_zoom(self, new_zoom, font, anchor="top"):
        new_zoom = max(MIN_ZOOM, min(MAX_ZOOM, new_zoom))
        if abs(new_zoom - self.zoom) < 1e-6:
            return

        # Preserve view center in both axes
        if anchor == "center":
            anchor_y = self.scroll_y + (self.window[1] * 0.5)
            anchor_x = self.scroll_x + (self.window[0] * 0.5)
        else:
            anchor_y = self.scroll_y
            anchor_x = self.scroll_x

        rel_y = 0.0 if self._total_h <= 1 else (anchor_y / self._total_h)

        # X doesn't have a single total width (items vary), so we preserve by scaling scroll_x.
        zoom_ratio = new_zoom / self.zoom
        anchor_x_abs = anchor_x

        self.zoom = new_zoom
        self._cache.clear()
        self._rebuild_layout(font)

        # restore Y anchor
        new_anchor_y = rel_y * self._total_h
        if anchor == "center":
            self.scroll_y = int(new_anchor_y - (self.window[1] * 0.5))
        else:
            self.scroll_y = int(new_anchor_y)

        # restore X anchor
        if anchor == "center":
            new_anchor_x = anchor_x_abs * zoom_ratio
            self.scroll_x = int(new_anchor_x - (self.window[0] * 0.5))
        else:
            self.scroll_x = int(self.scroll_x * zoom_ratio)

        # clamp
        self.scroll_y = max(0, min(self.scroll_y, max(0, self._total_h - self.window[1])))
        self.scroll_x = max(0, self.scroll_x)

    def _rebuild_layout(self, font):
        w = self.window[0]
        self._tops = []
        self._heights = []
        y = 0
        self.attachments_anchor = None

        for it in self.items:
            self._tops.append(y)
            h = it.height(w, self.zoom, font)
            self._heights.append(h)

            if isinstance(it, DividerItem) and it.label.lower().startswith("attachments"):
                self.attachments_anchor = y

            y += h + self.spacing

        self._total_h = y

    def _get_surface(self, idx, it, font):
        key = (idx, round(self.zoom, ZOOM_CACHE_ROUND))
        if key in self._cache:
            return self._cache[key]
        surf = it.render(self.window[0], self.zoom, font)
        self._cache[key] = surf
        return surf

    def _draw_visible(self, screen, font):
        view_top = self.scroll_y
        view_bot = self.scroll_y + self.window[1]
        win_w = self.window[0]

        for i, it in enumerate(self.items):
            top = self._tops[i]
            h = self._heights[i]
            bot = top + h

            if bot < view_top - VISIBILITY_MARGIN:
                continue
            if top > view_bot + VISIBILITY_MARGIN:
                break

            surf = self._get_surface(i, it, font)

            # Horizontal placement:
            # - if narrower, center it, and allow scroll_x to shift around that center
            # - if wider, scroll_x pans the crop window
            if surf.get_width() <= win_w:
                base_x = (win_w - surf.get_width()) // 2
                x = base_x - self.scroll_x
            else:
                x = -self.scroll_x

            screen.blit(surf, (x, top - self.scroll_y))
