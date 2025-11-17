document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('themeToggle');

  toggle.addEventListener('click', () => {
    document.body.classList.toggle('dark');
    toggle.textContent = document.body.classList.contains('dark')
      ? '☀️ Light Mode'
      : '🌙 Dark Mode';
  });
});

