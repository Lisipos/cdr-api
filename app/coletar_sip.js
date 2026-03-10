(async () => {

function wait(ms){ return new Promise(r=>setTimeout(r,ms)); }

// =============================
// CALCULAR ÚLTIMA HORA
// =============================

const agora = new Date();
const umaHoraAtras = new Date(agora.getTime() - (60 * 60 * 1000));

function formatDate(d){
    const dia = String(d.getDate()).padStart(2,'0');
    const mes = String(d.getMonth()+1).padStart(2,'0');
    const ano = d.getFullYear();
    return `${dia}/${mes}/${ano}`;
}

function formatHora(d){
    const h = String(d.getHours()).padStart(2,'0');
    const m = String(d.getMinutes()).padStart(2,'0');
    return `${h}:${m}`;
}

const dataI = formatDate(umaHoraAtras);
const dataF = formatDate(agora);

const horaI = formatHora(umaHoraAtras);
const horaF = formatHora(agora);

console.log("Período coletado:");
console.log(dataI, horaI, "até", dataF, horaF);

// =============================

const iframe = document.querySelector('#next_tab_relatorioEstatisticaSIP');
const doc = iframe.contentWindow.document;

const select = doc.querySelector('#txtRota');
const rotas = [...select.options].filter(o=>o.value);

console.log("Rotas encontradas:", rotas.length);

let csvFinal = "rota,sip_code,quantidade\n";

for (const rota of rotas){

    const nome = rota.textContent.trim();
    const id = rota.value;

    console.log("Coletando:", nome);

    const url = `/relatorioEstatisticaSIP/data?${Math.random()}&relatorioAlarmes=DESC&SORT_CHANGE=&SORT_TAG=create_date&PAGE=1&txtDataI=${encodeURIComponent(dataI)}&txtDataF=${encodeURIComponent(dataF)}&txtHoraInicial=${encodeURIComponent(horaI)}&txtHoraFinal=${encodeURIComponent(horaF)}&txtRota=${id}`;

    const res = await fetch(url,{
        method:"GET",
        credentials:"include",
        headers:{
            "X-Requested-With":"XMLHttpRequest"
        }
    });

    const html = await res.text();

    const matches = [...html.matchAll(/name:'([^']+)', y:(\d+)/g)];

    console.log("SIP encontrados:", matches.length);

    for(const m of matches){
        const sip = m[1];
        const qtd = m[2];

        csvFinal += `"${nome}","${sip}",${qtd}\n`;
    }

    await wait(600);

}

// =============================
// GERAR CSV
// =============================

const blob = new Blob([csvFinal], {type:"text/csv"});
const link = document.createElement("a");

link.href = URL.createObjectURL(blob);
link.download = "relatorio_sip_rotas_ultima_hora.csv";
link.click();

console.log("FINALIZADO 🚀");

})();