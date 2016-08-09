fsm
	.state("empty")
		.on("change:locations").to("show")	
		.on("blur").to("notactive")	
	.state("show")
		.enter(updateLocation,runTimer)	
		.on("change:locations").exec(updateLocations)
								  .ifVal(0).to("empty")
		.on("blue").to("notactive")
		.on("ontimer").exec(requests.runNewLocationsQuery)
		.on("change:newLocations").exec(updateLocationsByNew)
		.on("onrecent").exec($query.val,requests.runLocationQuery)
		.on("onlocation").exec(
		.exit(stopTimer)			
	.state("notactive")
		.on("focus").exec(locationsIsEmpty)
					  .ifVal(true).to("empty")
					  .ifVal(false).to("show")


 .on("click",fsm.onlocation)