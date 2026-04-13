# Organizacao Local Do Projeto

Este projeto esta sendo mantido localmente e publicado manualmente no GitHub Pages.

## Estrutura principal

- `site-retorica-main/`: arquivos do site estatico
- `functions/`: funcoes Firebase em Python
- `Backups/`: backups zipados locais
- `.firebaserc` e `firebase.json`: configuracao de deploy

## Fluxo recomendado

1. Fazer alteracoes locais.
2. Conferir o que mudou com `git status`.
3. Criar backup zipado antes de mudancas maiores.
4. Publicar quando estiver validado.

## Comandos uteis

Ver o que mudou:

```powershell
git status
```

Salvar um checkpoint local:

```powershell
git add .
git commit -m "checkpoint local"
```

Salvar status + backup + commit com um comando:

```powershell
.\checkpoint.ps1 -Mensagem "descrição da alteração"
```

Gerar backup zipado:

```powershell
$ts = Get-Date -Format 'yyyy-MM-dd_HHmmss'
Compress-Archive -Path '.\site-retorica-main', '.\functions', '.\.firebaserc', '.\firebase.json' -DestinationPath ".\Backups\projeto-retorica_$ts.zip" -Force
```

Publicar no Firebase/GitHub Pages:

```powershell
firebase deploy
```

## Observacoes

- O `.gitignore` da raiz evita versionar `Backups/`, `.claude/`, `venv/` e arquivos temporarios.
- O arquivo `site-retorica-main/index.html.backup` continua versionado por ser um backup funcional do proprio projeto.
