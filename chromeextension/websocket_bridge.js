
// sleep function
V.sleep = function(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

V.createWebSocket = function(controller, url, canvas, width, height) {
	var BSON = bson().BSON;
	var ws = new WebSocket(url);
	ws.binaryType = "arraybuffer"; // alternative: "blob"
	var context = canvas.getContext("2d");

	
	// scaled canvas
	var outputCanvas = document.createElement("canvas");
	outputCanvas.width = width;
	outputCanvas.height = height;
	var outputContext = outputCanvas.getContext("2d");
	

	// finally ready (not before, and can cause error, as canvas is not ready yet)
	ws.onopen = function() {
		console.log('BotIO: Connected to Controller-Server.');
		ws.send(BSON.serialize({"state":"game_start", "width":width, "height":height, "numkeys":controller.numkeys, "channels": controller.numchannels}));
	}

	// reconnect (once per second)
	ws.onclose = function() {
		console.log('BotIO: Connection Closed!');
		setTimeout(createWebSocket, 1*1000, controller, url, canvas, width, height);
	}

	ws.onerror = function(error) {
		console.log('BotIO: OMG! WebSocket Error ' + error);
		console.log(error);
	}

	ws.onmessage = async function(e) {
		var msg;
		try {
			uint8Array  = new Uint8Array(e.data);
			msg = BSON.deserialize(uint8Array);
		}
		catch(err) {
			console.log('Failed to deserialize: ', err);
			return;
		}

		while(!controller.playing())
			await sleep(50);
			

		// apply control for last image
		used_keys = controller.applyKeys(msg.keys)
		
		// receive current score
		var current_score = controller.getScore();

		// send image (on request)
		outputContext.drawImage(canvas, 0, 0, width, height);
		var pixelArray = outputContext.getImageData(0,0, width, height).data;
		var pixellen = pixelArray.length;
		var byteArray = new Uint8Array(pixellen);
		for(var i=0; i<pixellen; i++)
			byteArray[i] = pixelArray[i];

		var response = {
			"state": "game_running",
			"score": current_score,
            "used_keys" : used_keys,
            "userinput" : controller.userinput
		};

		ws.send(BSON.serialize(response));
		ws.send(byteArray);
	}

}
