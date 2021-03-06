# Humnet data prep program
# Bring in 2010 migration data, collapse by MSA
# Output node csv with name, fips, lat, long, population, total domestic total foreign total nonmigrants 
# Output link csv with origin destination, returns, exemptions, total agi

library(gdata)
library(foreign)
setwd("~/projects/thesis")

#### Import data ####

## Total population ##
popdat = read.csv("data/msas/DEC_10_SF1_SF1DP1.csv")
popdat$fips = as.character(popdat$GEO.id2)
popdat[nchar(popdat$fips) == 4,"fips"] = paste("0",popdat[nchar(popdat$fips) == 4,"fips"],sep = "")
stopifnot(nchar(popdat$fips)==5)
popdat = popdat[,c("fips","HD01_S001")]
popdat = rename.vars(popdat, from = c("fips","HD01_S001"),to = c("cnty","pop"))

## Counties to MSAs ##
ctomsa = read.csv("data/msas/CountyMSA.csv")
ctomsa$msa = as.character(ctomsa$CBSA)
stopifnot(nchar(ctomsa$msa )==5)
ctomsa$cnty = as.character(ctomsa$County)
ctomsa[nchar(ctomsa$cnty)==4,"cnty"] = paste("0",ctomsa[nchar(ctomsa$cnty)==4,"cnty"],sep ="")
stopifnot(nchar(ctomsa$cnty )==5)

## MSA Names ##
msanames = read.csv("data/msas/MSANames.csv")
msanames$msa = as.character(msanames$MSACode)
stopifnot(nchar(msanames$msa )==5)

## Centroids ##
cents = read.dbf('data/msas/tl_2010_us_cbsa10/tl_2010_us_cbsa10.dbf')
#cent2 = read.table("data/msas/MSACents.txt", header = TRUE,sep = ",")
cents$msa = as.character(cents$CBSAFP)
cents$lat = as.numeric(as.character(cents$INTPTLAT10))
cents$lon = as.numeric(as.character(cents$INTPTLON10))
cents = cents[,c("msa","lat","lon")]

#Bring in county centroids
ccents = read.dbf('data/msas/tl_2013_us_county/tl_2013_us_county.dbf')
ccents$fips = as.character(ccents$GEOID)
ccents$lat = as.numeric(as.character(ccents$INTPTLAT))
ccents$lon = as.numeric(as.character(ccents$INTPTLON))
ccents$cid = paste('c_',ccents$fips,sep = "")
ccents = ccents[,c("fips","lat","lon",'cid')]

## Migration Data ##
#Inflow vs outflow appear equivalent except for sums at top of each entry and 60-80 records in only one of the two files

