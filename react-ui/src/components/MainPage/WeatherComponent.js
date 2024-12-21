import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { WiDaySunny, WiCloud, WiRain } from 'react-icons/wi';
import './WeatherComponent.css'; 

const WeatherComponent = () => {
  const [weatherData, setWeatherData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const apiKey = process.env.REACT_APP_WEATHER_API_KEY; 
    const lat = '61.217381'; 
    const lon = '-149.863129'; 
    const url = `https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/${lat},${lon}?unitGroup=us&key=${apiKey}&contentType=json`;

    const fetchWeather = async () => {
      try {
        const response = await axios.get(url);
        setWeatherData(response.data);
        setIsLoading(false);
      } catch (error) {
        setError(error);
        setIsLoading(false);
      }
    };

    fetchWeather();
  }, []);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  const { temp, humidity, windspeed } = weatherData.currentConditions;
  const [minTemp, maxTemp] = [weatherData.days[0].tempmin, weatherData.days[0].tempmax];
  
  const getWeatherIcon = (description) => {
    switch (description.toLowerCase()) {
      case 'clear':
      case 'sunny':
        return <WiDaySunny size={64} />;
      case 'cloudy':
      case 'overcast':
        return <WiCloud size={64} />;
      case 'rain':
      case 'showers':
        return <WiRain size={64} />;
      default:
        return <WiDaySunny size={64} />;
    }
  };

  return (
    <div className="weather-widget">
      {/* Left Section */}
      <div className="left-section">
        <div className="weather-city">Anchorage, AK, USA</div>
        <div className="weather-date">{new Date().toLocaleDateString('en-US', { weekday: 'long', day: 'numeric', month: 'long' })}</div>
      </div>

      {/* Middle Section */}
      <div className="middle-section">
        <div className="temp-icon">
          <div className="weather-temp">{temp}F</div>
          <div className="weather-icon">{getWeatherIcon(weatherData.description)}</div>
        </div>
        <div className="weather-range">Max: {maxTemp} F / Min: {minTemp} F</div>
      </div>

      {/* Right Section */}
      <div className="right-section">
        <div className="weather-condition">{weatherData.description}</div>
        <div className="weather-details">
          <div>Wind: {windspeed} MPH</div>
          <div>Humidity: {humidity}%</div>
        </div>
      </div>
    </div>
  );
};

export default WeatherComponent;
