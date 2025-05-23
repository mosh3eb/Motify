// Add smooth scrolling to all links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    document.querySelector(this.getAttribute('href')).scrollIntoView({
      behavior: 'smooth'
    });
  });
});

// Add animation to admonitions
document.querySelectorAll('.admonition').forEach((admonition) => {
  admonition.style.opacity = '0';
  admonition.style.transform = 'translateY(20px)';
  admonition.style.transition = 'all 0.3s ease';
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  });
  
  observer.observe(admonition);
});

// Add theme toggle animation
const themeToggle = document.querySelector('.md-toggle');
if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    document.body.style.transition = 'background-color 0.3s ease';
  });
}

// Add hover effect to navigation items
document.querySelectorAll('.md-nav__item').forEach((item) => {
  item.addEventListener('mouseenter', () => {
    item.style.transform = 'translateX(5px)';
    item.style.transition = 'transform 0.2s ease';
  });
  
  item.addEventListener('mouseleave', () => {
    item.style.transform = 'translateX(0)';
  });
});

// Add search highlight animation
const searchInput = document.querySelector('.md-search__input');
if (searchInput) {
  searchInput.addEventListener('focus', () => {
    searchInput.style.transform = 'scale(1.02)';
    searchInput.style.transition = 'transform 0.2s ease';
  });
  
  searchInput.addEventListener('blur', () => {
    searchInput.style.transform = 'scale(1)';
  });
}

// Add progress bar animation
window.addEventListener('scroll', () => {
  const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
  const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
  const scrolled = (winScroll / height) * 100;
  
  const progressBar = document.querySelector('.md-progress');
  if (progressBar) {
    progressBar.style.width = scrolled + '%';
  }
});

// Add table of contents highlight
const toc = document.querySelector('.md-nav--secondary');
if (toc) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');
        const tocLink = document.querySelector(`.md-nav--secondary a[href="#${id}"]`);
        if (tocLink) {
          document.querySelectorAll('.md-nav--secondary a').forEach(link => {
            link.classList.remove('active');
          });
          tocLink.classList.add('active');
        }
      }
    });
  }, { threshold: 0.5 });
  
  document.querySelectorAll('h2, h3').forEach(heading => {
    observer.observe(heading);
  });
}

// Add mobile menu animation
const mobileMenuButton = document.querySelector('.md-header__button');
if (mobileMenuButton) {
  mobileMenuButton.addEventListener('click', () => {
    const nav = document.querySelector('.md-nav--primary');
    if (nav) {
      nav.style.transition = 'transform 0.3s ease';
      nav.style.transform = nav.style.transform === 'translateX(0)' ? 'translateX(-100%)' : 'translateX(0)';
    }
  });
}

// Add footer animation
const footer = document.querySelector('.md-footer');
if (footer) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        footer.style.opacity = '1';
        footer.style.transform = 'translateY(0)';
      }
    });
  });
  
  observer.observe(footer);
  footer.style.opacity = '0';
  footer.style.transform = 'translateY(20px)';
  footer.style.transition = 'all 0.3s ease';
} 