// shared utilities, updates login/logout link
async function updateAuthLink(){
  const a = document.getElementById('authLink');
  if(!a) return;
  try{
    const res = await fetch('/auth/me');
    const r = await res.json();
    if(r.logged_in){
      a.textContent = 'Logout';
      a.href = '#';
      a.addEventListener('click', async (e)=>{ e.preventDefault(); await fetch('/auth/logout',{method:'POST'}); window.location.reload(); });
    } else {
      a.textContent = 'Login';
      a.href = '/login.html';
    }
  }catch(e){
    console.log(e);
  }
}

// Guest ID management using localStorage
function getGuestId(){
  let guestId = localStorage.getItem('guest_id');
  if(!guestId){
    guestId = 'guest_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('guest_id', guestId);
  }
  return guestId;
}

// Get current user ID or guest ID for API calls
async function getCustomerId(){
  try{
    const res = await fetch('/auth/me');
    const r = await res.json();
    if(r.logged_in && r.user && r.user.id){
      return r.user.id;
    }
  }catch(e){
    console.log('Auth check failed:', e);
  }
  return getGuestId();
}

updateAuthLink();
