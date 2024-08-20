# 
# Function to calculate the relative magnitude of shocks to capital stocks
# relative to the size of the sectoral capital stocks.
# 
# Stocks can be provided either at the country or at the NUTS3 level. The regional 
# aggregation of data and stocks has to match. 
# The column names in data and stocks should match.
# 
# Parameters
# 	data  				The shock impacts specifying the capital destroyed
# 	stocksNUTS3   The sectoral stocks of capital at NUTS3 level
#   stocksCNT     The sectoral stocks of capital at country level
# 
# Returns
# 	shock data relative to the stocks
# 
# Benjamin Blanz 2024
#
relData <- function(data,stocksNUTS3=NULL,stocksCNT=NULL){
	sectorColPattern <- 'ALL|TOTAL|^[A-Z]$|AGR|MIN|MFG|EGW|CNS|TRD|OTP|WTP|CMN|OFI|OBS|REA|PUB|OSG|agr|coa.oil.gas|pro|ely.elc|ser|air.wtp.tran'
	# Ensure the Total clumn is called TOTAL, not ALL as in some scenarios
	names(data)[names(data)=='ALL'] <- 'TOTAL'
	names(stocksNUTS3)[names(stocksNUTS3)=='ALL'] <- 'TOTAL'
	names(stocksCNT)[names(stocksCNT)=='ALL'] <- 'TOTAL'
	# Identify the columns with data (not the columns with country or idx). 
	sectorCols <- grep(sectorColPattern,names(data),perl = T)
	# prepare an empty data set for the relative data, keeping the index columns
	data.rel <- data
	data.rel[,sectorCols] <- NA
	for(i in 1:nrow(data)){
		# identify the correct row in the stocks 
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
		# calculate relative impact for all sectors of this row
		for(s in names(data)[sectorCols]){
			suppressWarnings(data.rel[i,s] <- as.numeric(data[i,s]) / as.numeric(stocks[rowInStocks,s]))
			if (is.nan(data.rel[i,s])|is.na(data.rel[i,s])){
				data.rel[i,s] <- 0
			}
		}
	}
	return(data.rel)
}
