# Header Module

## Purpose

Top navigation bar for the one-page scroll layout. Sticky/fixed positioning, black background, navigation links to all slides.

## Specification

### HTML Structure

```html
<header class="header" x-data="{ isScrolled: false }" @scroll="isScrolled = window.scrollY > 50">
  <div class="header-content">
    <!-- Logo (clickable to slide 1) -->
    <button class="header-logo" @click="scrollToSlide(1)">DJ_Visit</button>
    
    <!-- Navigation -->
    <nav class="header-nav">
      <button class="nav-link" @click="scrollToSlide(1)">Главная</button>
      <button class="nav-link" @click="scrollToSlide(2)">Почему я?</button>
      <!-- Logo centered -->
      <button class="nav-link" @click="scrollToSlide(3)">Портфолио</button>
      <button class="nav-link" @click="scrollToSlide(7)">Связь со мной</button>
    </nav>
  </div>
</header>
```

### Styling

- **Position:** `position: sticky` or `position: fixed` (TBD in CSS review)
- **Background:** Black `#000000`
- **Height:** ~80px
- **Layout:** Flexbox, centered content
- **Logo:** Centered, clickable
- **Navigation:** Flex row, evenly spaced
- **Text color:** White `#FFFFFF`
- **Hover:** Subtle color change (orange tint or opacity)

### CSS Variables Used

```css
--color-black: #000000;
--color-white: #FFFFFF;
--color-primary-orange: #[TBD from Figma];
--header-height: 80px;
--font-family-sans: [TBD from Figma];
```

### Interactivity

- Buttons trigger scroll to corresponding slide
- Alpine.js: `scrollToSlide(slideNumber)` function
- Scroll tracking: highlight active nav link (TBD for Phase 2)

## Assets

- Logo image (if not text): `/app/static/img/logo.png`

## Status

- Phase 1: Static layout (no scroll tracking yet)
- Phase 3: Add active link highlighting + scroll spy
