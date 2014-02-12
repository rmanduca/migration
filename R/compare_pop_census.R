# Program to compare the total population by county to the Census 2010 population by county
# Adding in income comparison

library(gdata)
library(maps)
library(RColorBrewer)
setwd("~/projects/thesis")
source('code/R/aggplus.R')

## Total population - Census ##
popdat = read.csv("data/msas/DEC_10_SF1_SF1DP1.csv")
popdat$fips = as.character(popdat$GEO.id2)
popdat[nchar(popdat$fips) == 4,"fips"] = paste("0",popdat[nchar(popdat$fips) == 4,"fips"],sep = "")
stopifnot(nchar(popdat$fips)==5)
popdat = popdat[,c("fips","HD01_S001")]
popdat = rename.vars(popdat, from = c("fips","HD01_S001"),to = c("cnty","pop"))

## Income Data
'''
1 year estimates - only have 800 counties
incdat = read.csv('data/acs/acs_income_1yr/ACS_10_1YR_DP03_with_ann.csv')
incdat$fips = as.character(incdat$GEO.id2)
incdat[nchar(incdat$fips) == 4,"fips"] = paste("0",incdat[nchar(incdat$fips) == 4,"fips"],sep = "")
stopifnot(nchar(incdat$fips)==5)
incdat = incdat[,c('fips','HC01_VC85','HC01_VC86')]
incdat = rename.vars(incdat, from = c('fips','HC01_VC85','HC01_VC86'), to = c('cnty','medinc','meaninc'))
'''
incdat = read.csv('data/acs/ACS_10_5YR_S1901/ACS_10_5YR_S1901_with_ann.csv')
incdat$fips = as.character(incdat$GEO.id2)
incdat[nchar(incdat$fips) == 4,"fips"] = paste("0",incdat[nchar(incdat$fips) == 4,"fips"],sep = "")
stopifnot(nchar(incdat$fips)==5)
incdat = incdat[,c('fips','HC01_EST_VC15','HC02_EST_VC15','HC03_EST_VC15','HC04_EST_VC15')]
incdat = rename.vars(incdat, from = c('fips','HC01_EST_VC15','HC02_EST_VC15','HC03_EST_VC15','HC04_EST_VC15'), to = c('cnty','mihh','mifam','mimc','minf'))


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


## Income analysis
miginctot = aggplus(migpop, 'Aggr_AGI','cntyd',sum)
migrettot = aggplus(migpop, 'Return_Num','cntyd',sum)
miginc = merge(miginctot, migrettot, by = 'cntyd')
miginc$migmeaninc = miginc$Aggr_AGI / miginc$Return_Num * 1000
#AGI in $1000's

compinc = merge(incdat,miginc,by.x = 'cnty',by.y = 'cntyd', all = T)

#Nothing missing in migration
compinc[is.na(compinc$migmeaninc),]
#Places missing income are two counties in Alaska
compinc[is.na(compinc$mihh),]
#Several counties that don't have migration data (all -1 in migr)
compinc[compinc$Aggr_AGI <0,]
#Drop both types of NA and the -1 counties
compinc = compinc[!is.na(compinc$migmeaninc) & !is.na(compinc$mihh) & compinc$Aggr_AGI >=0,]

#Look at ratio of migincome to incomes
compinc$ratio = compinc$migmeaninc / compinc$mihh

summary(compinc$ratio)
hist(compinc$ratio, breaks = 50)

# Ratio is about .8 - mean household income is higher than mean return income. Could be from multiple returns per household I guess? 
# Not sure any way to do better.