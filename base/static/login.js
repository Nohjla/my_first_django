const container=document.querySelector('.container');
const LogInLink=document.querySelector('.SignInLink');
const RegisterLink=document.querySelector('.SignUpLink');
RegisterLink.addEventListener('click', ()=>{
    container.classList.add('active');
})
LogInLink.addEventListener('click', ()=>{
    container.classList.remove('active');
})