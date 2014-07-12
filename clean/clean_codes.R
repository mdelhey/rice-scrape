library(stringr)

f_in <- "raw/codes.pdf"
f_out_csv <- "data/codes.csv"
f_in_txt <- str_replace(f_in, ".pdf", ".txt")

project_dir <- "/Users/mdelhey/rice-scrape"
setwd(project_dir)

# Call 'pdftotext'
system(sprintf("pdftotext -table %s", f_in))

# read output
txt <- readLines(f_in_txt, warn = FALSE)

# match 3-letter abbrev.
abbr <- unlist(str_match(str_match(txt, "[A-Z]{3}\\s"), "[A-Z]{3}"))

# remove OTR (other)
OTR <- str_match(abbr, "OTR")
abbr[which(!is.na(OTR))] <- NA

# Remove NA codes
codes <- as.vector(abbr)
data <- txt[which(!is.na(codes))]

# Split columns by 3 spaces
split <- str_split(data, "  ")
subs <- lapply(split, function(x) head(x[x != ""], 3))

# Rbind using lapply (introduce NA's)
df <- data.frame(code=NA, name=NA, ref=NA)
df_na <- lapply(subs, function(x) rbind(x, df))

# Combine, remove NA-induced rows
tmp <- do.call("rbind", df_na)
df_out <- tmp[!is.na(tmp$code), ]

# manual fixes
df_out$ref <- as.numeric(df_out$ref)
df_out <- df_out[!is.na(df_out$ref), ]

# Trim whitespace from names
df_out$name <- str_trim(df_out$name)

# save as csv
write.table(df_out, f_out_csv, row.names = FALSE, col.names = FALSE, sep = ",")

# write to db
library(RPostgreSQL)
con <- dbConnect(PostgreSQL(), dbname = "ricedb")
dbWriteTable(con, "t_building_codes", df_out, append = FALSE, overwrite = TRUE)
dbDisconnect(con)
