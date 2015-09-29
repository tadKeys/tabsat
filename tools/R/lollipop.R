#!/usr/bin/Rscript

#usage: Rscript --vanilla lollipop.R [inputdirectory] [bs-seq-library:<DIR|NONDIR>] [tool used for alignments]

################################## Required R packages ################################################################
library(ggplot2)
library(plyr)
library(reshape2)


################################## Filtering of Parameters ############################################################
args<-commandArgs(TRUE)
directory = args[1];
library_dir = args[2]; #directional or non-directional
aligner = args[3]


################################## Managing working directory #########################################################
current_dir <- getwd()
setwd(directory)

##DEBUG
#print(current_dir)

################################## Method for the creation of a lollipop plot #########################################
plotting <- function(x){
  plottype <- x
  if (plottype == "adapted") dataset$Pos <- as.factor(dataset$Pos)

  ## DEBUG
#  print(Name)
#  print("dataset")
#  print(dataset)
#  print("")
#  print(nrow(dataset))


  ## Check if only one position should be printed -> don't do this as it results in an error
  if(nrow(dataset) == 1) {
    return()
  }

  pdf(file = paste("PLOTS/",library_dir,"_",aligner,"_",plottype,"___",Name,".pdf",sep=""), width=pixelw, height = pixelh)
  p <-  ggplot(dataset, aes(x=Pos, y=variable,color=cut(value, breaks=c(-0.01,10,20,30,40,50,60,70,80,90,100)),shape=ifelse(is.na(value),"Missing","Present")))
  p <- p + geom_point(size=4)
  p <- p + scale_shape_manual(name="",values=c(Missing=4,Present=19))
  if (plottype == "proportional") 
  {p <- p + scale_x_continuous(breaks=xaxes)}
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
data <- subset(data, select=(names(data)[grep('^Name|^chr|^Pos|^Reads...ME', names(data))]))
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

  target <- max(dataset$Pos) - min(dataset$Pos)
  pixelw <-target*8.32/72 # target * 33
  pixelh <- pixelw * 0.32
  chrom <- unique(dataset$chr)
  Name <- unique(dataset$Name)
  dataset <- subset(dataset, select=c(-Name, -chr))
  dataset <- melt(dataset, id.vars="Pos")
  dataset$variable <- gsub("\\.\\.\\.","_",dataset$variable)
  xaxes <- unique(dataset$Pos)
  plotting("adapted")
  plotting("proportional")
}


################################# Change working directory to default ################################################
setwd(current_dir)


######################################################################################################################

