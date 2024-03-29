getReadings();

var get_reading = setInterval(getReadings, 5000);

var jr

const record_dates = document.getElementsByClassName("record-date")
var coll = document.getElementsByClassName("collapsible");

coll[0].addEventListener("click", function() {
    this.classList.toggle("active");
    for (let i = 0; i < record_dates.length; i++) {
        record_dates[i].classList.toggle("record-hide");
    }
});

function getReadings() {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        jr = JSON.parse(this.responseText)
        
        const animation = document.getElementById("animation");
        
        if (jr.current_speed > 0) {
            animation.classList.remove("sleep")
            animation.classList.add("running")
            setElement("last_run_time", "");
        } else {
            animation.classList.remove("running")
            animation.classList.add("sleep")
            setElement("last_run_time", "Last Active " + formatTime(jr.last_run_time) + " ago");
        }

        setElement("start_date", 'Active since ' + jr.start_date);
        setElement("days_active", '   (' + jr.days_active.toLocaleString('en-GB', {minimumFractionDigits: 0, maximumFractionDigits: 0}) + ' days)');
        setElement("top_speed_record", jr.top_speed_record[0] + ' km/h');
        setElement("top_speed_record_date", 'Set ' + jr.top_speed_record[1]);
        
        if (jr.fastest_10m_record[0] == 10000) {
            setElement("fastest_10m_record", "-");
        } else {
            setElement("fastest_10m_record", formatTime(jr.fastest_10m_record[0]));
        }
        
        if (jr.fastest_100m_record[0] == 10000) {
            setElement("fastest_100m_record", "-");
        } else {
            setElement("fastest_100m_record", formatTime(jr.fastest_100m_record[0]));
        }
        
        setElement("fastest_10m_record_date", 'Set ' + jr.fastest_10m_record[1]);
        setElement("fastest_100m_record_date", 'Set ' + jr.fastest_100m_record[1]);
       
        if (jr.longest_run_record[1] == jr.longest_run_record[3]) {
            setElement("longest_run_dist_time", jr.longest_run_record[0]+ " m (" + formatTime(jr.longest_run_record[2]) + ")");
            setElement("longest_run_date", 'Set ' + jr.longest_run_record[1]);
        } else {
            setElement("longest_run_dist_time", jr.longest_run_record[0]+ " m, " + formatTime(jr.longest_run_record[2]));
            setElement("longest_run_date", 'Set ' + jr.longest_run_record[1] + ', ' + jr.longest_run_record[3]);
        }
        
        setElement("max_distance_day_record", jr.max_distance_day_record[0] + " m");
        setElement("max_distance_day_record_date", 'Set ' + jr.max_distance_day_record[1]);
            
        for (let i = 0; i < jr.new_record_day.length; i++) {
            if (jr.new_record_day[i] != "") {
                if (!document.getElementById(jr.new_record_day[i]).classList.contains("record-highlight")) {
                    document.getElementById(jr.new_record_day[i]).classList.add("record-highlight");
                }
                
                var highlight_row = document.getElementById(jr.new_record_day[i] + "_label").innerHTML
                if (document.getElementById(jr.new_record_day[i] + "_label").innerHTML != "") {
                    document.getElementById(jr.new_record_day[i] + "_label").innerHTML =  highlight_row.replace(/\*/g, '') + ' *';
                }
            }
         }
        
        allTimeDropdownChange();
        activityDropdownChange();
        frequencyDropdownChange();
    }
    
    xhttp.open("POST", "readData", true);
    xhttp.send();
}

function formatDistance(value) {
    if (value < 1000) {
        return value + ' m';
    } else if (value < 100000) {
        return (value / 1000).toFixed(1) + ' km';
    } else {
        return (value / 1000).toLocaleString('en-GB', { minimumFractionDigits: 0, maximumFractionDigits: 0 }) + ' km';
    }
}

function formatTime(value) {
    if (value < 60) {
        return value + ' s';
    } else if (value < 3600) {
        return Math.floor(value / 60) + 'm ' + (value % 60).toFixed(0) + 's';
    } else if (value < 360000) {
        return Math.floor(value / 3600) + 'h ' + ((value / 60) % 60).toFixed(0) + 'm';
    } else {
        return (value / 3600).toLocaleString('en-GB', { minimumFractionDigits: 0, maximumFractionDigits: 0 }) + ' hrs';
    }
}

function formatGeneral(value) {
    if (value < 10){
        return value;
    } else if (value < 100){
        return value.toFixed(1);
    } else {
        return value.toLocaleString('en-GB', {minimumFractionDigits: 0, maximumFractionDigits: 0});
    }
}

