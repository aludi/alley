library(bnlearn)
library(dplyr)
library(readr)


merge1 <- read_csv("out/data/merge.csv", col_types = cols(
  X1 = col_skip(),
  `Unnamed: 0_x` = col_skip(),
  run = col_skip(),
  agentID = col_skip(),
  other = col_skip(),
  other_thief = col_skip(),
  other_suspect = col_skip(),
  other_cs = col_double(),
  other_alib = col_double(),
  `Unnamed: 0_y` = col_skip(),
  suspect = col_double(),
  victim = col_double(),
  thief = col_double(),
  DNAatCS = col_double(),
  locCS = col_double(),
  statement = col_double(),
  experiment_name = col_skip(),
  runs = col_skip()
))
  

merge_d <- merge1 %>% mutate_if(is.double,as.factor)
d <- as.data.frame(merge_d)

n <- read.net(file="~/Desktop/phd/code/alley/out/BNs/manual.net")
graphviz.plot(n)
x<- bn.net(n)
plot(x)
fitted <- bn.fit(x, data = d, method='mle')
#fitted = bn.fit(structure, d, method = "mle")
write.net(file="~/Desktop/phd/code/alley/out/BNs/manualMLE.net", fitted)


fitted <- bn.fit(x, data = d)
write.net(file="~/Desktop/phd/code/alley/out/BNs/manualDEF.net", fitted)
plot(x)



structure <- hc(d)
fitted = bn.fit(structure, d, method = "mle")
write.net(file="~/Desktop/phd/code/alley/out/BNs/bic.net", fitted)
plot(structure)


structure <- hc(d, score="loglik")
fitted = bn.fit(structure, d, method = "mle")
write.net(file="~/Desktop/phd/code/alley/out/BNs/loglik.net", fitted)
plot(structure)



structure <- hc(d, score="aic")
fitted = bn.fit(structure, d, method = "mle")
write.net(file="~/Desktop/phd/code/alley/out/BNs/aic.net", fitted)
plot(structure)

structure <- hc(d, score="bdj")
fitted = bn.fit(structure, d, method = "mle")
write.net(file="~/Desktop/phd/code/alley/out/BNs/bdj.net", fitted)
plot(structure)

structure <- hc(d, score="pred-loglik")
fitted = bn.fit(structure, d, method = "mle")
write.net(file="~/Desktop/phd/code/alley/out/BNs/predloglik.net", fitted)
plot(structure)

structure <- hc(d, score="bde")
fitted = bn.fit(structure, d, method = "mle")
write.net(file="~/Desktop/phd/code/alley/out/BNs/bde.net", fitted)
plot(structure)

structure <- hc(d, score="bds")
fitted = bn.fit(structure, d, method = "mle")
write.net(file="~/Desktop/phd/code/alley/out/BNs/bds.net", fitted)
plot(structure)

structure <- hc(d, score="mbde")
fitted = bn.fit(structure, d, method = "mle")
write.net(file="~/Desktop/phd/code/alley/out/BNs/mbde.net", fitted)
plot(structure)

structure <- hc(d, score="bdla")
fitted = bn.fit(structure, d, method = "mle")
write.net(file="~/Desktop/phd/code/tortLaw/automaticBNs/bdla.net", fitted)
plot(structure)

structure <- hc(d, score="k2")
fitted = bn.fit(structure, d, method = "mle")
write.net(file="~/Desktop/phd/code/tortLaw/automaticBNs/k2.net", fitted)
plot(structure)

structure <- hc(d, score="fnml")
fitted = bn.fit(structure, d, method = "mle")
write.net(file="~/Desktop/phd/code/tortLaw/automaticBNs/fnml.net", fitted)
plot(structure)

structure <- hc(d, score="qnml")
fitted = bn.fit(structure, d, method = "mle")
write.net(file="~/Desktop/phd/code/tortLaw/automaticBNs/qnml.net", fitted)
plot(structure)

