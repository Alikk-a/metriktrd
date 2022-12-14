'use strict';

function timeConverter(UNIX_timestamp){
      var a = new Date(UNIX_timestamp * 1000);
      var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
      var months_n = ['01','02','03','04','05','06','07','08','09','10','11','12'];
      var year = a.getFullYear();
      var month = months_n[a.getMonth()];
      var date = a.getDate();
      var hour = a.getHours();
      var min = a.getMinutes();
      var sec = a.getSeconds();
      var time = date +'-' + month + '-' + year + ' ' + hour + ':' + min + ':' + sec ;
      return time;
}

function changeType (vardata, id_out) {
    if (vardata.data[0].type == 'scatter') {
        for (let key in vardata.data) {
            if (vardata.data[key].name != "price BTC") {
                vardata.data[key].type = 'bar';
            }
        };
    } else {
        for (let key in vardata.data) {
            vardata.data[key].type = 'scatter';
        };
    }
    Plotly.newPlot(id_out, vardata,{});
}

function modeBar (vardata, id_out) {
    console.log(vardata.layout.barmode);
    if (vardata.layout.barmode == "stack") {
        vardata.layout.barmode = "";
    } else {
        vardata.layout.barmode = "stack";
    }
    Plotly.newPlot(id_out, vardata,{});
}

function onoffSlide (vardata, id_out) {
    if (vardata.layout.xaxis.rangeslider.visible) {
        vardata.layout.xaxis.rangeslider = {visible: false};
    } else {
        vardata.layout.xaxis.rangeslider = {visible: true};
    }
    Plotly.newPlot(id_out, vardata,{});
}

class GraphModule {
    constructor(name, subname, filename, idout, variabl, rangestart, slider, laycolor, barmode, barline, coment, parentSelector) {
        this.filename = filename;
        this.name = name;
        this.subname = subname;
        this.idout = idout;
        this.variabl = variabl;
        this.rangestart = rangestart;
        this.slider = slider;
        this.laycolor = laycolor;
        this.barmode = barmode;
        this.barline = barline;
        this.coment = coment;
        this.parent = document.querySelector(parentSelector);
        this.varout();
    }

    // сборка итоговой переменной
    varout() {
        this.variabl.layout.xaxis.rangeslider = {visible: this.slider};
        this.variabl.config = {displaylogo: false, modeBarButtonsToRemove: ['pan2d','select2d','lasso2d','zoomOut2d','zoomIn2d','zoom2d','toggleSpikelines']};
        this.variabl.layout.barmode = this.barmode;
        var dat = Date.parse(this.rangestart);
        var rangeEnd = new Date();
        this.variabl.layout.xaxis.range = [dat, rangeEnd];
        this.variabl.layout.plot_bgcolor = this.laycolor;
        for (let key in this.variabl.data) {
            if (this.variabl.data[key].name != "price BTC") {
                this.variabl.data[key].type = this.barline;
            }
        };
        if(this.coment == 'None') {
            this.coment = '';
        };
    }

    render() {
        const element = document.createElement('div');
        let varib = this.variabl;
        element.innerHTML = `
            <div class="card"  id=${this.idout}_L>
                <div class="filter">
                    <a class="icon" data-bs-toggle="dropdown"><i class="bi bi-gear-fill"></i></a>
                    <ul class="dropdown-menu dropdown-menu-end dropdown-menu-arrow">
                        <li><a onclick="changeType(${this.filename}, '${this.idout}')" class="dropdown-item"
                               style="cursor: pointer">Тип Line-Bar</a></li>
                        <li><a onclick="modeBar(${this.filename}, '${this.idout}')" class="dropdown-item"
                               style="cursor: pointer">Бары Сумарно - Рядом</a></li>
                        <li><a onclick="onoffSlide(${this.filename}, '${this.idout}')"
                               class="dropdown-item" style="cursor: pointer">Слайдер Off-On</a></li>
                    </ul>
                </div>
                <div class="card-body">
                    <h5 class="card-title">${this.name}<span>${this.subname}</span></h5>
                    <div class="chart" id="${this.idout}"></div>
                    <div class="card-footer">${this.coment}</div>
                </div>
            </div>
        `;
        this.parent.append(element);
        Plotly.newPlot(this.idout, this.variabl,{});
    }
}