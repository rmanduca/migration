# Program to start comparing the distribution of migrants across years

library(gdata)
setwd("~/projects/thesis")

# Bring in data created in prep_allyears
# Yearly migrations
for(i in 4:9){
	if(i == 9){
		datim = read.csv(paste('output/m2m0',i,i+1,'.csv',sep = ""))
	}
	else{
		datim = read.csv(paste('output/m2m0',i,'0',i+1,'.csv',sep = ""))	
	}
	#Just looking at exemptions for now
	datim = datim[,c('source','target','Exmpt_Num')]
	datim = rename.vars(datim, from = "Exmpt_Num", to = paste('e',i,sep = ''))
	assign(paste('d',i,sep = ""), datim)
}

#Metro Population data
pops = read.csv('output/msadata.csv')
# Merge all years together

dat = merge(d4, d5,by = c('source','target'), all = T)
dat = merge(dat, d6,by = c('source','target'), all = T)
dat = merge(dat, d7,by = c('source','target'), all = T)
dat = merge(dat, d8,by = c('source','target'), all = T)
dat = merge(dat, d9,by = c('source','target'), all = T)
dat[is.na(dat)] = 0

#Add in pop origin and pop destination
dat = merge(dat, pops[,c('id','pop','MSAName')], by.x = 'source',by.y = 'id')
dat = rename.vars(dat, from = c('pop','MSAName'),to = c('spop','sname'))
dat = merge(dat, pops[,c('id','pop','MSAName')], by.x = 'target',by.y = 'id')
dat = rename.vars(dat, from = c('pop','MSAName'),to = c('tpop','tname'))

#Compute correlation across years
cor(dat[,3:8],dat[,3:8])

#Plot correlations
plot(dat$e4, dat$e5, pch = 20)
plot(dat$e4, dat$e6, pch = 20)
plot(dat$e4, dat$e7, pch = 20)
plot(dat$e4, dat$e8, pch = 20)

#Huge outlier is LA-Riverside
dat[dat$e4 > 39000,]

#Try correlations again without them
cor(dat[dat$e4 < 39000,3:8],dat[dat$e4 < 39000,3:8])
#Still pretty high?

#Plots by year - Still need some formatting
for(j in 3:7){
pdf(paste('output/rplots/biyearly_0',j+1,'.pdf', sep = ''))
par(mfrow = c(2,2),oma = c(0, 0, 3, 0))
for(i in 3:7){
	if(i == j) next
	plot(dat[dat$e4 < 39000,j],dat[dat$e4 < 39000,i], pch = 20, 
	xlim = c(0,50000), ylim = c(0,50000),
	ylab = paste('0',i+1,'-0',i+2, sep = ''),
	xlab = paste('0',j+1,'-0',j+2, ', cor = ',round(cor(dat[dat$e4 < 39000,3],dat[dat$e4 < 39000,i]), 2), sep = ""))
}
mtext(paste('Biyearly Comparisons, 0',j+1,'-0',j+2, sep = ""), outer = TRUE, cex = 1.5)
dev.off()
}





