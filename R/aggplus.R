## Better aggregate that doesn't require renaming all the time

library(gdata)

aggplus = function(data,aggvar, byvar,fun ) {
	retval = aggregate(data[,aggvar],list(data[,byvar]), FUN = fun)
	retval = rename.vars(retval, from = c("Group.1",'x'), to = c(byvar,aggvar))
}