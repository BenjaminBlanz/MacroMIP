relData <- function(data,stocksNUTS3=NULL,stocksCNT=NULL){
	names(data)[names(data)=='ALL'] <- 'TOTAL'
	names(stocksNUTS3)[names(stocksNUTS3)=='ALL'] <- 'TOTAL'
	names(stocksCNT)[names(stocksCNT)=='ALL'] <- 'TOTAL'
	sectorCols <- grep('ALL|TOTAL|^[A-Z]$',names(data),perl = T)
	data.rel <- data
	data.rel[,sectorCols] <- NA
	for(i in 1:nrow(data)){
		if('fid4' %in% names(data)){
			stocks <- stocksNUTS3
			rowInStocks <- which(stocks$fid4 == data$fid4[i])
		} else if (nchar(data$CNTR_CODE[i])==2){
			stocks <- stocksCNT
			rowInStocks <- which(stocks$CNTR_CODE_Eurostat == data$CNTR_CODE[i])
			if(length(rowInStocks)==0){
				rowInStocks <- which(stocks$CNTR_CODE_iso2== data$CNTR_CODE[i])
			} 
		} else if (nchar(data$CNTR_CODE[i])==3){
			stocks <- stocksCNT
			rowInStocks <- which(stocks$CNTR_CODE_iso3 == data$CNTR_CODE[i])
		}
		if(length(rowInStocks)==0){
			warning(paste('no region match for data row',i))
		}
		for(s in names(data)[sectorCols]){
			suppressWarnings(data.rel[i,s] <- as.numeric(data[i,s]) / as.numeric(stocks[rowInStocks,s]))
			if (is.nan(data.rel[i,s])|is.na(data.rel[i,s])){
				data.rel[i,s] <- 0
			}
		}
	}
	return(data.rel)
}
