#
# Uses the stocks in the flood scenario 2 and in the country level aggregate stocks derived
# from it to relativize the shocks in the earthquake and flood1 scenarios.
# 

source('funRelData.R')

nuts3LevelStocks <- read.csv("helperData/nuts3LevelStocks.csv", row.names=NULL)
countryLevelStocks <- read.csv("helperData/countryLevelStocks.csv", row.names=NULL)


files <- list.files('scenarios',pattern = 'csv',recursive = T)
files <- paste0('scenarios/',files[grep('.csv$(?<!rel.csv)',files,perl=T)])
cat('Calculating relative impacts for...\n')
for(f.i in 1:length(files)){
	file <- files[f.i]
	cat(sprintf('%i of %i %s\n',f.i, length(files),file))
	data <- read.csv(file,row.names=NULL)
	data.CNT <- relData(data,nuts3LevelStocks,countryLevelStocks)
	write.csv(data.CNT,gsub('.csv','-rel.csv',file),row.names = F)
}


