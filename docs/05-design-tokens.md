# Design Tokens

## Colors

From Figma design (1920x6093px frame):

```css
:root {
  /* Primary brand color */
  --color-primary-orange: #[TBD from Figma export];
  
  /* Neutral palette */
  --color-black: #000000;
  --color-white: #FFFFFF;
  --color-gray-light: #F5F5F5;
  --color-gray-dark: #1A1A1A;
  
  /* Semantic */
  --color-text-primary: var(--color-white);
  --color-text-secondary: rgba(255, 255, 255, 0.7);
  --color-text-tertiary: rgba(255, 255, 255, 0.5);
  --color-background: var(--color-black);
  --color-accent: var(--color-primary-orange);
}
```

## Typography

From Figma:

```css
:root {
  /* Font families (TBD) */
  --font-family-heading: [Extract from Figma];
  --font-family-body: [Extract from Figma];
  
  /* Font sizes (modular scale) */
  --font-size-xs: 0.75rem;   /* 12px */
  --font-size-sm: 0.875rem;  /* 14px */
  --font-size-base: 1rem;    /* 16px */
  --font-size-lg: 1.125rem;  /* 18px */
  --font-size-xl: 1.5rem;    /* 24px */
  --font-size-2xl: 2rem;     /* 32px */
  --font-size-3xl: 3rem;     /* 48px */
  --font-size-4xl: 4rem;     /* 64px */
  
  /* Line heights */
  --line-height-tight: 1.2;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
}
```

## Spacing

```css
:root {
  --space-xs: 0.25rem;   /* 4px */
  --space-sm: 0.5rem;    /* 8px */
  --space-md: 1rem;      /* 16px */
  --space-lg: 1.5rem;    /* 24px */
  --space-xl: 2rem;      /* 32px */
  --space-2xl: 3rem;     /* 48px */
  --space-3xl: 4rem;     /* 64px */
}
```

## Layout

```css
:root {
  /* Content width (max-width for 2K screens) */
  --content-max-width: 1920px;
  
  /* Header */
  --header-height: 80px;
  
  /* Breakpoints for responsive */
  --breakpoint-sm: 640px;    /* Small phones */
  --breakpoint-md: 768px;    /* Tablets */
  --breakpoint-lg: 1024px;   /* Desktops */
  --breakpoint-xl: 1280px;   /* Large desktops */
  --breakpoint-2xl: 1920px;  /* Extra large (2K) */
}
```

## Other

```css
:root {
  /* Transitions */
  --transition-fast: 150ms ease-in-out;
  --transition-normal: 300ms ease-in-out;
  --transition-slow: 500ms ease-in-out;
  
  /* Shadows (optional) */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
}
```

## Usage Example

```css
h1 {
  font-family: var(--font-family-heading);
  font-size: var(--font-size-4xl);
  color: var(--color-text-primary);
  line-height: var(--line-height-tight);
  margin-bottom: var(--space-lg);
}
```

---

## TODO

- [ ] Extract exact colors from Figma (hex codes)
- [ ] Extract font families and weights from Figma
- [ ] Finalize typography scale
- [ ] Define breakpoints for responsive design
