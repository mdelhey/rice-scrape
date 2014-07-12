library(RPostgreSQL)
library(lubridate)
library(stringr)

dbuser <- "mdelhey"
dbname <- "ricedb"
dbhost <- "localhost"

project_dir <- "/Users/mdelhey/rice-scrape/"
setwd(project_dir)

# Query
rdb.con <- dbConnect(PostgreSQL(), host = dbhost, user = dbuser, dbname = dbname)
tbl.raw <- dbGetQuery(rdb.con, "select * from t_courses_raw")
tbl <- tbl.raw


### CRN  -----------------------------------------------------------------------
tbl$crn <- as.integer(tbl.raw$crn)

### Enrolled  ------------------------------------------------------------------
tbl$enrolled <- as.numeric(str_match(str_match(tbl.raw$enrolled, "Enrolled: [0-9]+"), "[0-9]+"))
tbl$enrolled_max <- as.numeric(str_match(str_match(tbl.raw$enrolled, "Max [0-9]+"), "[0-9]+"))
tbl$enrolled_pr <- ifelse(str_detect(tbl.raw$enrolled, "Permission Required"), TRUE, FALSE)

### Faculty  -------------------------------------------------------------------
# Remove leading "Faculty :"
faculty <- str_replace(str_replace(tbl.raw$faculty, "Faculty: ", ""), "Faculty:", "")

# Watch out for more than 1 faculty (current just take first)
faculties <- str_split(faculty, "; ")
faculties_list <- ifelse(faculties == "", NA, faculties)
tbl$faculty <- as.vector(do.call("rbind", lapply(faculties_list, function(l) l[1])))
tbl$faculty_num <- unlist(lapply(faculties_list, length))

### Title  ---------------------------------------------------------------------
tbl$department <- str_match(tbl.raw$course, "[A-Z]{4}")

### Course  --------------------------------------------------------------------
course_section <- str_match_all(tbl.raw$course, "[0-9]{3}")

# Find broken index
bad_section_idx <- which(do.call("rbind", lapply(course_section, function(l) dim(l)[1] )) != 2)

# Get broken section values
bad_section <- as.vector(do.call("rbind", lapply(str_match_all(tbl.raw$course[bad_section_idx], "[A-Z0-9]{3}"), function(l) l[3,1])))

# Fix by taking last num and append 00. E.g. AW2 ---> 002
bad_section_cln <- as.vector(do.call("rbind", lapply(str_match_all(bad_section, "[A-Z0-9]{1}"), function(l) paste0("00", l[3,1]))))
names(bad_section_cln) <- bad_section_idx

# Paste back using idx
course_section[bad_section_idx] <- lapply(bad_section_idx, function(idx) tmp <- rbind(course_section[[idx]], bad_section_cln[paste(idx)]) )

# Write columns
tbl$course_number <- as.vector(do.call("rbind", lapply(course_section, function(l) l[1,1])))
tbl$course_section <- as.vector(do.call("rbind", lapply(course_section, function(l) l[2,1])))

# Course level
tbl$course_level <- ifelse(as.numeric(tbl$course_number) >= 500, "Grad", "Undergrad")

### Meeting  -------------------------------------------------------------------
# Just take first meeting
meeting <- str_replace(tbl.raw$meeting, "Meeting: ", "")
meetings <- str_split(meeting, "; ")

tbl$meeting <- as.vector(do.call("rbind", lapply(meetings, function(l) l[1])))
tbl$meeting_num <- unlist(lapply(meetings, length))

# Meeting times (NA = no meeting time set)
meeting_times <- str_match_all(tbl$meeting, "[0-9]{2}:[0-9]{2}[[APM]{2}")
meeting_start <- as.vector(do.call("rbind", lapply(meeting_times, function(l) if (is.null(dim(l))) { NA } else { l[1,1] })))
meeting_end <- as.vector(do.call("rbind", lapply(meeting_times, function(l) if (is.null(dim(l))) { NA } else { l[2,1] })))

tbl$meeting_diff <- as.numeric(strptime(meeting_end, format = "%I:%M%p") - strptime(meeting_start, format = "%I:%M%p"))

# Insert into db
dbWriteTable(rdb.con, "t_courses", tbl, row.names = FALSE, overwrite = TRUE)

# Disconnect
dbDisconnect(rdb.con)
