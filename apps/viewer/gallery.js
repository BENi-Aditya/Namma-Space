const PUBLIC_VIEW = false;
if(new URLSearchParams(location.search).has('model')) location.replace('viewer.html'+location.search);
let token=null;
async function load(){
 try{if(PUBLIC_VIEW)throw Error('Public library');const r=await fetch('/api/status');if(r.ok){const s=await r.json();token=s.token;document.querySelector('#admin').hidden=false;}}catch{}
 try{let data; if(token){data=await (await fetch('/api/models')).json();}else{data=await(await fetch('models.json', {cache:'no-store'})).json();await Promise.all(data.models.map(async m=>{const key={gaussian:'splat',pointcloud:'pointcloud',stl:'stl'}[m.defaultAsset]||'pointcloud';try{m.ready=!!m[key]&&(await fetch(m[key],{method:'HEAD'})).ok;}catch{m.ready=false;}}));}
 const ready=data.models.filter(m=>m.ready);document.querySelector('#count').textContent=`${ready.length} AVAILABLE SPACES`;
 const root=document.querySelector('#models');root.replaceChildren();
 for(const m of ready){const card=document.createElement('article');card.className='card';const art=document.createElement('div');art.className='model-art';art.textContent='◇';const title=document.createElement('h2');title.textContent=m.name;const description=document.createElement('p');description.textContent=m.method==='splatfacto'?'Gaussian splat reconstruction':'Point cloud / reconstructed geometry';const row=document.createElement('div');row.className='row';const link=document.createElement('a');link.className='button primary';link.href='viewer.html?model='+encodeURIComponent(m.id);link.textContent='Explore space ↗';row.append(link);
 if(token){const rename=document.createElement('button');rename.textContent='Rename';rename.onclick=async()=>{const name=prompt('Model name',m.name);if(name===null)return;const r=await fetch('/api/rename',{method:'POST',headers:{'Content-Type':'application/json','X-Namma-Token':token},body:JSON.stringify({id:m.id,name})});const result=await r.json();if(!r.ok){alert(result.error);return;}load();};row.append(rename);}
 card.append(art,title,description,row);root.append(card);}
 if(!ready.length){root.className='empty';root.textContent='No exported models are available yet. Complete a training run in the local training studio.';}
 }catch(e){document.querySelector('#message').textContent='Could not load the model library: '+e.message;}}
load();