for(yr in c('0405','0506','0607','0708','0809','0910')){
	
#Inflow - primary data
migr = read.csv(paste("data/irs/countyinflow",yr,".csv",sep = ''))
migr$sto = as.character(migr$State_Code_Origin)
migr[nchar(migr$sto)==1,"sto"] = paste("0",migr[nchar(migr$sto)==1,"sto"],sep ="")

migr$std = as.character(migr$State_Code_Dest)
migr[nchar(migr$std)==1,"std"] = paste("0",migr[nchar(migr$std)==1,"std"],sep ="")

migr$cno = as.character(migr$County_Code_Origin)
migr[nchar(migr$cno)==1,"cno"] = paste("0",migr[nchar(migr$cno)==1,"cno"],sep ="")
migr[nchar(migr$cno)==2,"cno"] = paste("0",migr[nchar(migr$cno)==2,"cno"],sep ="")

migr$cnd = as.character(migr$County_Code_Dest)
migr[nchar(migr$cnd)==1,"cnd"] = paste("0",migr[nchar(migr$cnd)==1,"cnd"],sep ="")
migr[nchar(migr$cnd)==2,"cnd"] = paste("0",migr[nchar(migr$cnd)==2,"cnd"],sep ="")

migr$cntyo = paste(migr$sto,migr$cno,sep="")
migr$cntyd = paste(migr$std,migr$cnd,sep="")
stopifnot(nchar(migr$cntyo)==5)
stopifnot(nchar(migr$cntyd)==5)

#Outflow - for Node Stats and confirmation
omigr = read.csv(paste('data/irs/countyoutflow',yr,'.csv',sep = ''))
check = merge(migr,omigr, by = c("State_Code_Origin",'State_Code_Dest','County_Code_Origin','County_Code_Dest'))
stopifnot(check$Return_Num.x == check$Return_Num.y)

check2 = merge(migr,omigr, by = c("State_Code_Origin",'State_Code_Dest','County_Code_Origin','County_Code_Dest'), all = T)
innotout = check2[is.na(check2$Return_Num.y) & check2$State_Code_Origin <57,]
outnotin = check2[is.na(check2$Return_Num.x) & check2$State_Code_Dest <57,]

write.csv(innotout,paste('output/innotout',yr,'.csv',sep = ''), row.names= FALSE) 
write.csv(outnotin,paste('output/outnotin',yr,'.csv',sep = ''), row.names= FALSE) 

# Export list of -1's, then remove -1's and set negative AGIs to null ###
dim(migr[migr$Return_Num < 0,])
write.csv(migr[migr$Return_Num < 0,], paste('output/minus1s_',yr,'.csv',sep = ""), row.names = FALSE)
migr = migr[migr$Return_Num >=0,]
dim(migr[migr$Aggr_AGI <0,])
write.csv(migr[migr$Aggr_AGI < 0,], paste('output/negAGI_',yr,'.csv',sep = ""), row.names = FALSE)
migr[migr$Aggr_AGI<0,'Aggr_AGI'] = NA
#This appears to be working, but gave trouble one time

#### Merge and Aggregate Data ####

## Links ##
#Add on origin and destination msas. Include full list for compiling total stats - don't limit to just ones in MSAs
ccmigr = merge(migr,ctomsa,by.x = "cntyo",by.y = "cnty", all.x = TRUE)
ccmigr = merge(ccmigr,ctomsa,by.x = "cntyd",by.y = "cnty", all.x = TRUE)
ccmigr = rename.vars(ccmigr,from = c("msa.x","msa.y"),to = c("msao","msad"))
#stopifnot(dim(ccmigr)[1]==110651)

##MSA-MSA flows
#Limit to MSA to MSA
mmmigr = ccmigr[!is.na(ccmigr$msao) & !is.na(ccmigr$msad),]
stopifnot(mmmigr$Return_Num >=0)
#stopifnot(dim(mmmigr)[1]==68831)

#Collapse into MSA-MSA flows
m2m = aggregate(mmmigr[,c('Exmpt_Num','Return_Num','Aggr_AGI')],list(mmmigr$msao,mmmigr$msad),FUN = "sum")
m2m = rename.vars(m2m,from = c("Group.1","Group.2"),to = c("source","target"))
m2m = m2m[m2m$source != m2m$target,]

#Export
write.csv(m2m,paste('output/m2m',yr,'.csv',sep = ''), row.names= FALSE)


##County-MSA flows
#Drop destinations that aren't counties
ccmigr = ccmigr[ccmigr$County_Code_Dest != 0,]

#Drop origins that aren't from states
ccmigr = ccmigr[ccmigr$State_Code_Origin < 57,]

#Make counties into MSAs for purposes of aggregation
ccmigr[is.na(ccmigr$msao),'msao'] = paste("c_", ccmigr[is.na(ccmigr$msao),'cntyo'], sep = '')
ccmigr[is.na(ccmigr$msad),'msad'] = paste('c_', ccmigr[is.na(ccmigr$msad),'cntyd'], sep = '')

#Collapse into MSA-County flows
c2m = aggregate(ccmigr[,c('Exmpt_Num','Return_Num','Aggr_AGI')],list(ccmigr$msao,ccmigr$msad),FUN = "sum")
c2m = rename.vars(c2m,from = c("Group.1","Group.2"),to = c("source","target"))
c2m = c2m[c2m$source != c2m$target,]

#Confirm this matches m2m for msa-msa flows
check3 = merge(c2m,m2m, by = c('source','target'),all.y = T)

#Same size
stopifnot(dim(check3)[1] == dim(m2m)[1])
#Same values
stopifnot(check3$Exmpt_Num.x == check3$Exmpt_Num.y)
stopifnot(check3$Return_Num.x == check3$Return_Num.y)
stopifnot((check3$Aggr_AGI.x == check3$Aggr_AGI.y) | is.na(check3$Aggr_AGI.x)) #Because of the NAs in AGI in introduce earlier

#Export
write.csv(c2m, paste('output/c2m',yr,'.csv',sep = ''),row.names = F)

#Add both directions; only count once
#Merge on other direction
m2m2 = merge(m2m,m2m,by.x = c('source','target'),by.y = c('target','source'),all = TRUE)
m2m2 = rename.vars(m2m2, from = c("Exmpt_Num.x","Return_Num.x","Aggr_AGI.x","Exmpt_Num.y","Return_Num.y","Aggr_AGI.y"), to = c('exmpt_st','return_st','aggragi_st','exmpt_ts','return_ts','aggragi_ts'))

#Get common pairs
m2m2$msa1 = apply(m2m2[,c('source','target')],1,min)
m2m2$msa2 = apply(m2m2[,c('source','target')],1,max)

#Pick only the first appearance of each pair
getfirst = function(x) x[1]
#mcol = by(m2m2, list(as.factor(m2m2$msa1),as.factor(m2m2$msa2)),getfirst)
#mcol = aggregate(m2m2, list(as.factor(m2m2$msa1),as.factor(m2m2$msa2)),getfirst)
mcol = aggregate(m2m2[,c('source','target','exmpt_st','return_st','aggragi_st','exmpt_ts','return_ts','aggragi_ts')], by=list(m2m2$msa1,m2m2$msa2),FUN=getfirst)
mcol=mcol[,3:10]
mcol[is.na(mcol)]=0
mcol$exmptgross = apply(mcol[,c('exmpt_st','exmpt_ts')],1,FUN=min)

#Export
write.csv(mcol,paste('output/grossm',yr,'.csv',sep = ''),row.names = FALSE)
write.csv(mcol[mcol$exmptgross > 0,],paste('output/grossm_abridged',yr,'.csv',sep = ''),row.names=F)
} #End year loop

