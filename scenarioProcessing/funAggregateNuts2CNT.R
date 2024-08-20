#
# Function to aggregate stocks or stock data to the country level from the NUTS3 level
# 
# Parameters
# 	data		data to aggregate
# 	codes   country codes
#
# Returns
#   aggregated data
#   
aggregateNUTS3ToCountry <- function(data,codes){
	sectorColPattern <- 'ALL|TOTAL|^[A-Z]$|AGR|MIN|MFG|EGW|CNS|TRD|OTP|WTP|CMN|OFI|OBS|REA|PUB|OSG'
	# identify columns with data rather than identifiers
	sectorCols <- grep(sectorColPattern,names(data),perl = T)
	# convert data to numeric (deals with in import error)
	for(s in sectorCols){
		suppressWarnings(data[[s]] <- as.numeric(data[[s]]))
	}
	data[is.na(data)] <- 0
	# combine the data and the codes datasets on the fid4 field if the data dataset 
	# does not already have a CNTR_CODE field that can be used for aggregation
	if(!('CNTR_CODE'%in%names(data))){
		data <- merge(codes,data,by = 'fid4')
	}
	sectorCols <- grep(sectorColPattern,names(data),perl = T)
	data <- aggregate(data[,c(sectorCols)],
											 by = list(Category=data$CNTR_CODE),FUN=sum)
	names(data)[1] <- 'CNTR_CODE'
	codesCNT <- codes[,-1]
	codesCNT <- codesCNT[!duplicated(codesCNT),]
	data <- merge(codesCNT,data)
	return(data)
}
