#!/usr/bin/Rscript

#usage: Rscript --vanilla lollipop.R [inputdirectory] [bs-seq-library:<DIR|NONDIR>] [tool used for alignments]

################################## Required R packages ################################################################
library(ggplot2)
library(plyr)
library(reshape2)

## DEBUG
#options(error=traceback)

################################## Filtering of Parameters ############################################################
args <- commandArgs(TRUE)
directory <- args[1]
library_dir <- args[2] #directional or non-directional
aligner <- args[3]
samples.sorting.file <- args[4] #Parameter specifying the sample order of the plot



################################## Managing working directory #########################################################
current_dir <- getwd()
setwd(directory)

##DEBUG
#print(current_dir)

################################## Method for the creation of a lollipop plot #########################################
plotting <- function(x){
    plottype <- x
    if (plottype == "adapted") dataset$pos <- as.factor(dataset$pos)

    ## DEBUG
    # print(Name)
    # print("dataset")
    # print(head(dataset))
    # print(str(dataset))
    # print(dataset)
    # print("")
    # print(nrow(dataset))
    # print("samples.sorting.file")
    # print(samples.sorting.file)


    ## Fix the name of the sample.sorting.file
    my.sorting.data.fixed <- NA

    if(!is.na(samples.sorting.file)) {
	#print("Valid sorting file")

	## Convert to vector
	my.sorting.data <- read.table(samples.sorting.file) 
	my.sorting.data.vector <- as.vector(my.sorting.data[,1])

	## Initialize vector
	my.sorting.data.fixed <- unique(dataset$variable)

	##DEBUG
	#print(my.sorting.data)
	#print(str(my.sorting.data))
	#print(my.sorting.data.vector)
	#print(str(my.sorting.data.vector))
	#print(paste0("my.sorting.data.fixed: ", my.sorting.data.fixed))
	#print("my.sorting.data.fixed")
	#print(my.sorting.data.fixed)


	#print("Starting finding matches")

	sorting.index <- 1
	for(sample.name in my.sorting.data.vector) {
	    ## Find the corresponding name in the dataset
	    for(my.name in dataset$variable) {
		## DEBUG
    		#print(paste0("my.name: ", my.name))
		#print(paste0("sample.name: ", sample.name))
		
		if (grepl(my.name, sample.name) || grepl(sample.name, my.name)) {
		    my.sorting.data.fixed[sorting.index] <- my.name
		}
	    }
	    sorting.index <- sorting.index + 1
	}


    }

    #print("Start sorting")

    ## Sort the dataset according to the sample values
    if(!is.na(my.sorting.data.fixed)) {

	## Create index based on sorting data
	idx <- sapply(my.sorting.data.fixed, function(x) {
	    which(dataset$variable == x)
	})

	#print("Built index")
	#print(idx)

	dataset <- dataset[idx,]
	## Set as factor
	dataset$variable <- factor(dataset$variable, levels=dataset$variable)

    }


    ## Check if only one position should be printed -> don't do this as it results in an error
    if(nrow(dataset) == 1) {
	return()
    }

    dataset$variable <- factor(dataset$variable, levels=dataset$variable)


    pdf(file = paste("PLOTS/",library_dir,"_",aligner,"_",plottype,"___",Name,".pdf",sep=""), width=pixelw, height = pixelh)
    p <-  ggplot(dataset, aes(x=pos, y=variable, color=cut(value, breaks=c(-0.01,10,20,30,40,50,60,70,80,90,100)), shape=ifelse(is.na(value), "Missing", "Present")))
    p <- p + geom_point(size=4)
    p <- p + scale_shape_manual(name="", values=c(Missing=4, Present=19))
    if (plottype == "proportional") {
	p <- p + scale_x_continuous(breaks=xaxes)
    }
    p <- p + scale_color_discrete(h=c(0,360)+15, c=100, l=65, h.start=0, direction=1, na.value="grey", name= "% Methylation", labels=c("0-10%","10-20%","20-30%","30-40%","40-50%","50-60%","60-70%","70-80%","80-90%","90-100%"),drop=FALSE)
    p <- p + xlab("CpG Position") 
    p <- p + ylab("Sample")
    p <- p + ggtitle(paste("Target: ", Name, "(",chrom,")"))
    p <- p + theme_bw()
    p <- p + theme(axis.text.x = element_text(angle=90, hjust=1, vjust=0.5),plot.title = element_text(vjust=2),axis.title.x = element_text(vjust=-0.5),axis.title.y = element_text(vjust=1.5)) 
    print(p)

    print("Done with printing")

    dev.off()
}


################################### Read in & splitting the data######################################################
warnings()
data <- read.csv("ResultMethylList.csv")
data <- subset(data, select=(names(data)[grep('^Name|^chr|^pos|^Reads...ME', names(data))]))
dfs <- split(data, f=data[, "Name"])
lapply(dfs, function(x) write.csv(x,row.names= FALSE, quote = FALSE,na = "NA", file=paste0(x[1,1], ".csv")))


################################### Create proportional & adapted plot for every target ##############################
files <- list.files(path=getwd(), pattern="cg.*\\.csv", all.files=T, full.names=T)
#fileConn<-file("targetlength.txt")
for (file in files) {
    dataset <- read.table(file,  sep=",",na.strings="-", header=TRUE)

    ##DEBUG
    #print(basename(file))
    #print(dataset)
    #dataset <-read.table("cg04856858.csv",  sep=",",na.strings="-", header=TRUE)

    target <- max(dataset$pos) - min(dataset$pos)
    pixelw <-target*8.32/72 # target * 33
    pixelh <- pixelw * 0.32
    chrom <- unique(dataset$chr)
    Name <- unique(dataset$Name)

    ## Subset the dataset
    dataset <- subset(dataset, select=c(-Name, -chr))
    dataset <- melt(dataset, id.vars="pos")
    
    ## Substitute "." with "_"
    dataset$variable <- gsub("\\.\\.\\.","_",dataset$variable)

    ## Remove "Reads_ME_" prefix
    dataset$variable <- gsub("Reads_ME_","",dataset$variable)
    
    xaxes <- unique(dataset$pos)
    plotting("adapted")
    plotting("proportional")
}

print("Done printing all targets.")


################################# Change working directory to default ################################################
setwd(current_dir)


######################################################################################################################

