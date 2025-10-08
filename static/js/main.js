function scanQR(event_id) {
    let scanner = new Instascan.Scanner({ video: document.getElementById('preview') });
    
    scanner.addListener('scan', function(content) {
        console.log("QR scanned:", content);

        if(content === "event_id:" + event_id) {
            if(navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(pos) {
                    fetch("/mark_attendance/" + event_id, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ lat: pos.coords.latitude, lon: pos.coords.longitude })
                    })
                    .then(res => res.json())
                    .then(data => {
                        alert(data.message);
                        // After marking attendance, redirect to feedback form
                        window.location.href = "/feedback/" + event_id;
                    })
                    .catch(err => console.error(err));
                });
            } else {
                alert("Geolocation not supported in your browser!");
            }
        } else {
            alert("Invalid QR code!");
        }
    });

    Instascan.Camera.getCameras().then(function(cameras) {
        if(cameras.length > 0) {
            scanner.start(cameras[0]);
        } else {
            alert("No cameras found.");
        }
    }).catch(e => console.error(e));
}
