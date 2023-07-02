// functionality to add the a "Go to top" button which will only appear when the the screen will be scorlled down
const toTop = document.querySelector('.gototop')
window.addEventListener("scroll", () => {
   if(window.pageYOffset > 200) {
       toTop.classList.add("active");
   }else{
       toTop.classList.remove("active");
   }
})

// functionality to add the a "Home" button which will only appear when the the screen will be scorlled down
const homeBtn = document.querySelector('.home-btn')
window.addEventListener("scroll", () => {
   if(window.pageYOffset > 200) {
       homeBtn.classList.add("active");
   }else{
       homeBtn.classList.remove("active");
   }
})

// fuctionality to the project slider
const productContainers = [...document.querySelectorAll('.project-container')];
const nxtBtn = [...document.querySelectorAll('.next-btn')];
const preBtn = [...document.querySelectorAll('.prev-btn')];
productContainers.forEach((item, i) => {
    let containerDimensions = item.getBoundingClientRect();
    let containerWidth = containerDimensions.width;

    nxtBtn[i].addEventListener('click', () => {
        item.scrollLeft += containerWidth/2;
    })

    preBtn[i].addEventListener('click', () => {
        item.scrollLeft -= containerWidth/2;
    })
})

// functionality to add a confirmation on delete project
function confirmAction(event, linkId) {
    event.preventDefault();
  
    var link = document.getElementById(linkId);
  
    var message = "With this action, the selected item will be deleted permanently. Are you sure you want to proceed?";
    var confirmation = window.confirm(message);

    if (confirmation) {
        window.location.href = link.href;
      } else {
      }
}