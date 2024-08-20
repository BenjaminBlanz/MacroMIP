#
# Uses the stocks in the flood scenario 2 and in the country level aggregate stocks derived
# from it to relativize the shocks in the earthquake and flood1 scenarios.
# 
# Benjamin Blanz 2024
# 

source('funRelData.R')

nuts3LevelStocksNACE <- read.csv("helperData/nuts3LevelStocksNACE.csv", row.names=NULL)
countryLevelStocksNACE <- read.csv("helperData/countryLevelStocksNACE.csv", row.names=NULL)
nuts3LevelStocksGTAP <- read.csv("helperData/nuts3LevelStocksGTAP.csv", row.names=NULL)
countryLevelStocksGTAP <- read.csv("helperData/countryLevelStocksGTAP.csv", row.names=NULL)
nuts3LevelStocksGRACE <- read.csv("helperData/nuts3LevelStocksGRACE.csv", row.names=NULL)
countryLevelStocksGRACE <- read.csv("helperData/countryLevelStocksGRACE.csv", row.names=NULL)


files <- list.files('scenarios',pattern = 'csv',recursive = T)
files <- paste0('scenarios/',files[grep('.csv$(?<!rel.csv)',files,perl=T)])
cat('Calculating relative impacts for...\n')
for(f.i in 1:length(files)){
	file <- files[f.i]
	cat(sprintf('%i of %i %s\n',f.i, length(files),file))
	data <- read.csv(file,row.names=NULL)
	if(grepl('GTAP',file)){
		data.rel <- relData(data,nuts3LevelStocksGTAP,countryLevelStocksGTAP)
		write.csv(data.rel,gsub('.csv','-rel.csv',file),row.names = F)
	} else if (grepl('GRACE',file)) {
		data.rel <- relData(data,nuts3LevelStocksGRACE,countryLevelStocksGRACE)
		write.csv(data.rel,gsub('.csv','-rel.csv',file),row.names = F)
	} else {
		data.rel <- relData(data,nuts3LevelStocksNACE,countryLevelStocksNACE)
		write.csv(data.rel,gsub('.csv','-rel.csv',file),row.names = F)
	}
}


