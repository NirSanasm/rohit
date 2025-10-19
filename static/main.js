document.getElementById('ua').textContent = navigator.userAgent;
document.getElementById('platform').textContent = navigator.platform;
document.getElementById('screen').textContent = `${screen.width}x${screen.height}`;

if (navigator.deviceMemory) {
  document.getElementById('memory').textContent = `${navigator.deviceMemory} GB`;
} else {
  document.getElementById('memory').textContent = 'unknown';
}

if (navigator.connection) {
  document.getElementById('connection').textContent = `${navigator.connection.effectiveType} (downlink ${navigator.connection.downlink || 'n/a'})`;
} else {
  document.getElementById('connection').textContent = 'unknown';
}

// public IP
fetch('https://api.ipify.org?format=json')
  .then(r => r.json())
  .then(data => document.getElementById('public-ip').textContent = data.ip)
  .catch(() => document.getElementById('public-ip').textContent = 'error');

// basic download speed test (approx)
async function simpleDownloadTest(){
  const url = 'https://upload.wikimedia.org/wikipedia/commons/3/3f/JPEG_example_flower.jpg';
  const sizeBytes = 600000;
  const start = performance.now();
  try{
    await fetch(url, {cache: 'no-store'});
    const end = performance.now();
    const seconds = (end - start)/1000;
    const mbps = ((sizeBytes*8)/(seconds*1024*1024)).toFixed(2);
    document.getElementById('download-speed').textContent = `${mbps} Mbps (approx)`;
  } catch (e){
    document.getElementById('download-speed').textContent = 'error';
  }
}
simpleDownloadTest();

// Server info
document.getElementById('get-server-info').addEventListener('click', async ()=>{
  const out = document.getElementById('server-info-output');
  out.textContent = 'loading...';
  const r = await fetch('/api/server-info');
  const j = await r.json();
  out.textContent = JSON.stringify(j, null, 2);
});

// ping/traceroute
async function runNet(cmd){
  const host = document.getElementById('host-input').value.trim();
  if(!host){ alert('enter host'); return; }
  const out = document.getElementById('net-output');
  out.textContent = 'running...';
  const resp = await fetch(cmd, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ host })
  });
  const j = await resp.json();
  out.textContent = j.output || j.error || JSON.stringify(j);
}

document.getElementById('btn-ping').addEventListener('click', ()=>runNet('/api/ping'));
document.getElementById('btn-trace').addEventListener('click', ()=>runNet('/api/traceroute'));

// server-side speedtest
document.getElementById('server-speedtest').addEventListener('click', async ()=>{
  const out = document.getElementById('server-speed-output');
  out.textContent = 'running...';
  const r = await fetch('/api/server-speedtest');
  const j = await r.json();
  out.textContent = JSON.stringify(j, null, 2);
});
