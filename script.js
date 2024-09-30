(async () => {
  
  let data = await getData();
  
  let map = L.map('map').setView([48.864, 2.349], 4);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 16,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map);
  
  for(let i=0; i<data.length;i++) {
    
    let cargo = [];
    if(data[i].Cargo_1.trim() !== '') cargo.push(data[i].Cargo_1);
    if(data[i].Cargo_2.trim() !== '') cargo.push(data[i].Cargo_2);
    if(data[i].Cargo_3.trim() !== '') cargo.push(data[i].Cargo_3);
    
    L.marker([
        parseInt(data[i]["Latitude"],10), parseInt(data[i]["Longitude"],10)
    ]).addTo(map).bindPopup(`
<h3>${data[i].NAME}</h3>
<p>
<b>Found in:</b> ${data[i].Year_Found}<br>
<b>Cargo:</b> ${cargo.join(', ')}<br>
    `);

  }

})();

async function getData() {
  return new Promise((resolve, reject) => {
    // hack for skipFirstNLines: https://github.com/mholt/PapaParse/issues/1040
    Papa.parse('https://assets.codepen.io/74045/shipwrecks2.csv', {
      download:true,
      header:true,
      beforeFirstChunk: chunk => [...chunk.split('\n').slice(1)].join('\n'),
      complete:(results) => {       
        resolve(results.data);
        }
      });
  });
}