function setElement(id, content) {
  document.getElementById(id).innerHTML = content;
}

function allTimeDropdownChange() {
    var at = document.getElementById("all_time_dropdown").value;
    setElement("distance_all_time", formatDistance(jr.distance_all_time[at]));
    setElement("time_all_time", formatTime(jr.time_all_time[at]));
    setElement("avg_speed_all_time", jr.avg_speed_all_time + ' km/h');
    setElement("runs_all_time", formatGeneral(jr.runs_all_time[at]));
    setElement("calories_all_time", formatGeneral(jr.calories_all_time[at]) + ' kcal');
    setElement("rotations_all_time", formatGeneral(jr.rotations_all_time[at]) + ' Wheel Rotations');
    setElement("peanuts_all_time", formatGeneral(jr.peanuts_all_time[at]) + ' Peanuts');
}

function activityDropdownChange() {
    var act_value = document.getElementById("activity_dropdown").value;
    var data_group, xTitle, labels, sortedArray, arrayOrder, actDataSet, axesTitle;
    
    if (act_value == 0){
        actChart.data.labels = Array.from({length: 24}, (_, i) => i + 1)
        data_group = jr.distance_hour
        xTitle = "Hour"
        
    } else if (act_value == 1){
        actChart.data.labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        data_group = jr.distance_month
        xTitle = "Month"
    }
    
    actDataSet = {
            data: data_group,
            borderWidth: 1,
            barPercentage: 1.0,
            categoryPercentage: 1.0,
            backgroundColor: '#5d279f'
    }
    
    axesTitle = {
        display: true,
        text: xTitle,
        color: "black",
    }

    actChart.data.datasets = []
    actChart.data.datasets.push(actDataSet);
    actChart.options.scales.x.title = axesTitle;
    actChart.update('none');
}

function frequencyDropdownChange() {
    var f = document.getElementById("frequency_dropdown").value;
    var data_group, freqAvg, avg_line_label, xTitle, tooltiptitle, sortedArray, arrayOrder;
    
    if (f == 0){
        freqChart.data.labels = Array.from(Array(26).keys()).concat(['>25']);
        tooltiptitle = Array.from({length: 25 }, (_, i) => `${i}-${i + 1}`).concat(['>25']);
        data_group = jr.speed_frequency
        freqAvg = jr.avg_speed_all_time
        avg_line_label = "Avg: " + jr.avg_speed_all_time + " km/h"
        xTitle = "Speed (km/h)"

    } else if (f == 1){
        freqChart.data.labels = Array.from({length: 31}, (_, i) => i * 10 === 0 ? '0' : (i * 10) + '').concat(['>300']);
        tooltiptitle = Array.from({length: 30 }, (_, i) => `${i * 10}-${(i + 1)*10}`).concat(['>300']);
        data_group = jr.run_distance_frequency
        freqAvg = jr.avg_run_distance / 10
        avg_line_label = "Avg: " + jr.avg_run_distance.toFixed(0) + " m"
        xTitle = "Distance (m)"
        
    } else if (f == 2){
        freqChart.data.labels = ['0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100', '110', '120', '>120']
        tooltiptitle = Array.from({length: 12 }, (_, i) => `${i * 10}-${(i + 1)*10}`).concat(['>120']);
        data_group = jr.run_time_frequency
        freqAvg = jr.avg_run_duration / 10
        avg_line_label = "Avg: " + jr.avg_run_duration.toFixed(0) + " s"
        xTitle = "Time (s)"
    }
    
    freqChart.options.plugins.tooltip.callbacks.title = (context) => tooltiptitle[context[0].dataIndex];

    var freqDataSet = {
        data: data_group,
        borderWidth: 1,
        backgroundColor: '#db6efa',
        barPercentage: 1.0,
        categoryPercentage: 1.0,
        xAxisID: "freqData"
    }
    
    var freqAnnot = {
            type: 'line',
            xMin: freqAvg,
            xMax: freqAvg,
            yMin: 0,
            yMax: Math.max(...data_group)/4,
            borderWidth: 1.5,
            borderColor: 'black',
            
            arrowHeads: {
                start: {
                    display: true,
                    length: 8,
                    width: 4,
                }
            },
            
            label: {
              display: true,
              position: 'end',
              yAdjust: -10,
              content: avg_line_label,
              backgroundColor: '#00000000',
              color: 'black',
              
            font: {
                size: 12,
                weight: 'normal'
              }
            }
    }
    var freqAxes = {
        display: false,
        max: data_group.length - 1,
        position: 'bottom'
    }
    var axesTitle = {
        display: true,
        text: xTitle,
        color: "black"
    }
          
    freqChart.data.datasets = []
    freqChart.data.datasets.push(freqDataSet);
    freqChart.options.plugins.annotation.annotations = []
    freqChart.options.plugins.annotation.annotations.push(freqAnnot);
    freqChart.options.scales.x.title = axesTitle;
    freqChart.options.scales.freqData = freqAxes;
    freqChart.update('none');
}

