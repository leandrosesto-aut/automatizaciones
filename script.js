/* ==========================================================================
   LEANDRO SESTO | AUTOMATIZACIONES - INTERACTION LOGIC
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  
  // 1. MOBILE NAVIGATION TOGGLE
  const navToggle = document.getElementById('nav-toggle');
  const navMenu = document.getElementById('nav-menu');
  
  if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
      navMenu.classList.toggle('open');
      
      // Change icon bars to close
      const icon = navToggle.querySelector('i');
      if (navMenu.classList.contains('open')) {
        icon.className = 'fa-solid fa-xmark';
      } else {
        icon.className = 'fa-solid fa-bars';
      }
    });

    // Close menu when clicking a link
    const navLinks = navMenu.querySelectorAll('a');
    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        navMenu.classList.remove('open');
        navToggle.querySelector('i').className = 'fa-solid fa-bars';
      });
    });
  }

  // 2. NAVBAR SCROLL EFFECT
  const navbar = document.getElementById('navbar');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });

  // 3. SCROLL REVEAL ANIMATIONS (Intersection Observer)
  const revealElements = document.querySelectorAll('.reveal');
  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('active');
        observer.unobserve(entry.target); // Stop observing once revealed
      }
    });
  }, {
    threshold: 0.15,
    rootMargin: '0px 0px -50px 0px'
  });

  revealElements.forEach(element => {
    revealObserver.observe(element);
  });

  // 4. ACTIVE NAVIGATION LINK ON SCROLL
  const sections = document.querySelectorAll('section, header');
  const menuLinks = document.querySelectorAll('.nav-link');

  window.addEventListener('scroll', () => {
    let current = '';
    
    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.clientHeight;
      if (window.scrollY >= (sectionTop - 150)) {
        current = section.getAttribute('id');
      }
    });

    menuLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === `#${current}`) {
        link.classList.add('active');
      }
    });
  });

  // 5. COPY EMAIL TO CLIPBOARD WITH TOOLTIP
  const btnCopy = document.getElementById('btn-copy');
  const emailLink = document.getElementById('email-link');
  const tooltip = document.getElementById('copy-tooltip');

  if (btnCopy && tooltip && emailLink) {
    btnCopy.addEventListener('click', (e) => {
      e.preventDefault();
      
      const emailText = emailLink.innerText.trim();
      
      // Use Clipboard API
      navigator.clipboard.writeText(emailText).then(() => {
        // Show Tooltip
        tooltip.classList.add('show');
        
        // Hide Tooltip after 2 seconds
        setTimeout(() => {
          tooltip.classList.remove('show');
        }, 2000);
      }).catch(err => {
        console.error('Error al copiar el texto: ', err);
      });
    });
  }

  // 6. INTERACTIVE BACKGROUND CANVAS PARTICLES
  const canvas = document.getElementById('canvas-bg');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    let particlesArray = [];
    
    // Set canvas size
    function resizeCanvas() {
      canvas.width = window.innerWidth;
      // Limit canvas animation height to hero area for better performance
      const heroSection = document.getElementById('hero');
      canvas.height = heroSection ? heroSection.offsetHeight : window.innerHeight;
    }
    
    window.addEventListener('resize', () => {
      resizeCanvas();
      initParticles();
    });
    
    resizeCanvas();

    // Mouse interactive coordinates
    const mouse = {
      x: null,
      y: null,
      radius: 100 // Area of influence
    };

    window.addEventListener('mousemove', (event) => {
      mouse.x = event.x;
      mouse.y = event.y + window.scrollY; // adjust for scroll
    });

    window.addEventListener('mouseout', () => {
      mouse.x = null;
      mouse.y = null;
    });

    // Particle Class
    class Particle {
      constructor(x, y, directionX, directionY, size, color) {
        this.x = x;
        this.y = y;
        this.directionX = directionX;
        this.directionY = directionY;
        this.size = size;
        this.color = color;
      }
      
      // Draw single particle
      draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2, false);
        ctx.fillStyle = this.color;
        ctx.fill();
      }
      
      // Update position and interactions
      update() {
        // Bounce off bounds
        if (this.x > canvas.width || this.x < 0) {
          this.directionX = -this.directionX;
        }
        if (this.y > canvas.height || this.y < 0) {
          this.directionY = -this.directionY;
        }
        
        // Mouse interact (push away)
        if (mouse.x !== null && mouse.y !== null) {
          let dx = mouse.x - this.x;
          let dy = mouse.y - this.y;
          let distance = Math.sqrt(dx * dx + dy * dy);
          
          if (distance < mouse.radius + this.size) {
            if (mouse.x < this.x && this.x < canvas.width - this.size * 10) {
              this.x += 2;
            }
            if (mouse.x > this.x && this.x > this.size * 10) {
              this.x -= 2;
            }
            if (mouse.y < this.y && this.y < canvas.height - this.size * 10) {
              this.y += 2;
            }
            if (mouse.y > this.y && this.y > this.size * 10) {
              this.y -= 2;
            }
          }
        }
        
        // Regular speed drift
        this.x += this.directionX;
        this.y += this.directionY;
        
        this.draw();
      }
    }

    // Populate particles
    function initParticles() {
      particlesArray = [];
      // Dynamic count based on screen size
      let numberOfParticles = (canvas.width * canvas.height) / 18000;
      numberOfParticles = Math.min(numberOfParticles, 80); // Cap at 80 particles
      
      for (let i = 0; i < numberOfParticles; i++) {
        let size = (Math.random() * 2) + 1; // 1 to 3px
        let x = (Math.random() * ((canvas.width - size * 2) - size * 2)) + size * 2;
        let y = (Math.random() * ((canvas.height - size * 2) - size * 2)) + size * 2;
        let directionX = (Math.random() * 0.4) - 0.2; // slow drift speed
        let directionY = (Math.random() * 0.4) - 0.2;
        
        // Alternate colors between Indigo and Teal (subtle for light background)
        let color = i % 2 === 0 ? 'rgba(79, 70, 229, 0.1)' : 'rgba(13, 148, 136, 0.1)';
        
        particlesArray.push(new Particle(x, y, directionX, directionY, size, color));
      }
    }

    // Connect particles with lines
    function connectParticles() {
      let opacityValue = 1;
      for (let a = 0; a < particlesArray.length; a++) {
        for (let b = a; b < particlesArray.length; b++) {
          let dx = particlesArray[a].x - particlesArray[b].x;
          let dy = particlesArray[a].y - particlesArray[b].y;
          let distance = Math.sqrt(dx * dx + dy * dy);
          
          if (distance < 110) {
            opacityValue = 1 - (distance / 110);
            ctx.strokeStyle = `rgba(79, 70, 229, ${opacityValue * 0.04})`;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(particlesArray[a].x, particlesArray[a].y);
            ctx.lineTo(particlesArray[b].x, particlesArray[b].y);
            ctx.stroke();
          }
        }
      }
    }

    // Animation Loop
    function animate() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      for (let i = 0; i < particlesArray.length; i++) {
        particlesArray[i].update();
      }
      
      connectParticles();
      requestAnimationFrame(animate);
    }
    
    initParticles();
    animate();
  }


  // ==========================================================================
  // 8. FAQ ACCORDION LOGIC
  // ==========================================================================
  const faqQuestions = document.querySelectorAll('.faq-question');
  faqQuestions.forEach(question => {
    question.addEventListener('click', () => {
      const answer = question.nextElementSibling;
      const isExpanded = question.getAttribute('aria-expanded') === 'true';
      
      // Close other FAQ items
      faqQuestions.forEach(otherQuestion => {
        if (otherQuestion !== question) {
          otherQuestion.setAttribute('aria-expanded', 'false');
          otherQuestion.nextElementSibling.style.maxHeight = null;
        }
      });
      
      // Toggle current item
      if (isExpanded) {
        question.setAttribute('aria-expanded', 'false');
        answer.style.maxHeight = null;
      } else {
        question.setAttribute('aria-expanded', 'true');
        answer.style.maxHeight = answer.scrollHeight + 'px';
      }
    });
  });

  // ==========================================================================
  // 9. B2B CONTACT FORM MOCK SUBMISSION
  // ==========================================================================
  const contactForm = document.getElementById('contact-form');
  const formSuccess = document.getElementById('form-success');
  const btnSubmit = document.getElementById('btn-submit-form');
  
  if (contactForm && formSuccess) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();
      
      const emailInput = document.getElementById('form-email');
      const email = emailInput.value.trim();
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      
      if (!emailRegex.test(email)) {
        emailInput.style.borderColor = 'var(--error)';
        return;
      }
      
      // Reset input style
      emailInput.style.borderColor = '';
      
      // Show loading state
      if (btnSubmit) {
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '<span>Enviando...</span> <i class="fa-solid fa-spinner fa-spin"></i>';
        
        // Simulate API call (1.5 seconds)
        setTimeout(() => {
          contactForm.style.display = 'none';
          formSuccess.style.display = 'block';
        }, 1500);
      }
    });
  }

});
