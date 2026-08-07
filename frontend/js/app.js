async function updateDashboard(){

    try{

        const response = await fetch("/api/dashboard");
        const data = await response.json();

        document.getElementById("status").innerHTML = `
<div class="card">

<h2>CasaBruno Platform</h2>

<p><b>Hostname:</b> ${data.system.hostname}</p>
<p><b>Sistema:</b> ${data.system.os} ${data.system.release}</p>

<hr>

<p><b>CPU:</b> ${data.system.cpu}%</p>
<p><b>Memória:</b> ${data.system.memory}%</p>
<p><b>Disco:</b> ${data.system.disk}%</p>

<hr>

<p><b>Home Assistant:</b> ${data.homeassistant.status}</p>

<p><b>Gateway:</b> ${data.network.gateway ? "🟢 Online" : "🔴 Offline"}</p>

<p><b>Internet:</b> ${data.network.google ? "🟢 Online" : "🔴 Offline"}</p>

<hr>

<p><b>Containers Docker:</b></p>

<ul>
${data.docker.map(c=>`<li>${c}</li>`).join("")}
</ul>

<p><small>${new Date().toLocaleTimeString()}</small></p>

</div>
`;

    }catch(e){

        document.getElementById("status").innerHTML =
        "<h2>Dashboard Offline</h2>";

    }

}

updateDashboard();

setInterval(updateDashboard,3000);
