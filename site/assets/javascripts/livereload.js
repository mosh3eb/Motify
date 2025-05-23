(function() {
    var socket = new WebSocket('ws://localhost:35729/livereload');
    var lastReload = 0;

    socket.onmessage = function(event) {
        var data = JSON.parse(event.data);
        if (data.command === 'reload') {
            var now = Date.now();
            if (now - lastReload > 1000) {  // Prevent multiple reloads
                lastReload = now;
                window.location.reload();
            }
        }
    };

    socket.onclose = function() {
        console.log('LiveReload connection closed. Retrying in 1 second...');
        setTimeout(function() {
            window.location.reload();
        }, 1000);
    };
})(); 