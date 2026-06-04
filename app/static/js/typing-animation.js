/* ============================================================================
   TYPING-ANIMATION.JS — Typewriter for Slide 2 (Figma node 17:105)
   ============================================================================ */

(function () {
  const texts = [
    'важно доверие аудитории, а не пустая картинка.',
    'зритель должен поверить человеку в кадре.',
    'нужно придумать идею, а не просто снять ролик.',
    'есть цель, но нет визуального решения.',
  ];

  const el = document.getElementById('typing-text');
  if (!el) return;

  let textIndex = 0;
  let charIndex = 0;
  let isDeleting = false;
  const typeSpeed = 60;
  const deleteSpeed = 30;
  const pauseBeforeDelete = 2000;
  const pauseBeforeType = 500;

  function type() {
    const current = texts[textIndex];
    if (isDeleting) {
      el.textContent = current.slice(0, charIndex - 1);
      charIndex--;
      if (charIndex === 0) {
        isDeleting = false;
        textIndex = (textIndex + 1) % texts.length;
        setTimeout(type, pauseBeforeType);
        return;
      }
      setTimeout(type, deleteSpeed);
    } else {
      el.textContent = current.slice(0, charIndex + 1);
      charIndex++;
      if (charIndex === current.length) {
        setTimeout(function () { isDeleting = true; type(); }, pauseBeforeDelete);
        return;
      }
      setTimeout(type, typeSpeed);
    }
  }

  type();
})();
