import React, { useState, useEffect } from 'react';
import './ScenarioAnalysis.css';
import ReactPlayer from 'react-player';
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos';
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';
import CircularProgress from '@mui/material/CircularProgress';
import Plot from 'react-plotly.js';
import { Tooltip } from 'react-tooltip';

function ScenarioAnalysis() {
  const [parameters, setParameters] = useState({
    disruptionLocation: '',
    inOutRoute: '',
    disruptionLength: '',
    disruptionTimeDate: '',
    startDate: '',
    endDate: '',
    blockLocation: '',
    routeDistribution: 0.0,
  });


  const [scenarioType, setScenarioType] = useState('shortTerm');
  const [showShortTermInputs, setShowShortTermInputs] = useState(true);
  const [showLongTermInputs, setShowLongTermInputs] = useState(false);
  const [isRunDisabled, setIsRunDisabled] = useState(true);
  const [suggestions, setSuggestions] = useState('');
  const [videoUrl, setVideoUrl] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [filteredRoutes, setFilteredRoutes] = useState([]);
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hasData, setHasData] = useState(false);

  const [plots, setPlots] = useState([]);
  const [currentPlotIndex, setCurrentPlotIndex] = useState(0);
  let baseUrl = process.env.REACT_APP_BACKEND_SERVER_URL;

  

  const validateFields = () => {
    if (scenarioType === 'shortTerm') {
      const { disruptionLocation, inOutRoute, disruptionLength, disruptionTimeDate } = parameters;
      
      setIsRunDisabled(
        !disruptionLocation || !inOutRoute || !disruptionLength || !disruptionTimeDate
      );
    } else {
      const { startDate, endDate, blockLocation, routeDistribution } = parameters;
      setIsRunDisabled(!startDate || !endDate || !blockLocation || !routeDistribution);
    }
  };

  useEffect(() => {
    validateFields();
  }, [parameters, scenarioType]);

  const sectionNamesMap = {
    'Section 1': 'Section 1 - Ocean Dock Rd before turn into Marathon Terminal',
    'Section 2': 'Section 2 - Ocean Dock Rd between turn into Marathon Terminal and turn into ABl',
    'Section 3': 'Section 3 - Between turn into ABl and turn onto Roger Graves Rd',
    'Section 4': 'Section 4 - Occurs along Anchorage Port Rd before turn onto Terminal Rd',
    'Section 5': 'Section 5 - Start of Terminal Rd, opposite the Control Center',
    'Section 6': 'Section 6 - Terminal Rd to the entrance of Tote yard',
    'Section 7': 'Section 7 - Anchorage Rd across from Petro Star and AFSC',
    'Section 8': 'Section 8 - Anchorage Rd from across Delta Western to across Matson yard',
    //'Section 9': 'Section 9 - Marathon Rd and south float access towards Matson yard',
  }


  const inOutRouteMap = {
    'Section 1': ['Insulfoam-Insulfoam', 
      'Insulfoam-Military', 
      'Military-Insulfoam', 
      'Military-Military'],
    'Section 2': [
      'Marathon-Military',
      'Marathon-Marathon',
      'Military-Marathon',
      'Military-Military',
      'Bluff-Marathon',
      'Marathon-Bluff',
      'Bluff-Military',
      'Military-Bluff',
      'Bluff-Bluff',
      'Marathon Transit Area Hybrid-Marathon Transit Area Hybrid',
    ],
    'Section 3': ['Marathon Transit Area Hybrid-Marathon Transit Area Hybrid', 
      'Marathon Transit Area Hybrid-Military', 
      'Military-Marathon Transit Area Hybrid', 
      'Military-Military'],
    'Section 4': ['ABI-Roger', 
      'Roger-ABI', 
      'ABI-ABI', 
      'Roger-Roger', 
      'ABI-Military', 
      'Military-ABI',
      'Military-Military', 
      'Marathon Transit Area Hybrid-Marathon Transit Area Hybrid'],
    'Section 5': ['Military-Military', 
      'Roger-Military', 
      'Military-Roger'],
    'Section 6': [
       'Transit-Transit',
       'Military-Military'],
    'Section 7': ['Marathon Transit Area Hybrid-Military', 
      'Marathon Transit Area Hybrid-Marathon Transit Area Hybrid', 
      'Military-Marathon Transit Area Hybrid', 
      'Military-Military', 
      'Tidewater-Tidewater', 
      'PertoStar-Tidewater', 
      'Tidewater-PertoStar'],
    'Section 8': ['Tidewater-Tidewater',
      'Marathon Transit Area Hybrid-Military',
      'Marathon Transit Area Hybrid-Marathon Transit Area Hybrid',
      'Military-Marathon Transit Area Hybrid',
      'Military-Military'],
    //'Section 9': ['Main Route-Main Route'],
  };

  // New: Fetch Risk Section Data
  const fetchRiskSectionData = async (section) => {
    const response = await fetch(baseUrl + `/riskSection?section=${section}`);
    return response.json();
  };

  // New: Fetch Risk Route Data
  const fetchRiskRouteData = async (inroute, outroute) => {
    const response = await fetch(baseUrl + `/riskRoute?inroute=${inroute}&outroute=${outroute}`);
    return response.json();
  };

  // New: Render Section Plot
  const renderSectionPlot = (data, selectedSection) => {
    const {
      "Alternative Route Diversity": diversity,
      "Alternative Route Efficacy": efficacy,
      "Amount of Traffic Impacted": traffic,
      "Overall Risk Level": risk,
      "Disruption Location": locations,
    } = data;

    setPlots((prevPlots) => [
      ...prevPlots,
      {
        data: [
          {
            x: locations,
            y: efficacy,
            type: 'bar',
            name: 'Alternative Route Efficacy',
            marker: {
              color: locations.map((loc) => (loc === selectedSection ? 'orange' : '#03DAC5')),
            },
          },
          {
            x: locations,
            y: diversity,
            type: 'bar',
            name: 'Alternative Route Diversity',
            marker: {
              color: locations.map((loc) => (loc === selectedSection ? 'orange' : '#CC7E85')),
            },
          },
          {
            x: locations,
            y: traffic,
            type: 'bar',
            name: 'Amount of Traffic Impacted',
            marker: {
              color: locations.map((loc) => (loc === selectedSection ? 'orange' : '#E8DBC5')),
            },
          },
          {
            x: locations,
            y: risk,
            type: 'bar',
            name: 'Overall Risk Level',
            marker: {
              color: locations.map((loc) => (loc === selectedSection ? 'orange' : '#93B7BE')),
            },
          },
        ],
        layout: { title: `Section Analysis: ${selectedSection}`, barmode: 'group' },
      },
    ]);
  };

  // New: Render Route Plot
  const renderRoutePlot = (data, inroute, outroute) => {
    const { "Alternative Route": routes, "Ease of Implementation": ease, "Overall Efficacy": efficacy, "Relative Performance": performance, "Route Diversity": diversity } = data;

    setPlots((prevPlots) => [
      ...prevPlots,
      {
        data: [
          {
            x: routes,
            y: ease,
            type: 'bar',
            name: 'Ease of Implementation',
            marker: {
              color: routes.map((route) => (route === inroute ? 'green' : route === outroute ? 'red' : '#03DAC5')),
            },
          },
          {
            x: routes,
            y: efficacy,
            type: 'bar',
            name: 'Overall Efficacy',
            marker: {
              color: routes.map((route) => (route === inroute ? 'green' : route === outroute ? 'red' : '#CC7E85')),
            },
          },
          {
            x: routes,
            y: performance,
            type: 'bar',
            name: 'Relative Performance',
            marker: {
              color: routes.map((route) => (route === inroute ? 'green' : route === outroute ? 'red' : '#E8DBC5')),
            },
          },
          {
            x: routes,
            y: diversity,
            type: 'bar',
            name: 'Route Diversity',
            marker: {
              color: routes.map((route) => (route === inroute ? 'green' : route === outroute ? 'red' : '#93B7BE')),
            },
          },
        ],
        layout: { title: `Route Analysis: ${inroute} to ${outroute}`, barmode: 'group' },
      },
    ]);
  };


  useEffect(() => {
    const selectedLocation = parameters.disruptionLocation;
    if (selectedLocation && inOutRouteMap.hasOwnProperty(selectedLocation)) {
      setFilteredRoutes(inOutRouteMap[selectedLocation]);
    } else {
      setFilteredRoutes([]); // Clear options if location is invalid or not matched
    }
  }, [parameters.disruptionLocation]);

  // Function to render the table
  const renderTable = () => {
    if (data && data.length > 0) {
      const headers = Object.keys(data[0]).map(header => header.replace(/ - /g, '<br>'));
      const excludedColumns = ['Route']
      const rows = data.map((item) => {
        return Object.keys(item).map((key) => {
          // Convert values to minutes unless the column is excluded
          if (!excludedColumns.includes(key)) {
            return (item[key] / 60).toFixed(2); // Convert seconds to minutes and format to 2 decimals
          }
          return item[key]; // Keep excluded columns unchanged
        });
      });

      return (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                {headers.map((header, index) => (
                  <th key={index} dangerouslySetInnerHTML={{ __html: header }}></th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.length > 0 ? (
                rows.map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {row.map((cell, cellIndex) => (
                      <td key={cellIndex}>{cell}</td>
                    ))}
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={headers.length}>No data available</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      );
    } else {
      return <div>No data to display.</div>;
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;

    if (name === 'endDate' && parameters.startDate) {
      const startDate = new Date(parameters.startDate);
      const endDate = new Date(value);
      if (endDate <= startDate) {
        alert('End date must be greater than start date.');
        return;
      }
    }

    if (name === 'routeDistribution') {
      setParameters((prevParams) => ({
        ...prevParams,
        routeDistribution: parseFloat(value), // Convert to float
      }));
    } else {
      setParameters((prevParams) => ({
        ...prevParams,
        [name]: value,
      }));
    }
  };

  const handlePrevPlot = () => {
    setCurrentPlotIndex((prevIndex) => (prevIndex > 0 ? prevIndex - 1 : plots.length - 1)); // Updated
  };

  const handleNextPlot = () => {
    setCurrentPlotIndex((prevIndex) => (prevIndex + 1) % plots.length); // Updated
  };

  async function fetchData(scenario) {
    let baseUrl = process.env.REACT_APP_BACKEND_SERVER_URL;
    let type = ''
    if(scenario === 'shortTerm'){
      type = 'short'
    }else if (scenario === 'longTerm'){
      type = 'long'
    }
    const response = await fetch(baseUrl + '/scenario_analysis/plots_suggestions?type='+type, {
      method: 'GET',
    });

    if (response.status === 200) {
      const jsonData = await response.json();
      return jsonData;
    } else {
      console.error('Error fetching data:', response.statusText);
      return null;
    }
  }

  const prepareBoxPlotData = (data) => {
    return Object.keys(data).map((key) => ({
      y: data[key],
      type: 'box',
      name: `${key}`,
    }));
  };

  const prepareLinePlotData = (data) => {
    return Object.keys(data).map((key) => ({
      x: Array.from({ length: data[key].length }, (_, index) => index),
      y: data[key],
      type: 'scatter',
      mode: 'lines+markers',
      name: `${key}`,
    }));
  };

  const handleRunScenario = async () => {

    if (isRunDisabled) {
      alert('Please fill out all required fields.');
      return;
    }

    setIsLoading(true);
    setHasData(false);
    setData(null);
    setPlots([]); 

    const baseUrl = process.env.REACT_APP_BACKEND_SERVER_URL;
    const apiUrl = baseUrl + '/scenario_analysis';
    const beVideoUrl = baseUrl + '/videoUrls';

    const disruptionDateTime = new Date(parameters.disruptionTimeDate);
    const disruptionLength = parameters.disruptionLength;
    const disruptionLocation = parameters.disruptionLocation;
    const inOutRoute = parameters.inOutRoute;
    const month = disruptionDateTime.toLocaleString('en-US', { month: 'short' });
    const dayOfWeek = getNumericDayOfWeek(disruptionDateTime.toLocaleString('en-US', { weekday: 'short' }));
    const hour = disruptionDateTime.getHours();

    function getNumericDayOfWeek(shortDay) {
      const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
      const index = daysOfWeek.indexOf(shortDay);
      return index !== -1 ? (index + 1).toString() : '';
    }

    const scenarioType = document.querySelector('input[name="scenarioType"]:checked').value;
    let video_url_before = '';
    let video_url_after = '';
    let videoRequestBody = {
      analysis_type: scenarioType,
    };
    if(scenarioType === "shortTerm"){
      videoRequestBody.disruption_location = disruptionLocation;
      videoRequestBody.inOutRoute = inOutRoute;
    } else if (scenarioType === "longTerm"){
      videoRequestBody.disruption_location = parameters.blockLocation
    }

    try {
      const videoResponse = await fetch(beVideoUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(videoRequestBody),
      });

      if (videoResponse.status === 200) {
        const videoData = await videoResponse.json();
        video_url_before = videoData.video_url_before;
        video_url_after = videoData.video_url_after;

        setVideoUrl(video_url_before);
        setIsPlaying(true);
      }
    } catch (error) {
      console.error('Video API request failed with status:', error);
    }

    const requestBody = {};

    

    if (scenarioType === 'shortTerm') {
      requestBody.disruption_length = disruptionLength;
      requestBody.disruption_location = disruptionLocation;
      requestBody.inOutRoute = inOutRoute;
      requestBody.date_hour = disruptionDateTime;
      requestBody.month = month;
      requestBody.day = dayOfWeek;
      requestBody.hour = hour;
    } else {
      requestBody.start_date = parameters.startDate;
      requestBody.end_date = parameters.endDate;
      requestBody.block_location = parameters.blockLocation;
      requestBody.route_distribution = [parameters.routeDistribution, 1 - parameters.routeDistribution];
    }
    requestBody.analysis_type = scenarioType;
    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (response.status === 200) {
        setHasData(true);
        setIsLoading(false);

        const baseUrl2 = process.env.REACT_APP_BACKEND_SERVER_URL + '/files/';
        

        const scenarioData = await fetchData(scenarioType);
        if (scenarioData) {
          //console.log(scenarioData);
          setData(scenarioData.simulation_results);

          if (scenarioType === 'shortTerm') {
            const cyclePlot = {
              data: prepareBoxPlotData(Object.fromEntries(
                Object.entries(scenarioData.cycle_data).map(([key, values]) => [
                  key,
                  values.map((value) => value / 60), // Convert seconds to minutes
                ])
              )
            ),
              layout: { title: 'Cycle Time Box Plot', boxmode: 'group',
                yaxis: {
                  title: 'Cycle Time (Minutes)', 
                },
              },
            };

            const waitPlot = {
              data: prepareBoxPlotData(Object.fromEntries(
                Object.entries(scenarioData.waiting_data).map(([key, values]) => [
                  key,
                  values.map((value) => value / 60), // Convert seconds to minutes
                ])
              )
            ),
              layout: { title: 'Wait Time Box Plot', boxmode: 'group',
                yaxis: {
                  title: 'Wait Time (Minutes)', 
                },
              },
            };



            setPlots([cyclePlot, waitPlot]);
            if(disruptionLocation){
              const sectionData = await fetchRiskSectionData(disruptionLocation);
              renderSectionPlot(sectionData, disruptionLocation);
            }

            
            if (inOutRoute) {
              const [inroute, outroute] = inOutRoute.split('-');
            const routeData = await fetchRiskRouteData(inroute, outroute);

              renderRoutePlot(routeData, inroute, outroute);
            }
            

          }
          else if (scenarioType === 'longTerm'){
            const cycleLinePlot = {
              data: prepareLinePlotData(scenarioData.average_cycle_times),
              layout: { title: 'Average Cycle Time Plot',

                yaxis: {
                  title: 'Cycle Time (Minutes)', 
                },
                xaxis: {
                  title: 'Hour of the day', 
                },
               },
            };
          
            const waitLinePlot = {
              data: prepareLinePlotData(scenarioData.average_waiting_times),
              layout: { title: 'Average Waiting Time Plot' ,
                yaxis: {
                  title: 'Wait Time (Seconds)', 
                },
                xaxis: {
                  title: 'Hour of the day', 
                },
              },
            };

            const hazmatWaitLinePlot = {
              data: prepareLinePlotData(scenarioData.hazmat_wait_times),
              layout: { title: 'Hazmat Waiting Time Plot' },
            }
          
            setPlots([cycleLinePlot, waitLinePlot, hazmatWaitLinePlot]);

          }

          setVideoUrl(video_url_after);
        } else {
          console.error('Failed to retrieve data for scenario:', scenarioType);
        }

        
      } else {
        console.error('API request failed with status:', response.status);
      }
    } catch (error) {
      console.error('Error while sending API request:', error);
    }
  };

  const handleScenarioTypeChange = (e) => {
    const newType = e.target.value;
    setScenarioType(newType);

    if (newType === 'shortTerm') {
      setShowShortTermInputs(true);
      setShowLongTermInputs(false);
    } else {
      setShowShortTermInputs(false);
      setShowLongTermInputs(true);
    }
  };

  const handleClear = () => {
    setParameters({
      disruptionLocation: '',
      disruptionLength: '',
      disruptionTimeDate: '',
      inOutRoute: '',
      startDate: '',
      endDate: '',
      blockLocation: '',
      routeDistribution: 0.0,
    });
    setScenarioType('shortTerm');
    setSuggestions('');
    setVideoUrl('');
    setPlots([]);
  };

  return (
    <div className="scenario-analysis-container">
      <div className="left-panel">
        {/* Radio Buttons for Scenario Type */}
        <div className="scenario-type-radio">
          <label>
            <input
              type="radio"
              name="scenarioType"
              value="shortTerm"
              checked={scenarioType === 'shortTerm'}
              onChange={handleScenarioTypeChange}
            />
            Short-term
          </label>
          <label>
            <input
              type="radio"
              name="scenarioType"
              value="longTerm"
              checked={scenarioType === 'longTerm'}
              onChange={handleScenarioTypeChange}
            />
            Long-term
          </label>
        </div>

        {/* Scenario Parameters */}
        <div className="scenario-parameters">
          <h3 className="sa-headers">Scenario Parameters</h3>

          {showShortTermInputs && (
            <div className="short-term-inputs">
              {/* Disruption Location */}
              <div className="parameter">
                <label htmlFor="disruptionLocation">Disruption Location:
                <a data-tooltip-id="aboutTipDL" data-tooltip-content="Select the location where the disruption is expected to occur."
                 className="tooltip-circle">?</a>
              <Tooltip id="aboutTipDL" place="top" effect="solid" className="custom-tooltip" />
            
                </label>
                <select id="disruptionLocation" name="disruptionLocation" onChange={handleInputChange}>
                  <option value="">Select</option>
                  {Object.keys(sectionNamesMap).map((section) => (
                    <option key={section} value={section}>
                      {sectionNamesMap[section]}
                    </option>
                  ))}
                </select>
              </div>

              {/* In - Out Route */}
              <div className="parameter">
                <label htmlFor="inIutRoute">EntryRoute - ExitRoute
                <a data-tooltip-id="aboutTipEE" data-tooltip-content="Choose the entry and exit routes affected by the disruption to simulate its impact on traffic and logistics."
                 className="tooltip-circle">?</a>
              <Tooltip id="aboutTipEE" place="top" effect="solid" className="custom-tooltip" />
            
                </label>
                <select id="inOutRoute" name="inOutRoute" onChange={handleInputChange}>
                  <option value="">Select</option>
                  {filteredRoutes.map((route) => (
                    <option key={route} value={route}>
                      {route}
                    </option>
                  ))}
                </select>
              </div>

              {/* Disruption Length */}
              <div className="parameter">
                <label htmlFor="disruptionLength">Disruption Length:
                <a data-tooltip-id="aboutTipDisruption" data-tooltip-content="Enter the exact date and time when the disruption is expected to start. This helps in scheduling and analysis."
                 className="tooltip-circle">?</a>
              <Tooltip id="aboutTipDisruption" place="top" effect="solid" className="custom-tooltip" />
            
                </label>
                <select id="disruptionLength" name="disruptionLength" onChange={handleInputChange}>
                  <option value="">Select</option>
                  <option value="short">Short (15 Min- 30 Min)</option>
                  <option value="medium">Medium (30 Min - 2 Hrs)</option>
                  <option value="long">Long (2 Hrs - 4 Hrs)</option>
                </select>
              </div>
              {/* Disruption Time & Date */}
              <div className="parameter">
                <label htmlFor="disruptionTimeDate">Disruption Time & Date:</label>
                <input type="datetime-local" id="disruptionTimeDate" name="disruptionTimeDate" onChange={handleInputChange} />
              </div>
            </div>
          )}

          {showLongTermInputs && (
            <div className="long-term-inputs">
              <div className="parameter">
                <label htmlFor="startDate">Start Date:</label>
                <input type="date" id="startDate" name="startDate" onChange={handleInputChange} />
              </div>
              <div className="parameter">
                <label htmlFor="endDate">End Date:</label>
                <input type="date" id="endDate" name="endDate" onChange={handleInputChange} />
              </div>
              <div className="parameter">
                <label htmlFor="blockLocation">Block Location:</label>
                <select id="blockLocation" name="blockLocation" onChange={handleInputChange}>
                  <option value="">Select</option>
                  <option value="Construction at Crossing Before Checkpoint">Construction at Crossing Before Checkpoint</option>
                  <option value="Construction at Ocean Dock Rd and Roger Graves Rd">Construction at Ocean Dock Rd and Roger Graves Rd</option>
                  <option value="Anchorage Port Rd">Anchorage Port Rd</option>
                  <option value="Terminal Rd">Terminal Rd</option>
                </select>
              </div>
              <div className="parameter">
                <label htmlFor="routeDistribution">Route Distribution:</label>
                <select id="routeDistribution" name="routeDistribution" onChange={handleInputChange}>
                  <option value="">Select</option>
                  <option value="0">0 , 1</option>
                  <option value="0.25">0.25 , 0.75</option>
                  <option value="0.5">0.5 , 0.5</option>
                  <option value="0.75">0.75 , 0.25</option>
                  <option value="1">1 , 0</option>
                </select>
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="action-buttons">
          <button className="run-button" disabled={isRunDisabled} onClick={handleRunScenario} >
            Run
          </button>
          <button className="stop-button">Stop</button>
          <button className="clear-button" onClick={handleClear}>Clear</button>
        </div>
      </div>
      <div className="center-panel">
        <div className="statistics-and-plots">
          <h3 className="sa-headers">Statistics and Plots
          <a data-tooltip-id="aboutTipSaP" data-tooltip-content="Once the simulation is run, this section will display relevant statistics and plots based on the analysis of the disruption."
                 className="tooltip-circle">?</a>
              <Tooltip id="aboutTipSaP" place="top" effect="solid" className="custom-tooltip" />
            
          </h3>
          {isLoading ? (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
              <CircularProgress size={100} />
            </div>
          ) : hasData ? (
            <div className="plot-container">
              <ArrowBackIosIcon className="arrow-icon left-arrow" onClick={handlePrevPlot} />
              <div className="plot-wrapper">
                {plots[currentPlotIndex] && (
                  <Plot data={plots[currentPlotIndex].data} layout={plots[currentPlotIndex].layout} />
                )}
              </div>
              <ArrowForwardIosIcon className="arrow-icon right-arrow" onClick={handleNextPlot} />
            </div>
          ) : (
            <div>Run scenario analysis to see the corresponding plots.</div>
          )}
        </div>

        <div className="sa-suggestions-box">
          <h3 className="sa-headers">Suggestions
          <a data-tooltip-id="aboutTipSuggestions" data-tooltip-content="After running the simulation, this section will provide the stats of other possible alternatives for the selected disruption."
                 className="tooltip-circle">?</a>
              <Tooltip id="aboutTipSuggestions" place="top" effect="solid" className="custom-tooltip" />
            
          </h3>
          <p>{suggestions}</p>
          {data ? renderTable() : <div>Run scenario analysis to see suggestions...</div>}
        </div>
      </div>
      {/* Video and Suggestions */}
      <div className="right-panel">
        {/* Video Container */}
        <div className="video-placeholder">
          {videoUrl ? (
            <ReactPlayer url={videoUrl} playing={isPlaying} loop controls width="100%" height="100%" />
          ) : (
            <video width="100%" height="100%" controls>
              <source src={videoUrl} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          )}
        </div>
      </div>
    </div>
  );
}

export default ScenarioAnalysis;
