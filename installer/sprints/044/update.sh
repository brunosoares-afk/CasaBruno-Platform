#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 044"
echo "========================================"
echo

echo "Instalando Dashboard Frontend..."

mkdir -p "$ROOT/frontend"

mkdir -p "$ROOT/frontend/css"
mkdir -p "$ROOT/frontend/js"
mkdir -p "$ROOT/frontend/assets"

cat > "$ROOT/frontend/index.html" << 'HTML'
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>CasaBruno Platform</title>
<link rel="stylesheet" href="css/style.css">
</head>

<body>

<div class="container">

<h1>CasaBruno Platform</h1>

<div id="status">
Carregando...
</div>

</div>

<script src="js/app.js"></script>

</body>
</html>
HTML

cat > "$ROOT/frontend/css/style.css" << 'CSS'
body{
    background:#10151d;
    color:#fff;
    font-family:Arial,Helvetica,sans-serif;
    margin:40px;
}

.container{
    max-width:900px;
    margin:auto;
}

h1{
    color:#27d980;
}

#status{
    margin-top:30px;
    padding:20px;
    background:#1c2430;
    border-radius:8px;
}
CSS

cat > "$ROOT/frontend/js/app.js" << 'JS'
fetch("http://127.0.0.1:8080/")
.then(r=>r.json())
.then(data=>{
    document.getElementById("status").innerHTML=`
        <b>Platform:</b> ${data.platform}<br>
        <b>AI:</b> ${data.ai}<br>
        <b>Status:</b> ${data.status}
    `;
})
.catch(()=>{
    document.getElementById("status").innerHTML="API Offline";
});
JS

echo
echo "[OK] Dashboard Frontend instalado."
echo
