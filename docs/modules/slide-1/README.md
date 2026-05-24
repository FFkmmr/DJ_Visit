# Slide 1: Hero Section (Главная)

## Purpose

Opening/hero slide for the web business card. Features background video, wavy decorative shape, producer info, and animated marquee text.

## Concept (from concept.md)

- **Background:** Video (muted, no sound, loops, lazy-loaded)
- **Wavy shape:** Black animated wave covering ~50% of slide, separates background from content
- **Left side:** Photo + decorative black shape below it (scales together with wave)
- **Right side:** Producer name + title + marquee text "ЧЕЛОВЕК ВАЖНЕЕ ФОРМАТА" (scrolls RTL)
- **Bottom:** Marquee text with services + orange stars "Продакшн ✦ Сценарий ✦ ..." (scrolls)
- **Line elements:** Black outside the wave, white inside the wave

## HTML Structure

```html
<section class="slide slide-1" id="slide-1">
  <!-- Background video (lazy-loaded) -->
  <video 
    class="slide-1-bg-video"
    x-data="{ isVisible: false }"
    @intersectionchange="isVisible = $event.detail"
    :autoplay="isVisible"
    loop
    muted
  >
    <source src="/static/video/slide-1-bg.mp4" type="video/mp4">
  </video>

  <!-- Container for all content -->
  <div class="slide-1-container">
    
    <!-- Wavy shape + Photo section -->
    <div class="slide-1-left">
      <!-- Wavy shape (SVG or PNG) -->
      <div class="slide-1-wave">
        <!-- SVG: viewBox="0 0 600 800" -->
      </div>
      
      <!-- Photo -->
      <img src="/static/img/producer-photo.jpg" alt="Producer" class="slide-1-photo">
      
      <!-- Decorative shape below photo -->
      <div class="slide-1-photo-decor"></div>
    </div>

    <!-- Info section (name + title + marquee) -->
    <div class="slide-1-right">
      <h1 class="slide-1-name">DJ Name</h1>
      <p class="slide-1-title">Music Producer / Director</p>
      
      <!-- Marquee text (right to left) -->
      <div class="marquee marquee-rtl">
        <span>"ЧЕЛОВЕК ВАЖНЕЕ ФОРМАТА"</span>
      </div>
    </div>
  </div>

  <!-- Bottom marquee (services) -->
  <div class="slide-1-bottom">
    <div class="marquee marquee-ltr">
      <span>Продакшн ✦ Сценарий ✦ Креатив ✦ Съёмка ✦ Режиссура ✦ Постпродакшн ✦ Кастинг ✦ Работа с актёром ✦</span>
    </div>
  </div>
</section>
```

## Styling

### Layout

- **Slide height:** Full viewport (`100vh`) + content bottom
- **Container:** Flexbox, row layout (left + right)
- **Left (50%):** Wave + photo (scales together)
- **Right (50%):** Name + title + marquee

### Colors & Typography

- **Background video:** Full-screen, object-fit: cover
- **Wavy shape:** Black `#000000`
- **Photo:** Standard border, fits in wave area
- **Text (right):** White `#FFFFFF`
- **Stars in bottom marquee:** Orange `--color-primary-orange`
- **Marquee text:** Gray (white 50% opacity)

### Animations

- **Marquee (RTL):** `@keyframes marquee-rtl` (infinite scroll, right to left)
- **Marquee (LTR):** `@keyframes marquee-ltr` (infinite scroll, left to right, services)
- **Stars:** Orange color (hardcoded in HTML or replaced via CSS `content`)

## Interactivity

- **Video lazy-load:** Alpine.js Intersection Observer → auto-play when visible
- **Marquee:** Pure CSS animation (no JS needed)

## Assets

- `/static/video/slide-1-bg.mp4` (background video)
- `/static/img/producer-photo.jpg` (producer photo)
- `/static/img/wave-shape.svg` or `.png` (wavy decoration)
- `/static/img/photo-decor.png` (black shape below photo)

## CSS Variables

```css
--color-black: #000000;
--color-white: #FFFFFF;
--color-white-50: rgba(255, 255, 255, 0.5);
--color-primary-orange: #[TBD];
--font-family-heading: [TBD];
--font-family-body: [TBD];
```

## Status

- Phase 1: Static layout (no lazy-load, no marquee animation yet)
- Phase 1b: Add marquee CSS animations
- Phase 2: Add video lazy-loading
- Phase 3: Polish animations, add parallax (optional)

## Open Questions

- Wavy shape: SVG or PNG? (SVG preferred for scaling)
- Video format: MP4 H.264 codec? Target bitrate?
- Producer name/title text: hardcoded or from config?
