#
# aggregate the flood2010 and earthquake scenarios to country level
#
# Benjamin Blanz 2024
#

source('funAggregateNuts2CNT.R')
codes <- read.csv("helperData/nuts3fid4Codes.csv")
codes <- codes[,c('fid4','CNTR_CODE','CNTR_NAME','CNTR_CODE_iso2','CNTR_CODE_iso3','CNTR_CODE_Eurostat')]
codes <- codes[!duplicated(codes),]

# files to aggregate

files <- list.files('scenarios',pattern = 'csv',recursive = T)
files <- paste0('scenarios/',files[grep('.csv$(?<!aggCNT.csv)',files,perl=T)])
files <- files[grep('.csv$(?<!rel.csv)',files,perl=T)]
cat('Aggregating NUTS3 to CNT for...\n')
for(f.i in 1:length(files)){
	file <- files[f.i]
	cat(sprintf('%i of %i %s\n',f.i, length(files),file))
	data <- read.csv(file,row.names=NULL)
	if(!('fid4'%in%names(data))){
		cat('    fid4 col missing probably already country level data\n')
	} else {
		data.CNT <- aggregateNUTS3ToCountry(data,codes)
		write.csv(data.CNT,gsub('.csv','-aggCNT.csv',file),row.names = F)
	}
}
