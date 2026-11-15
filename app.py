from flask import Flask, render_template_string, request, jsonify
import json
import os

app = Flask(__name__)

FILE = "sleep_data.json"

def load_data():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sleep Tracker</title>

<style>
body {
    background: #0d1117;
    color: white;
    font-family: Arial;
    padding: 30px;
}
.container {
    max-width: 1100px;
    margin: auto;
}
h1 { font-size: 36px; }
.subtitle { color: #8b949e; }
.stats {
    display: flex;
    gap: 15px;
    margin: 30px 0;
}
.stat {
    background: #161b22;
    padding: 20px;
    border-radius: 12px;
    flex: 1;
}
.stat h2 { font-size: 28px; }
.months {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
}
.month {
    background: #161b22;
    padding: 15px;
    border-radius: 12px;
}
.days {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 5px;
}
.day {
    aspect-ratio: 1;
    border-radius: 4px;
    background: #30363d;
    border: none;
    cursor: pointer;
    color: white;
}
.day:hover { outline: 2px solid white; }
.bad { background: #8b0000; }
.low { background: #a3e4a5; }
.good { background: #87CEEB; }
.high { background: #CC5500; }
select {
    background: #161b22;
    color: white;
    padding: 10px;
}
.legend {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
    margin-top: 30px;
}
@media(max-width:700px) {
    .months { grid-template-columns: repeat(2,1fr); }
}
@media(max-width:450px) {
    .months { grid-template-columns: 1fr; }
}
</style>
</head>

<body>
<div class="container">

<h1>🌙 Sleep Tracker</h1>
<p class="subtitle">Track your sleep throughout the year.</p>

<select id="year"></select>

<div class="stats">
<div class="stat"><h2 id="total">0</h2>Recorded Days</div>
<div class="stat"><h2 id="average">0</h2>Average Sleep</div>
<div class="stat"><h2 id="perfect">0</h2>Perfect Days</div>
</div>

<div class="months" id="calendar"></div>

<div class="legend">
<span>🟥 Less than 6h</span>
<span>🟩 6–7h</span>
<span>🟢 7–10h</span>
<span>🩷 10h+</span>
</div>

</div>

<script>
let data = {};

const names = [
"January","February","March","April",
"May","June","July","August",
"September","October","November","December"
];

const yearSelect = document.getElementById("year");

for(let y=2026;y<=2040;y++){
    let option=document.createElement("option");
    option.value=y;
    option.textContent=y;
    if(y===new Date().getFullYear()) option.selected=true;
    yearSelect.appendChild(option);
}

async function loadData(){
    const response=await fetch("/data");
    data=await response.json();
    render();
}

function color(h){
    if(h<6)return "bad";
    if(h<7)return "low";
    if(h<10)return "good";
    return "high";
}

async function editDay(key){
    let value=prompt("How many hours did you sleep?",data[key]??"");
    if(value===null)return;

    if(value.trim()===""){
        delete data[key];
    }else{
        let h=Number(value);
        if(!Number.isFinite(h)||h<0||h>24){
            alert("Enter a number between 0 and 24");
            return;
        }
        data[key]=h;
    }

    await fetch("/save",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify(data)
    });

    render();
}

function render(){
    let year=Number(yearSelect.value);
    let calendar=document.getElementById("calendar");
    calendar.innerHTML="";

    for(let m=0;m<12;m++){
        let box=document.createElement("div");
        box.className="month";

        let title=document.createElement("h3");
        title.textContent=names[m];
        box.appendChild(title);

        let grid=document.createElement("div");
        grid.className="days";

        let first=new Date(year,m,1).getDay();
        let count=new Date(year,m+1,0).getDate();

        for(let i=0;i<first;i++){
            grid.appendChild(document.createElement("div"));
        }

        for(let d=1;d<=count;d++){
            let key=`${year}-${m+1}-${d}`;
            let btn=document.createElement("button");
            btn.className="day";
            btn.textContent=d;

            if(data[key]!==undefined){
                btn.classList.add(color(data[key]));
                btn.title=data[key]+" hours";
            }

            btn.onclick=()=>editDay(key);
            grid.appendChild(btn);
        }

        box.appendChild(grid);
        calendar.appendChild(box);
    }

    updateStats(year);
}

function updateStats(year){
    let values=Object.entries(data)
        .filter(([k])=>k.startsWith(year+"-"))
        .map(([k,v])=>v);

    let total=values.length;
    let average=total?values.reduce((a,b)=>a+b,0)/total:0;
    let perfect=values.filter(h=>h>=7&&h<10).length;

    document.getElementById("total").textContent=total;
    document.getElementById("average").textContent=average.toFixed(1)+"h";
    document.getElementById("perfect").textContent=perfect;
}

yearSelect.onchange=render;
loadData();
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/data")
def get_data():
    return jsonify(load_data())

@app.route("/save", methods=["POST"])
def save():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid data"}), 400
    save_data(data)
    return jsonify({"status": "saved"})

if __name__ == "__main__":
    app.run()
