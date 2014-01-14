# Humnet graph making program
library(plyr)
library(gdata)
setwd("~/projects/thesis")

dta = read.csv('gephi/rdundirn2.csv')
links = read.csv('output/grossm_abridged.csv')

hist(dta$Degree)

#Degree
t = table(round_any(dta$Degree,10))
pdf('output/degreedensity.pdf')
plot(as.numeric(names(t)),t, log = 'yx', main = "Degree Distribution (log-log)", xlab = 'Degree',ylab = 'Count', pch = 20)
dev.off()

mean(dta$Degree)
median(dta$Degree)


#Clustering Coef
t = table(round_any(dta$Clustering.Coefficient,.05))
pdf('output/cc.pdf')
plot(as.numeric(names(t)),t,  main = "Clustering Coefficient Distribution", xlab = 'Clustering Coefficient',ylab = 'Count', pch = 20,yaxt = 'n')
axis(2,0:10*25)
dev.off()

#Clust vs Degree
pdf('output/ccvsdegree.pdf')
plot(dta$Degree, dta$Clustering.Coefficient, main = "Clustering Coefficient vs Degree", xlab = "Degree",ylab = 'Clustering Coefficient', pch = 20)
dev.off()

pdf('output/ccvswdegree.pdf')
plot(dta$Weighted.Degree, dta$Clustering.Coefficient, main = "Clustering Coefficient vs Weighted Degree", xlab = "Weighted Degree",ylab = 'Clustering Coefficient', pch = 20)
dev.off()


#Weighted Degree
t = table(round_any(dta$Weighted.Degree,100))
n = as.numeric(names(t))

pdf('output/weighteddegree.pdf')
plot(n,t, log = 'x', main = "Weighted Degree Distribution (log-lin)", xlab = 'Weighted Degree',ylab = 'Count', pch = 20)
axis(2,at = 1:10*10)
dev.off()
mean(dta$Weighted.Degree)
median(dta$Weighted.Degree)

#Weighted vs Unweighted Degree
pdf('output/wuwlog.pdf')
plot(dta$Degree, dta$Weighted.Degree, main = "Weighted vs Unweighted Degree - Correlation 0.846 - Log-Log", xlab = "Unweighted Degree",ylab = 'Weighted Degree',log = 'xy', pch = 20)
dev.off()
cor(dta$Degree, dta$Weighted.Degree)

pdf('output/wuw.pdf')
plot(dta$Degree, dta$Weighted.Degree, main = "Weighted vs Unweighted Degree - Correlation 0.846", xlab = "Unweighted Degree",ylab = 'Weighted Degree', pch = 20)
dev.off()
cor(dta$Degree, dta$Weighted.Degree)


#Betweenness Centrality
t = table(round_any(dta$Betweenness.Centrality,100))

pdf('output/betweenness.pdf')
plot(as.numeric(names(t)),t, log = 'yx', main = "Betweenness Centrality Distribution (log-log)", xlab = 'Degree',ylab = 'Count', yaxt = "n" ,pch = 20)
axis(2,at = c(5,10,50,100,500))
dev.off()

#Betweenness vs Degree
pdf('output/betweennessvsdegree.pdf')
plot(dta$Degree,dta$Betweenness.Centrality, pch = 20, main = "Betweenness Centrality vs Degree - Correlation 0.826", xlab = "Degree", ylab = 'Betweenness Centrality')
dev.off()
pdf('output/betweennessvsdegreelog.pdf')
plot(dta$Degree,dta$Betweenness.Centrality, pch = 20, main = "Betweenness Centrality vs Degree - Correlation 0.826", xlab = "Degree", ylab = 'Betweenness Centrality', log = 'xy')
dev.off()
cor(dta$Degree,dta$Betweenness.Centrality)

pdf('output/bvwd.pdf')
plot(dta$Weighted.Degree,dta$Betweenness.Centrality, pch = 20, main = "Betweenness Centrality vs Weighted Degree - Correlation 0.708", xlab = "Weighted Degree", ylab = 'Betweenness Centrality')
dev.off()
pdf('output/bvwdl.pdf')
plot(dta$Weighted.Degree,dta$Betweenness.Centrality, pch = 20, main = "Betweenness Centrality vs Weighted Degree - log-log", xlab = "Weighted Degree", ylab = 'Betweenness Centrality',log = 'xy')
dev.off()

cor(dta$Weighted.Degree,dta$Betweenness.Centrality)



#Closeness vs Degree
pdf('output/closenessvsdegree.pdf')
plot(dta$Degree,dta$Closeness.Centrality, pch = 20, main = "Closeness Centrality vs Degree", xlab = "Degree", ylab = 'Closeness Centrality')
dev.off()
pdf('output/Closevsdegreelog.pdf')
plot(dta$Degree,dta$Closeness.Centrality, pch = 20, main = "Closeness Centrality vs Degree", xlab = "Degree", ylab = 'Closeness Centrality', log = 'xy')
dev.off()

#Weights Dist
t = table(round_any(links$exmptgross,1000))
pdf('output/weightsdist.pdf')
plot(as.numeric(names(t)),t, log = 'yx', main = "Edge Weight Distribution", xlab = 'Edge Weight (Number of Migrants)',ylab = 'Count',yaxt = 'n')
axis(2,at = c(10,100,500,1000))
dev.off()
mean(links$exmptgross)
median(links$exmptgross)