let intro = document.querySelector(".intro");
let logo = document.querySelector(".logo-header");
let logoSpan = document.querySelectorAll(".logo");

window.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    logoSpan.forEach((span, idx) => {
      setTimeout(() => {
        span.classList.add('active');
      }, (idx + 1) * 400);
    });

    setTimeout(() => {
      logoSpan.forEach((span, idx) => {
        setTimeout(() => {
          span.classList.remove('active');
          span.classList.add('fade');
        }, (idx + 1) * 50)
      })
    }, 2000);

    setTimeout(() => {
      intro.style.top = '-100vh';
    }, 2300)
  })
})


window.addEventListener("scroll", function () {
  var header = document.querySelector("header");
  header.classList.toggle("sticky", window.scrollY)
})


ScrollReveal({
  // reset: true,
  distance: '80px',
  duration: 2000,
  delay: 100
});

ScrollReveal().reveal('.home-content, .heading', { origin: 'top' });
ScrollReveal().reveal('.home-img, .contact form', { origin: 'bottom' });
ScrollReveal().reveal('.home-content h1, .about-img', { origin: 'left' });
ScrollReveal().reveal('.home-content p, .about-content, .services', { origin: 'right' });


const typed = new Typed('.multiple-text', {
  strings: ['Mock Interviews','Interview Preparation Tools'],
  typeSpeed: 70,
  backSpeed: 50,
  backDelay: 1000,
  loop: true
});



const checkboxes = document.querySelectorAll('.bg-color-checkbox');
checkboxes.forEach(checkbox => {
  checkbox.addEventListener('change', function () {
    updateProgressBar();
    storeMarkedQuestions();
    const questionDiv = this.parentElement;
    questionDiv.style.backgroundColor = this.checked ? 'green' : 'initial';
  });
});
