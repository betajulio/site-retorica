const fs = require('fs');
const files = ['galeria.html', 'noticias.html', 'repertorio.html', 'setlist.html', 'sugestoes.html', 'logs.html', 'audit.html'];
for (const file of files) {
  if (!fs.existsSync(file)) continue;
  let content = fs.readFileSync(file, 'utf8');
  
  // Replace navUser
  content = content.replace(
    /<span class="nav-user" id="navUser" style="display:none">.*?Membro<\/span>/,
    '$&\n    <a href="index.html" class="coin-balance" id="coinBalance" style="display:none;text-decoration:none"><img src="imagens/coin.png" alt="Retorica Coin"><strong id="coinBalanceValue">0</strong></a>'
  );

  // Replace navUserMobile
  content = content.replace(
    /<span class="nav-user" id="navUserMobile" style="display:none;text-align:center">.*?Membro<\/span>/,
    '$&\n    <a href="index.html" class="coin-balance" id="coinBalanceMobile" style="display:none;text-decoration:none;margin:0 auto"><img src="imagens/coin.png" alt="Retorica Coin"><strong id="coinBalanceValueMobile">0</strong></a>'
  );

  fs.writeFileSync(file, content, 'utf8');
}
