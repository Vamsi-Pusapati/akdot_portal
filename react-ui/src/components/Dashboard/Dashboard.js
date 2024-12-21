import React, { useState, useEffect, useCallback } from 'react';
import './Dashboard.css';
import mapImage from './poa.png';
import Plot from 'react-plotly.js';
import DashboardMapComponent from '../MapComponent/DashboardMap';
import { Tooltip } from 'react-tooltip'
function Dashboards() {
  const baseUrl = process.env.REACT_APP_BACKEND_SERVER_URL + "/dashboard/";
  
  const [cycleTime, setCycleTime] = useState({})
  const [hourlyCount, setHourlyCount] = useState({})
  const [waitingTime, setWaitingTime] = useState({})
  const [maxQueueData, setMaxQueueData] = useState({});
  const [sectionCount, setSectionCount] = useState({})
  const [weeklyCount, setWeeklyCount] = useState({})
  const [monthCorrelation, setMonthCorrelation] = useState({})
  const [weekCorrelation, setWeekCorrelation] = useState({})


  const [vehicleType, setVehicleType] = useState('cars');
  const [selectedDay, setSelectedDay] = useState(0);



  const dayOptions = [
    { value: 0, label: 'Today' },
    { value: 1, label: 'Tomorrow' },
    { value: 2, label: '2 Days from Now' },
    { value: 3, label: '3 Days from Now' },
    { value: 4, label: '4 Days from Now' },
    { value: 5, label: '5 Days from Now' },
    { value: 6, label: '6 Days from Now' },
  ];

  const handleDayChange = (event) => {
    setSelectedDay(parseInt(event.target.value)); // Parse string value to integer
    fetchCycleTimeData(selectedDay); 
    fetchHourlyCountsData(vehicleType, selectedDay);
    fetchWaitingTimeData(selectedDay);
    fetchMaximumQueueData(selectedDay);
    fetchSectionCounts(vehicleType, selectedDay);
    fetchWeeklyCounts(vehicleType, selectedDay);
    fetchMonthCorrelation(selectedDay);
    fetchWeekCorrelation(selectedDay);
  };
  const handleVehicleTypeChange = (event) => {
    setVehicleType(event.target.value);
    fetchHourlyCountsData(event.target.value, selectedDay)
    fetchSectionCounts(event.target.value, selectedDay);
    fetchWeeklyCounts(event.target.value, selectedDay);
  };

  const fetchCycleTimeData = useCallback(async (selectedDay) => {
    try {
      const response = await fetch(baseUrl + "cycle_times?day=" + selectedDay, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
  
      if (response.ok) {
        const data = await response.json();
  
        // Convert seconds to decimal minutes
        const convertToMinutes = (seconds) => seconds / 60;
  
        const avgCycleTimesInMinutes = data.average_cycle_times.map(convertToMinutes);
        const maxCycleTimesInMinutes = data.max_cycle_times.map(convertToMinutes);
  
        const cycleplot = {};
        const cycleplot_data = [
          {
            x: data.hours,
            y: avgCycleTimesInMinutes, // Use converted values
            name: 'Average Cycle Time',
            mode: 'lines+markers',
            line: {
              dash: 'solid',
            },
          },
          {
            x: data.hours,
            y: maxCycleTimesInMinutes, // Use converted values
            name: 'Maximum Cycle Time',
            mode: 'lines+markers',
            line: {
              dash: 'dot',
            },
          },
        ];
  
        
      //  const formatToMinutesSeconds = (value) => {
      //    const minutes = Math.floor(value);
      //    const seconds = Math.round((value - minutes) * 60);
      //    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
      // };
  
        const cycleplot_layout = {
          xaxis: {
            title: 'Hour of day',
            showline: true,
            showgrid: true,
            showticklabels: true,
            tickvals: data.hours,
            tickangle: 0,
          },
          yaxis: {
            title: 'Cycle Time (Minutes)', 
            //tickformat: '.2f',
            //tickvals: avgCycleTimesInMinutes.concat(maxCycleTimesInMinutes),
            //ticktext: avgCycleTimesInMinutes.concat(maxCycleTimesInMinutes).map(formatToMinutesSeconds),
          },
          legend: {
            orientation: 'h',
            x: 0.5,
            y: 1.0,
            xanchor: 'center',
            yanchor: 'bottom',
          },
          margin: {
            l: 50,
            r: 50,
            b: 50,
            t: 50,
            pad: 0,
          },
        };
  
        cycleplot.data = cycleplot_data;
        cycleplot.layout = cycleplot_layout;
        setCycleTime(cycleplot);
      }
    } catch (error) {
      console.error('Error fetching cycle time data:', error);
    }
  }, []);
  

  const fetchHourlyCountsData = useCallback(async (vehicleType, selectedDay) => {
    try{
      const response = await fetch(baseUrl + "hourly_counts?vehicle="+vehicleType+"&day=" + selectedDay, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      if (response.ok) {
        let data = await response.json();
        const hourlyCountPlot = {}
        const hourlyCountPlot_data = [
          {
            x : data.hourly_sorted,
            y : data["Upper Bound"],
            name: 'Upper Bound',
            mode: 'lines+markers',
            line: {
              dash: 'dot'
            }
          },
          {
            x : data.hourly_sorted,
            y : data["Mean"],
            name: 'Mean',
            mode: 'lines+markers',
            line: {
              dash: 'line'
            }
          },
          {
            x : data.hourly_sorted,
            y : data["Lower Bound"],
            name: 'Lower Bound',
            mode: 'lines+markers',
            line: {
              dash: 'dot'
            }
          }
          
        ]
        const hourlyCountPlot_layout = {
          // title:'Hourly Arrival Comparision', 
          xaxis: {
            title: 'Hour of day',
            showline: true,
            showgrid: true,
            showticklabels: true,
            tickvals: data.hourly_sorted,
            tickangle: 0

          },
          yaxis: {
            title: 'Arrivals' 
          },
          legend: {
            orientation: 'h',
            x: 0.5, // X position 0 (left) to 1 (right)
            y: 1.1, // Y position 0 (bottom) to 1 (top)
            xanchor: 'center',
            yanchor: 'bottom',
          },
          margin: {
            l: 50, // left margin
            r: 50, // right margin
            b: 50, // bottom margin
            t: 50, // top margin
            pad: 4
          },
        }
        hourlyCountPlot.data = hourlyCountPlot_data
        hourlyCountPlot.layout = hourlyCountPlot_layout;
        setHourlyCount(hourlyCountPlot);
      }

    } catch (error){
      console.error('Error fetching  hourly counts data: ', error);
    }
  },[]);

  const fetchWaitingTimeData = useCallback(async (selectedDay) => {
    try {
      const response = await fetch(baseUrl + "waiting_times?day=" + selectedDay, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
  
      if (response.ok) {
        let data = await response.json();
  
        // Convert seconds to decimal minutes
        const convertToMinutes = (seconds) => seconds / 60;
  
        // Convert waiting times to minutes
        const avgWaitingTimesInMinutes = data.average_cycle_times.map(convertToMinutes);
        const maxWaitingTimesInMinutes = data.max_cycle_times.map(convertToMinutes);
  
        const waitingTimePlot = {};
        const waitingTimePlot_data = [
          {
            x: data.hours,
            y: avgWaitingTimesInMinutes, // Use converted values
            name: 'Average Waiting Time',
            mode: 'lines+markers',
            line: {
              dash: 'solid',
            },
          },
          {
            x: data.hours,
            y: maxWaitingTimesInMinutes, // Use converted values
            name: 'Maximum Waiting Time',
            mode: 'lines+markers',
            line: {
              dash: 'dot',
            },
          },
        ];
  
        const waitingTimePlot_layout = {
          xaxis: {
            title: 'Hour of day',
            showline: true,
            showgrid: true,
            showticklabels: true,
            tickvals: data.hours,
            tickangle: 0,
          },
          yaxis: {
            title: 'Waiting Time (Minutes)', 
          },
          legend: {
            orientation: 'h',
            x: 0.5, // X position 0 (left) to 1 (right)
            y: 1.1, // Y position 0 (bottom) to 1 (top)
            xanchor: 'center',
            yanchor: 'bottom',
          },
          margin: {
            l: 50, // left margin
            r: 50, // right margin
            b: 50, // bottom margin
            t: 50, // top margin
            pad: 4,
          },
        };
  
        waitingTimePlot.data = waitingTimePlot_data;
        waitingTimePlot.layout = waitingTimePlot_layout;
  
        setWaitingTime(waitingTimePlot);
      }
    } catch (err) {
      console.log("Fetch Error :-S", err);
    }
  }, []);
  

  const fetchMaximumQueueData = useCallback(async(selectedDay) => {
    try{
      const response = await fetch(baseUrl + "max_queue_length?day="+selectedDay, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      if (response.ok) {
        let queueData = await response.json();

        const maxQueuePlot = {}
        const maxQueuePlot_data = [
          {
            x: Object.keys(queueData.most_likely), // Extract keys for x-axis
            y: Object.values(queueData.most_likely), // Extract values for y-axis
            name: 'Most Likely',
            type: 'bar', // Bar plot type
            marker: {
              color: 'rgb(255, 127, 80)' // Orange for most likely
            }
          },
          {
            x: Object.keys(queueData.optimistic),
            y: Object.values(queueData.optimistic),
            name: 'Optimistic',
            type: 'bar',
            marker: {
              color: 'rgb(144, 238, 144)' // Green for optimistic
            }
          },
          {
            x: Object.keys(queueData.pessimistic),
            y: Object.values(queueData.pessimistic),
            name: 'Pessimistic',
            type: 'bar',
            marker: {
              color: 'red' // Red for pessimistic
            }
          }
        ]
        const maxQueuePlot_layout = {
          // title:'Comparision of Maximum Queue Length by Hours Accross Environment', 
          xaxis: {
            title: 'Hour of day',
            showticklabels: true,
            tickvals: Object.keys(queueData.pessimistic),
            tickangle: -45

          },
          yaxis: {
            title: 'Maximum Queue Length' 
          },
          barmode: 'group',
          legend: {
            orientation: 'h',
            x: 0.5, // X position 0 (left) to 1 (right)
            y: 1.1, // Y position 0 (bottom) to 1 (top)
            xanchor: 'center',
            yanchor: 'bottom',
          },
          margin: {
            l: 50, // left margin
            r: 50, // right margin
            b: 50, // bottom margin
            t: 50, // top margin
            pad: 4
          },
        }
        maxQueuePlot.data = maxQueuePlot_data
        maxQueuePlot.layout = maxQueuePlot_layout
        setMaxQueueData(maxQueuePlot)
      }
    } catch  (error) {
      console.log('Error', error) 
    }
  },[]);

  const fetchSectionCounts = useCallback(async(vehicleType, selectedDay) => {
    try{
      console.log(baseUrl + "section_counts_stats?vehicle="+vehicleType+"&day="+selectedDay)
      const response = await fetch(baseUrl + "section_counts_stats?vehicle="+vehicleType, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      if (response.ok) {
        const sectionCountsData = await response.json();
        sectionCountsData.push({
          "Mean Count": 0,
          "Section ID": "8",
          "Section Name": "ABI road"
        })
        sectionCountsData.push({
          "Mean Count": 0,
          "Section ID": "9",
          "Section Name": "Transit A Area"
        })

        const filteredSections = sectionCountsData.filter(
          (section) => section["Section ID"] === "1" || section["Section ID"] === "4" || section["Section ID"] === "5" || section["Section ID"] === "9"
        );
  
        // Rename the sections
        const renamedSections = filteredSections.map((section) => {
          if (section["Section ID"] === "1") {
            section["Section Name"] = "Ocean Dock Drive (Section 1 to 3)";
          } else if (section["Section ID"] === "4") {
            section["Section Name"] = "Terminal Rd (Sections 5 and 6)";
          } else if (section["Section ID"] === "5") {
            section["Section Name"] = "Anchorage Port Rd (Sections 4, 7, and 8)"; 
          } else if (section["Section ID"] === "9") {
            section["Section Name"] = "Marathon and Transit Area (Sections 9)"; 
          }
          return section;
        });
        setSectionCount(renamedSections)
        
      }
    }catch (err){
      console.log("Fetch Section Error", err)
    }
  },[]);
  const fetchWeeklyCounts = useCallback(async(vehicleType, selectedDay) => {
    try {
      const response = await fetch(baseUrl + "weekly_counts?vehicle="+vehicleType+'&day='+selectedDay, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      if (response.ok) {
        const weeklyCountData = await response.json();
        const weeklyCountPlot = {}
        const weeklyCountPlot_data = [
          {
            mean:10,
            sd:2,
            name: "Monday",
            type:'box',
            showwhiskers:false,
            sizemode:"sd"
          },
          {
             // Dummy x-axis values (will be overridden)
            mean:10,
            sd:2,
            type: 'box',
            mode: 'box', // Set mode to 'boxes' for box plot
            fillcolor: 'rgb(0, 144, 255)', // Set box fill colo
            name: "Tuesday" ,
            sizemode:"sd"
            
          }
        ]
        const weeklyCountPlot_layout = {
          // title:'Expected Truck Arrivals by Day of Week',
          xaxis: {
            title: 'Day of Week',
            showticklabels: true,
            tickangle: 0

          },
          yaxis: {
            title: 'Number of Arrivals' 
          },
          legend: {
            orientation: 'h',
            x: 0.5, // X position 0 (left) to 1 (right)
            y: 1.1, // Y position 0 (bottom) to 1 (top)
            xanchor: 'center',
            yanchor: 'bottom',
          },
          margin: {
            l: 50, // left margin
            r: 50, // right margin
            b: 50, // bottom margin
            t: 50, // top margin
            pad: 4
          },
        }
        weeklyCountPlot.data = weeklyCountPlot_data
        weeklyCountPlot.layout = weeklyCountPlot_layout
        setWeeklyCount(weeklyCountPlot);
      }

    }catch (error){
      console.error("Error while fetching Weekly Counts", error)
    }
  },[]);

  const fetchMonthCorrelation = useCallback( async (selectedDay) => {
    try {
      
      const response = await fetch(baseUrl + "correlation?type=months&day="+selectedDay, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      if (response.ok) {
        const monthlyCountsData = await response.json();
        const months = Object.keys(monthlyCountsData);
        const monthData = [];
        const monthLabels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

        // Loop through months in the desired order
        for (const month of monthLabels) {
          const monthValues = [];
          // Check if data exists for the current month
          if (monthlyCountsData.hasOwnProperty(month)) {
            for (const otherMonth of monthLabels) {
              // Extract correlation value for the current month with other months
              const correlationValue = monthlyCountsData[month][otherMonth];
              monthValues.push(correlationValue);
            }
          } else {
            // Handle missing month data (optional)
            console.warn(`Data missing for month: ${month}`);
            monthValues.push(...Array(monthLabels.length).fill(null)); // Fill with null values
          }
          monthData.push(monthValues);
        }

        const heatmapData = [
          {
            z: monthData,
            type: 'heatmap',
            colorscale: 'Viridis', // Adjust colorscale as needed
          },
        ];

        const heatmapLayout = {
          xaxis: {
            title: 'Months',
            ticktext: monthLabels, // Set custom tick labels for months
            tickvals: Array.from({ length: monthLabels.length }, (_, i) => i), // Set tick positions
          },
          yaxis: {
            title: 'Months',
            ticktext: monthLabels, // Set custom tick labels for months
            tickvals: Array.from({ length: monthLabels.length }, (_, i) => i), // Set tick positions
          },
        };

        const monthCorrelationData = {}
        monthCorrelationData.data = heatmapData 
        monthCorrelationData.layout = heatmapLayout

        setMonthCorrelation(monthCorrelationData)

      }

    }catch (error){
      console.error("Error while fetching Monthly Correlation", error)
    }
  },[])

  const fetchWeekCorrelation = useCallback(async (selectedDay) => {
    try {
      const response = await fetch(baseUrl + "correlation?type=weeks&day="+selectedDay, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      if (response.ok) {
        const weeklyCountsData = await response.json();
        console.log(weeklyCountsData)
        const weekDays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
        const weekData = [];
  
        // Loop through weekdays in the desired order
        for (const day of weekDays) {
          const dayValues = [];
          // Check if data exists for the current day
          if (weeklyCountsData.hasOwnProperty(day)) {
            for (const otherDay of weekDays) {
              // Extract correlation value for the current day with other days
              const correlationValue = weeklyCountsData[day][otherDay];
              dayValues.push(correlationValue);
            }
          } else {
            // Handle missing day data (optional)
            console.warn(`Data missing for day: ${day}`);
            dayValues.push(...Array(weekDays.length).fill(null)); // Fill with null values
          }
          weekData.push(dayValues);
        }
  
        const heatmapData = [
          {
            z: weekData,
            type: 'heatmap',
            colorscale: 'Viridis', // Adjust colorscale as needed
          },
        ];
  
        const heatmapLayout = {
          xaxis: {
            title: 'Day Of Week',
            ticktext: weekDays, // Set custom tick labels for weekdays
            tickvals: Array.from({ length: weekDays.length }, (_, i) => i), // Set tick positions
          },
          yaxis: {
            title: 'Day Of Week',
            ticktext: weekDays, // Set custom tick labels for weekdays
            tickvals: Array.from({ length: weekDays.length }, (_, i) => i), // Set tick positions
          },
        };
  
        const weekCorrelationData = {};
        weekCorrelationData.data = heatmapData;
        weekCorrelationData.layout = heatmapLayout;
  
        setWeekCorrelation(weekCorrelationData); // Assuming you have a state for weekly data
  
      }
    } catch (error) {
      console.error("Error while fetching Weekly Correlation", error);
    }
  }, []);
  



  useEffect(() => {
    
    fetchCycleTimeData(selectedDay); 
    fetchHourlyCountsData(vehicleType, selectedDay);
    fetchWaitingTimeData(selectedDay);
    fetchMaximumQueueData(selectedDay);
    fetchSectionCounts(vehicleType, selectedDay);
    fetchWeeklyCounts(vehicleType, selectedDay);
    fetchMonthCorrelation(selectedDay);
    fetchWeekCorrelation(selectedDay);
  }, []); 



  return (
    <div className="dashboards-container">
      {/* First column */}
      <div className="dashboard-column first-column">
        <h3 class="h3-db">Cycle Times
        <a data-tooltip-id="cycle-tooltip" data-tooltip-content="Shows the average and maximum cycle times for vehicles arriving at the port, segmented by the hour of the day to help understand landside operation efficiency. Cycle Time is defined as the total time taken by a vehicle (e.g., a truck) from entering the port to leaving the port." className="tooltip-circle">
              ?
            </a>
            <Tooltip id="cycle-tooltip" className="custom-tooltip" />
          </h3>
        <Plot data={cycleTime.data} layout={cycleTime.layout} />
  
        <h3 class="h3-db">Hourly Arrival
          <a data-tooltip-id="aboutTipHourlyArrival" data-tooltip-content="Displays the number of arrivals each hour, along with upper and lower bounds, providing insights into peak and off-peak times for vehicle arrivals. Upper and Lower Bounds represent the highest and lowest limits of an expected range, such as the number of vehicles arriving at the port within a specific timeframe."
             className="tooltip-circle">?</a>
          <Tooltip id="aboutTipHourlyArrival" place="top" effect="solid" className="custom-tooltip" />
        </h3>
        <Plot data={hourlyCount.data} layout={hourlyCount.layout} />
  
        <h3 class="h3-db">Waiting Times
          <a data-tooltip-id="aboutTipWaitingTimes" data-tooltip-content="Monitors the average and maximum waiting times for vehicles throughout the day, assisting in identifying any delays or inefficiencies in landside operations. Waiting Times are defined as the amount of time a vehicle spends waiting at the port before it can proceed with its journey."
             className="tooltip-circle">?</a>
          <Tooltip id="aboutTipWaitingTimes" place="top" effect="solid" className="custom-tooltip"/>
        </h3>
        <Plot data={waitingTime.data} layout={waitingTime.layout} />
      </div>
  
      {/* Second column */}
      <div className="dashboard-column second-column">
        <h3 class="h3-db">Filter Vehicle Type
          <a data-tooltip-id="aboutTipVehicleType" data-tooltip-content="Allows users to filter the data displayed based on vehicle type (cars or trucks) for more detailed analysis."
             className="tooltip-circle">?</a>
          <Tooltip id="aboutTipVehicleType" place="top" effect="solid" className="custom-tooltip"/>
        </h3>
        <div style={{ display: 'flex', gap: '20px', paddingBottom: '20px', paddingLeft: '280px', paddingTop: '20px', backgroundColor: 'white', padding: '10px', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <label style={{ fontWeight: 'bold' }}>
            <input type="radio" id="cars" name="vehicleType" value="cars" style={{ marginRight: '5px' }} checked={vehicleType === 'cars'} onChange={handleVehicleTypeChange} />
            Cars
          </label>
          <label style={{ fontWeight: 'bold' }}>
            <input type="radio" id="trucks" name="vehicleType" value="trucks" style={{ marginRight: '5px' }} checked={vehicleType === 'trucks'} onChange={handleVehicleTypeChange} />
            Trucks
          </label>
        </div>
  
        <h3 class="h3-db">Select Day</h3>
        <div style={{ display: 'flex', gap: '20px', paddingBottom: '20px', paddingLeft: '280px', paddingTop: '20px', backgroundColor: 'white', padding: '10px', borderRadius: '5px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <select value={selectedDay} onChange={handleDayChange}>
            {dayOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
  
        <div>
          <DashboardMapComponent />
        </div>
  
        <h3 class="h3-db">Expected Vehicles in Each Route
          <a data-tooltip-id="aboutTipVehiclesSection" data-tooltip-content="Table listing various sections of the port and the mean count of expected vehicles in each area, giving a detailed view of traffic distribution."
             className="tooltip-circle">?</a>
          <Tooltip id="aboutTipVehiclesSection" place="top" effect="solid" className="custom-tooltip"/>
        </h3>
        <div>
          <table>
            <thead>
              <tr>
                <th>Section Name</th>
                <th>Mean Count</th>
              </tr>
            </thead>
            <tbody>
              {sectionCount && sectionCount.length > 0 ? (
                sectionCount.map((section) => (
                  <tr key={section["Section ID"]}>
                    <td>{section["Section Name"]}</td>
                    <td>{section["Mean Count"]}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="3">Data still not available</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
  
      {/* Third column */}
      <div className="dashboard-column third-column">
        <h3 class="h3-db">Maximum Hazmat Queue Length
          <a data-tooltip-id="aboutTipQueueLength" data-tooltip-content="A bar chart that displays the maximum expected queue length at Hazmat Lane, categorized by the hour, with projections for different scenarios: most likely, optimistic, and pessimistic."
             className="tooltip-circle">?</a>
          <Tooltip id="aboutTipQueueLength" place="top" effect="solid" className="custom-tooltip"/>
        </h3>
        <Plot data={maxQueueData.data} layout={maxQueueData.layout} />
  
        <h3 class="h3-db">Correlation by Months
          <a data-tooltip-id="aboutTipCorrelationMonths" data-tooltip-content="Heatmap illustrating the correlation between the arrivals of different months of the year, helping to identify seasonal trends or patterns."
             className="tooltip-circle">?</a>
          <Tooltip id="aboutTipCorrelationMonths" place="top" effect="solid" className="custom-tooltip"/>
        </h3>
        <Plot data={monthCorrelation.data} layout={monthCorrelation.layout} />
  
        <h3 class="h3-db">Correlation by Weekdays
          <a data-tooltip-id="aboutTipCorrelationWeekdays" data-tooltip-content="Heatmap that shows correlations between the arrivals across different weekdays, allowing for the identification of weekly patterns."
             className="tooltip-circle">?</a>
          <Tooltip id="aboutTipCorrelationWeekdays" place="top" effect="solid"  className="custom-tooltip"/>
        </h3>
        <Plot data={weekCorrelation.data} layout={weekCorrelation.layout} />
      </div>
    </div>
  );
  
}

export default Dashboards;
