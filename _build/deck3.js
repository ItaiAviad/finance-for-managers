/* explanation buttons: a click opens the note over the slide; a second click (or a click on the note) closes it */
document.addEventListener('click',e=>{const o=e.target.closest('.xov');if(o){e.stopPropagation();o.remove();return;}
 const b=e.target.closest('.xbtn');if(!b)return;e.stopPropagation();const sl=b.closest('section');let v=sl.querySelector('.xov');
 if(v){const same=v.dataset.k===b.dataset.k;v.remove();if(same)return;}
 v=document.createElement('div');v.className='xov';v.dataset.k=b.dataset.k;v.innerHTML=b.nextElementSibling.innerHTML+'<small class="xcl">לחצו על הביאור כדי לסגור אותו</small>';sl.appendChild(v);},true);
document.addEventListener('keydown',()=>document.querySelectorAll('.xov').forEach(x=>x.remove()),true);