actChart = new Chart(document.getElementById('activity-chart'), {
  type: 'bar',
  options: {
    maintainAspectRatio: false,
    scales: {
      x: {
        ticks: {
          color: "black",
          align: "center",
          maxRotation: 0,
          minRotation: 0,
        },
        grid: {
          display: false
        }
      },
      y: {
        beginAtZero: true,
        title: {
           display: true,
           text: "Distance (%)",
           color: "black"
        },
        ticks: {
          color: "black"
        },
        grid: {
          display: false
        }
      },
    },
    plugins: {
      legend: {
        display: false
      },
    }
  },
});
          
freqChart = new Chart(document.getElementById('frequency-graph'), {
  type: 'bar',
  options: {
    maintainAspectRatio: false,
    scales: {
      freqData: {
         display: false,
         position: 'bottom'
      },
      x: {
        offset: false,
        grid: {
            offset: false,
            display: false
        },
        ticks: {
          color: "black",
          align: "center",
          maxRotation: 0,
          minRotation: 0,
        },
      },
      y: {
        beginAtZero: true,
        title: {
           display: true,
           text: "Frequency (%)",
           color: "black"
        },
        ticks: {
          color: "black"
        },
        grid: {
          display: false
        }
      },
    },
    plugins: {
      legend: {
        display: false
      },
    },
  },
});

var j, selElmnt, selectedItem, optionList, optionItem;

/*look for any elements with the class "recent-select":*/
recentSelect = document.getElementsByClassName("recent-select");

for (const element of recentSelect) {
  selElmnt = element.getElementsByTagName("select")[0];

  // For each element, create a new DIV that will act as the selected item
  selectedItem = document.createElement("DIV");
  selectedItem.setAttribute("class", "select-selected");
  selectedItem.innerHTML = selElmnt.options[selElmnt.selectedIndex].innerHTML;
  element.appendChild(selectedItem);

  // For each element, create a new DIV that will contain the option list
  optionList = document.createElement("DIV");
  optionList.setAttribute("class", "select-items select-hide");

  for (j = 0; j < selElmnt.length; j++) {
    // For each option, create a new DIV that will act as an option item
    optionItem = document.createElement("DIV");
    optionItem.innerHTML = selElmnt.options[j].innerHTML;
    
    optionItem.addEventListener("click", function(e) {
        // When an item is clicked, update the original select box and the selected item
        var y, i, selectBox, h
        selectBox = this.parentNode.parentNode.getElementsByTagName("select")[0];
        h = this.parentNode.previousSibling;

        for (i = 0; i < selectBox.length; i++) {
          if (selectBox.options[i].innerHTML == this.innerHTML) {
            selectBox.selectedIndex = i;
            h.innerHTML = this.innerHTML;
            y = this.parentNode.getElementsByClassName("same-as-selected");
            
            for (const el of y) {
              el.removeAttribute("class");
            }
            
            this.setAttribute("class", "same-as-selected");
            
            if (selectBox.id == "all_time_dropdown") {
                allTimeDropdownChange();
            } else if (selectBox.id == "activity_dropdown") {
                activityDropdownChange();
            } else if (selectBox.id == "frequency_dropdown") {
                frequencyDropdownChange();
            }
            break;
          }
        }
        h.click();
    });
    optionList.appendChild(optionItem);
  }
  element.appendChild(optionList);
  
  selectedItem.addEventListener("click", function(e) {
      // Opens select box when clicked and closes any other open select boxes
      e.stopPropagation();
      closeAllSelect(this);
      this.nextSibling.classList.toggle("select-hide");
      this.classList.toggle("select-arrow-active");
    });
}

function closeAllSelect(elmnt) {
  // Closes all select boxes in document except current select box.
  selectItems = document.getElementsByClassName("select-items");
  selectSelected = document.getElementsByClassName("select-selected");
  
  for (const element of selectSelected) {
    if (elmnt != element) {
      element.classList.remove("select-arrow-active");
    }
  }
  
  for (const element of selectItems) {
    if (elmnt != element) {
      element.classList.add("select-hide");
    }
  }
}

// Closes select box if user clicks outside
document.addEventListener("click", closeAllSelect);