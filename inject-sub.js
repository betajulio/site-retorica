
const fs = require('fs');
const files = ['galeria.html', 'noticias.html', 'repertorio.html', 'setlist.html', 'sugestoes.html', 'logs.html', 'audit.html'].map(f => 'site-retorica-main/' + f);
for (const file of files) {
  if (!fs.existsSync(file)) continue;
  let content = fs.readFileSync(file, 'utf8');
  
  content = content.replace(
    /<span class="nav-user" id="navUser" style="display:none">.*?Membro<\/span>/,
    '$&\n    <a href="index.html" class="coin-balance" id="coinBalance" style="display:none;text-decoration:none"><img src="imagens/coin.png" alt="Retorica Coin"><strong id="coinBalanceValue">0</strong></a>'
  );

  content = content.replace(
    /<span class="nav-user" id="navUserMobile" style="display:none;text-align:center">.*?Membro<\/span>/,
    '$&\n    <a href="index.html" class="coin-balance" id="coinBalanceMobile" style="display:none;text-decoration:none;margin:0 auto"><img src="imagens/coin.png" alt="Retorica Coin"><strong id="coinBalanceValueMobile">0</strong></a>'
  );

  content = content.replace(
    /document\.getElementById\('navUser'\)\.style\.display\s*=\s*isLoggedIn \? '' : 'none';/,
    document.getElementById('navUser').style.display   = isLoggedIn ? '' : 'none';\n  if (isLoggedIn && isMember && auth.currentUser) { getDoc(doc(db, 'member_stats', auth.currentUser.email.toLowerCase())).then(s => { const c = s.exists() ? (s.data().coins||0) : 0; const d = document.getElementById('coinBalance'); const m = document.getElementById('coinBalanceMobile'); if(d){d.style.display='flex';document.getElementById('coinBalanceValue').textContent=c;} if(m){m.style.display='flex';document.getElementById('coinBalanceValueMobile').textContent=c;} }).catch(()=>{}); } else { const d = document.getElementById('coinBalance'); const m = document.getElementById('coinBalanceMobile'); if(d)d.style.display='none'; if(m)m.style.display='none'; }
  );

  fs.writeFileSync(file, content, 'utf8');
}

