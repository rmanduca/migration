# Program to compare the total population by county to the Census 2010 population by county

library(gdata)
library(maps)
library(RColorBrewer)
setwd("~/projects/thesis")

## Total population - Census ##
popdat = read.csv("data/msas/DEC_10_SF1_SF1DP1.csv")
popdat$fips = as.character(popdat$GEO.id2)
popdat[nchar(popdat$fips) == 4,"fips"] = paste("0",popdat[nchar(popdat$fips) == 4,"fips"],sep = "")
stopifnot(nchar(popdat$fips)==5)
popdat = popdat[,c("fips","HD01_S001")]
popdat = rename.vars(popdat, from = c("fips","HD01_S001"),to = c("cnty","pop"))

## 2009-2010 Migration Data ##
migr = read.csv(paste("data/irs/countyinflow",'0910',".csv",sep = ''))
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

#Look only at total migrants and nonmigrants
migpop = migr[(migr$cntyo == migr$cntyd) | (migr$sto == '96' & migr$County_Code_Dest > 0),]
migpoptot = aggregate(migpop$Exmpt_Num, by = list(migpop$cntyd), FUN = sum)
migpoptot = rename.vars(migpoptot, from = c('Group.1','x'), to = c('cnty','migpop'))
compare = merge(popdat, migpoptot, by = 'cnty', all = T)

#Places missing migpop are all Puerto Rico; ok
compare[is.na(compare$migpop),]
#Places missing pop are two counties in Alaska
compare[is.na(compare$pop),]
#Several counties that don't have pop data (all -1 in migr)
compare[compare$migpop <0,]
#Drop both types of NA and the -1 counties
compare = compare[!is.na(compare$migpop) & !is.na(compare$pop) & compare$migpop >=0,]

#Look at ratio of migpop to pop
compare$ratio = compare$migpop / compare$pop

#8 Counties with more tax exemptions than people (?)
compare[compare$ratio > 1,]
write.csv(compare[compare$ratio > 1, ], 'output/concerning_obs/exmpt_gt_pop.csv')

#Summary of ratio
summary(compare$ratio)
#On average, about 79% as many exemptions as people

#Totals - again, ratio of 79%
sum(compare$migpop) / sum(compare$pop)

#Hist 
pdf('output/rplots/census_migr_pop_hist.pdf')
hist(compare$ratio, breaks = 60)
dev.off()

#Export ratios
write.csv(compare, 'output/pop_compare.csv', row.names = F)