## Nodes ##
#For now just merge on lat/long to population

#Population
#Merge
cmpop = merge(popdat,ctomsa,by = "cnty",all.x = T)
stopifnot(dim(cmpop)[1]==3221)
mpop = merge(popdat,ctomsa,by = "cnty",all.x = F)
stopifnot(dim(mpop)[1]==1863)

#Collapse to counties and MSAs
cmpop[is.na(cmpop$msa),'msa'] = paste('c_',cmpop[is.na(cmpop$msa),'cnty'],sep = "")
popcm = aggregate(cmpop$pop, list(cmpop$msa),FUN = 'sum')
popcm = rename.vars(popcm,from = c("Group.1","x"),to = c("id","pop"))
stopifnot(dim(popcm)[1]==2313)

#Add in county and MSA lat and long
popcm = merge(popcm, cents, by.x = 'id', by.y = 'msa', all.x = T)
popcm = merge(popcm, ccents, by.x = 'id', by.y = 'cid', all.x = T)
popcm[is.na(popcm$lat.x), 'lat.x'] = popcm[is.na(popcm$lat.x), 'lat.y'] 
popcm[is.na(popcm$lon.x), 'lon.x'] = popcm[is.na(popcm$lon.x), 'lon.y'] 
stopifnot(!is.na(popcm$lat.x))
popcm = rename.vars(popcm, c('lat.x','lon.x'), c('lat','lon'))
popcm = popcm[,1:5]

#MSA
popmsa = popcm[substr(popcm$id,1,1) != 'c',]
stopifnot(dim(popmsa)[1]==955)
popmsa = merge(popmsa,msanames,by.x = "id", by.y = "msa", all )
stopifnot(is.na(popmsa$MSAName)==FALSE)
popmsa = popmsa[,setdiff(names(popmsa),'fips')]

#Export
write.csv(popmsa,'output/msadata.csv',row.names=FALSE)
write.csv(popcm,'output/cmdata.csv',row.names=FALSE)

