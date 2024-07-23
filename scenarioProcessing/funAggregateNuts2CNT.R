aggregateNUTS3ToCountry <- function(data,codes){
	sectorCols <- grep('ALL|TOTAL|^[A-Z]$',names(data),perl = T)
	for(s in sectorCols){
		suppressWarnings(data[[s]] <- as.numeric(data[[s]]))
	}
	data[is.na(data)] <- 0
	if(!('CNTR_CODE'%in%names(data))){
		data <- merge(codes,data,by = 'fid4')
	}
	sectorCols <- grep('ALL|TOTAL|^[A-Z]$',names(data),perl = T)
	data <- aggregate(data[,c(sectorCols)],
											 by = list(Category=data$CNTR_CODE),FUN=sum)
	names(data)[1] <- 'CNTR_CODE'
	codesCNT <- codes[,-1]
	codesCNT <- codesCNT[!duplicated(codesCNT),]
	data <- merge(codesCNT,data)
	return(data)
}
