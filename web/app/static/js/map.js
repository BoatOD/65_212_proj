$(function() {
 
    $('#us2').locationpicker({
       location: {latitude: 18.804651199999999, longitude: 98.95501329999998},   
       radius: 0,
       inputBinding: {
          latitudeInput: $('#lat'),
          longitudeInput: $('#lng'),
          locationNameInput: $('#location')
       },
       enableAutocomplete: true,
       onchanged: function(currentLocation, radius, isMarkerDropped) {
          alert("Location changed. New location (" + currentLocation.latitude + ", " + currentLocation.longitude + ")");
        }
    });
    });
    