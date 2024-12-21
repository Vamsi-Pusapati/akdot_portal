// /src/components/MapComponent/MapComponent.js
import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Fix for missing marker icons
let DefaultIcon = L.icon({
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

L.Marker.prototype.options.icon = DefaultIcon;

function LocationMarker({ onClick }) {
  useMapEvents({
    click(e) {
      onClick(e.latlng);
    },
  });

  return null;
}

function MapComponent() {
  // Center the map on Port of Anchorage
  const portAnchorageCoordinates = [61.2341, -149.8872]; // Latitude and Longitude of Port of Anchorage
  const [marker, setMarker] = useState();

  const handleMapClick = (latlng) => {
    console.log(latlng)
    setMarker(latlng);
  };

  return (
    <MapContainer
      center={portAnchorageCoordinates}
      zoom={14.5}
      style={{ height: '60vh', width: '100vh' }}
      scrollWheelZoom={false} 
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
        {
            marker && marker.lat && marker.lat && ( 
                <Marker position={marker}>
                    <Popup>
                        Coordinates: {marker.lat.toFixed(4)}, {marker.lng.toFixed(4)}
                    </Popup>
                </Marker>
            )
        }
      
      <LocationMarker onClick={handleMapClick} />
    </MapContainer>
  );
}

export default MapComponent;
